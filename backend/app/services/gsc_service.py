from __future__ import annotations

import json
from datetime import date
from typing import Optional

from google.oauth2 import service_account
from googleapiclient.discovery import build
from sqlalchemy.orm import Session

from app.config import get_settings
from app import models


_GSC_SCOPE = "https://www.googleapis.com/auth/webmasters.readonly"


def _build_credentials():
    settings = get_settings()

    if settings.google_service_account_json:
        info = json.loads(settings.google_service_account_json)
        return service_account.Credentials.from_service_account_info(
            info, scopes=[_GSC_SCOPE]
        )

    if settings.google_application_credentials:
        return service_account.Credentials.from_service_account_file(
            settings.google_application_credentials, scopes=[_GSC_SCOPE]
        )

    raise RuntimeError(
        "Google Service Account 未配置，请设置 GOOGLE_SERVICE_ACCOUNT_JSON 或 GOOGLE_APPLICATION_CREDENTIALS"
    )


def _build_service():
    creds = _build_credentials()
    # Search Console API 的服务名为 webmasters，版本 v3
    return build("webmasters", "v3", credentials=creds, cache_discovery=False)


def fetch_gsc_daily_summary(
    site_url: str,
    target_date: date,
) -> dict[str, Optional[float]]:
    """
    使用 Search Console API 获取某日的站点级别汇总指标。
    对应 gsc_daily 表字段。
    """
    service = _build_service()
    date_str = target_date.strftime("%Y-%m-%d")

    request = {
        "startDate": date_str,
        "endDate": date_str,
        "dimensions": [],  # 仅日汇总
        "rowLimit": 1,
    }

    response = (
        service.searchanalytics()
        .query(siteUrl=site_url, body=request)
        .execute()
    )

    rows = response.get("rows", [])
    if not rows:
        return {}

    row = rows[0]
    clicks = float(row.get("clicks", 0.0))
    impressions = float(row.get("impressions", 0.0))
    ctr = float(row.get("ctr", 0.0))
    position = float(row.get("position", 0.0))

    return {
        "impressions": int(impressions),
        "clicks": int(clicks),
        "ctr": ctr,
        "avg_position": position,
    }


def ingest_gsc_daily_for_project(
    db: Session,
    project: models.Project,
    target_date: date,
) -> models.GscDaily:
    """
    针对单个 project + 日期，从 GSC 拉取数据并写入 / 更新 gsc_daily。
    """
    if not project.gsc_property:
        raise ValueError(f"Project {project.project_key} 未配置 gsc_property")

    metrics = fetch_gsc_daily_summary(project.gsc_property, target_date)
    if not metrics:
        raise ValueError(f"GSC 无 {target_date} 数据")

    existing: Optional[models.GscDaily] = (
        db.query(models.GscDaily)
        .filter(
            models.GscDaily.project_id == project.id,
            models.GscDaily.date == target_date,
        )
        .first()
    )

    if existing:
        for key, value in metrics.items():
            setattr(existing, key, value)
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing

    record = models.GscDaily(
        project_id=project.id,
        date=target_date,
        **metrics,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def fetch_gsc_query_daily(
    site_url: str,
    target_date: date,
) -> list[dict[str, Optional[float]]]:
    """
    使用 Search Console API 获取某日的关键词维度数据。
    对应 gsc_query_daily 表字段。
    """
    service = _build_service()
    date_str = target_date.strftime("%Y-%m-%d")

    request = {
        "startDate": date_str,
        "endDate": date_str,
        "dimensions": ["query"],
        "rowLimit": 25000,
    }

    response = (
        service.searchanalytics()
        .query(siteUrl=site_url, body=request)
        .execute()
    )

    rows = response.get("rows", [])
    results: list[dict[str, Optional[float]]] = []

    for row in rows:
        keys = row.get("keys", [])
        query = keys[0] if keys else "(not set)"
        clicks = float(row.get("clicks", 0.0))
        impressions = float(row.get("impressions", 0.0))
        ctr = float(row.get("ctr", 0.0))
        position = float(row.get("position", 0.0))

        results.append(
            {
                "query": query,
                "clicks": clicks,
                "impressions": impressions,
                "ctr": ctr,
                "avg_position": position,
            }
        )

    return results


def ingest_gsc_query_daily_for_project(
    db: Session,
    project: models.Project,
    target_date: date,
) -> int:
    """
    针对单个 project + 日期，从 GSC 拉取关键词维度数据并写入 / 更新 gsc_query_daily。
    """
    if not project.gsc_property:
        raise ValueError(f"Project {project.project_key} 未配置 gsc_property")

    rows = fetch_gsc_query_daily(project.gsc_property, target_date)
    if not rows:
        return 0

    count = 0
    for item in rows:
        query = str(item["query"])
        existing: Optional[models.GscQueryDaily] = (
            db.query(models.GscQueryDaily)
            .filter(
                models.GscQueryDaily.project_id == project.id,
                models.GscQueryDaily.date == target_date,
                models.GscQueryDaily.query == query,
            )
            .first()
        )

        payload = {
            "clicks": int(item["clicks"] or 0),
            "impressions": int(item["impressions"] or 0),
            "ctr": float(item["ctr"] or 0.0),
            "avg_position": float(item["avg_position"] or 0.0),
        }

        if existing:
            for key, value in payload.items():
                setattr(existing, key, value)
            db.add(existing)
        else:
            record = models.GscQueryDaily(
                project_id=project.id,
                date=target_date,
                query=query,
                **payload,
            )
            db.add(record)

        count += 1

    db.commit()
    return count


def fetch_gsc_page_daily(
    site_url: str,
    target_date: date,
) -> list[dict[str, Optional[float]]]:
    """
    使用 Search Console API 获取某日的页面维度数据。
    对应 gsc_page_daily 表字段。
    """
    service = _build_service()
    date_str = target_date.strftime("%Y-%m-%d")

    request = {
        "startDate": date_str,
        "endDate": date_str,
        "dimensions": ["page"],
        "rowLimit": 25000,
    }

    response = (
        service.searchanalytics()
        .query(siteUrl=site_url, body=request)
        .execute()
    )

    rows = response.get("rows", [])
    results: list[dict[str, Optional[float]]] = []

    for row in rows:
        keys = row.get("keys", [])
        page = keys[0] if keys else "(not set)"
        clicks = float(row.get("clicks", 0.0))
        impressions = float(row.get("impressions", 0.0))
        ctr = float(row.get("ctr", 0.0))
        position = float(row.get("position", 0.0))

        results.append(
            {
                "page": page,
                "clicks": clicks,
                "impressions": impressions,
                "ctr": ctr,
                "avg_position": position,
            }
        )

    return results


def ingest_gsc_page_daily_for_project(
    db: Session,
    project: models.Project,
    target_date: date,
) -> int:
    """
    针对单个 project + 日期，从 GSC 拉取页面维度数据并写入 / 更新 gsc_page_daily。
    """
    if not project.gsc_property:
        raise ValueError(f"Project {project.project_key} 未配置 gsc_property")

    rows = fetch_gsc_page_daily(project.gsc_property, target_date)
    if not rows:
        return 0

    count = 0
    for item in rows:
        page = str(item["page"])
        existing: Optional[models.GscPageDaily] = (
            db.query(models.GscPageDaily)
            .filter(
                models.GscPageDaily.project_id == project.id,
                models.GscPageDaily.date == target_date,
                models.GscPageDaily.page == page,
            )
            .first()
        )

        payload = {
            "clicks": int(item["clicks"] or 0),
            "impressions": int(item["impressions"] or 0),
            "ctr": float(item["ctr"] or 0.0),
            "avg_position": float(item["avg_position"] or 0.0),
        }

        if existing:
            for key, value in payload.items():
                setattr(existing, key, value)
            db.add(existing)
        else:
            record = models.GscPageDaily(
                project_id=project.id,
                date=target_date,
                page=page,
                **payload,
            )
            db.add(record)

        count += 1

    db.commit()
    return count


