from __future__ import annotations

import json
from datetime import date
from typing import Optional

from google.analytics.data_v1beta import (  # type: ignore
    BetaAnalyticsDataClient,
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)
from google.oauth2 import service_account
from sqlalchemy.orm import Session

from app.config import get_settings
from app import models


_GA4_SCOPE = "https://www.googleapis.com/auth/analytics.readonly"


def _build_credentials():
    settings = get_settings()

    if settings.google_service_account_json:
        info = json.loads(settings.google_service_account_json)
        return service_account.Credentials.from_service_account_info(
            info, scopes=[_GA4_SCOPE]
        )

    if settings.google_application_credentials:
        return service_account.Credentials.from_service_account_file(
            settings.google_application_credentials, scopes=[_GA4_SCOPE]
        )

    raise RuntimeError(
        "Google Service Account 未配置，请设置 GOOGLE_SERVICE_ACCOUNT_JSON 或 GOOGLE_APPLICATION_CREDENTIALS"
    )


def _build_client() -> BetaAnalyticsDataClient:
    credentials = _build_credentials()
    return BetaAnalyticsDataClient(credentials=credentials)


def fetch_ga4_daily_metrics(
    property_id: str,
    target_date: date,
) -> dict[str, Optional[float]]:
    """
    调用 GA4 Data API，获取某天的核心汇总指标。
    返回值字段对应 ga4_daily 表的列。
    """
    client = _build_client()

    date_str = target_date.strftime("%Y-%m-%d")

    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=date_str, end_date=date_str)],
        metrics=[
            Metric(name="activeUsers"),
            Metric(name="sessions"),
            Metric(name="screenPageViews"),
            Metric(name="averageSessionDuration"),
            Metric(name="engagementRate"),
            Metric(name="bounceRate"),
        ],
    )

    response = client.run_report(request)
    if not response.rows:
        return {}

    values = [float(v.value) if v.value else 0.0 for v in response.rows[0].metric_values]

    return {
        "dau": int(values[0]),
        "sessions": int(values[1]),
        "page_views": int(values[2]),
        "avg_engagement_time": values[3],
        "engagement_rate": values[4],
        "bounce_rate": values[5],
    }


def ingest_ga4_daily_for_project(
    db: Session,
    project: models.Project,
    target_date: date,
) -> models.Ga4Daily:
    """
    针对单个 project + 日期，从 GA4 拉取数据并写入 / 更新 ga4_daily。
    """
    if not project.ga4_property_id:
        raise ValueError(f"Project {project.project_key} 未配置 ga4_property_id")

    metrics = fetch_ga4_daily_metrics(project.ga4_property_id, target_date)
    if not metrics:
        # 当天无数据，直接返回或可选择写入 0 值
        raise ValueError(f"GA4 无 {target_date} 数据")

    existing: Optional[models.Ga4Daily] = (
        db.query(models.Ga4Daily)
        .filter(
            models.Ga4Daily.project_id == project.id,
            models.Ga4Daily.date == target_date,
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

    record = models.Ga4Daily(
        project_id=project.id,
        date=target_date,
        **metrics,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def fetch_ga4_channel_daily(
    property_id: str,
    target_date: date,
) -> list[dict[str, Optional[float]]]:
    """
    获取按渠道（channel）维度的 GA4 指标，用于填充 ga4_channel_daily。
    维度：sessionDefaultChannelGroup
    指标：sessions、totalUsers、screenPageViews
    """
    client = _build_client()
    date_str = target_date.strftime("%Y-%m-%d")

    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=date_str, end_date=date_str)],
        dimensions=[Dimension(name="sessionDefaultChannelGroup")],
        metrics=[
            Metric(name="sessions"),
            Metric(name="totalUsers"),
            Metric(name="screenPageViews"),
        ],
    )

    response = client.run_report(request)
    results: list[dict[str, Optional[float]]] = []

    for row in response.rows:
        channel = row.dimension_values[0].value or "Other"
        sessions = float(row.metric_values[0].value or 0.0)
        users = float(row.metric_values[1].value or 0.0)
        page_views = float(row.metric_values[2].value or 0.0)

        results.append(
            {
                "channel": channel,
                "sessions": sessions,
                "users": users,
                "page_views": page_views,
            }
        )

    return results


def ingest_ga4_channel_daily_for_project(
    db: Session,
    project: models.Project,
    target_date: date,
) -> int:
    """
    填充指定 project + 日期的 ga4_channel_daily。
    返回写入/更新的记录数量。
    """
    if not project.ga4_property_id:
        raise ValueError(f"Project {project.project_key} 未配置 ga4_property_id")

    rows = fetch_ga4_channel_daily(project.ga4_property_id, target_date)
    if not rows:
        return 0

    count = 0
    for item in rows:
        channel = str(item["channel"])
        existing: Optional[models.Ga4ChannelDaily] = (
            db.query(models.Ga4ChannelDaily)
            .filter(
                models.Ga4ChannelDaily.project_id == project.id,
                models.Ga4ChannelDaily.date == target_date,
                models.Ga4ChannelDaily.channel == channel,
            )
            .first()
        )

        payload = {
            "sessions": int(item["sessions"] or 0),
            "users": int(item["users"] or 0),
            "page_views": int(item["page_views"] or 0),
        }

        if existing:
            for key, value in payload.items():
                setattr(existing, key, value)
            db.add(existing)
        else:
            record = models.Ga4ChannelDaily(
                project_id=project.id,
                date=target_date,
                channel=channel,
                **payload,
            )
            db.add(record)

        count += 1

    db.commit()
    return count


def fetch_ga4_page_daily(
    property_id: str,
    target_date: date,
) -> list[dict[str, Optional[float]]]:
    """
    获取按页面（pagePath）维度的 GA4 指标，用于填充 ga4_page_daily。
    指标：pageViews、averageSessionDuration、bounceRate。
    """
    client = _build_client()
    date_str = target_date.strftime("%Y-%m-%d")

    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=date_str, end_date=date_str)],
        dimensions=[Dimension(name="pagePath")],
        metrics=[
            Metric(name="screenPageViews"),
            Metric(name="averageSessionDuration"),
            Metric(name="bounceRate"),
        ],
    )

    response = client.run_report(request)

    # 用规范化的 page_path（例如转小写）聚合，防止 API 返回大小写差异等导致唯一键冲突。
    aggregated: dict[str, dict[str, float]] = {}

    for row in response.rows:
        raw_path = row.dimension_values[0].value or "(not set)"
        norm_key = raw_path.lower()
        pv = float(row.metric_values[0].value or 0.0)
        avg_time = float(row.metric_values[1].value or 0.0)
        bounce_rate = float(row.metric_values[2].value or 0.0)

        if norm_key not in aggregated:
            aggregated[norm_key] = {
                "page_path": raw_path,
                "page_views": pv,
                "avg_engagement_time": avg_time,
                "bounce_rate": bounce_rate,
            }
        else:
            prev = aggregated[norm_key]
            prev_pv = prev["page_views"]
            # 加权平均更新
            total_pv = prev_pv + pv if prev_pv + pv > 0 else 0.0
            if total_pv > 0:
                prev["avg_engagement_time"] = (
                    prev["avg_engagement_time"] * prev_pv + avg_time * pv
                ) / total_pv
                prev["bounce_rate"] = (
                    prev["bounce_rate"] * prev_pv + bounce_rate * pv
                ) / total_pv
            prev["page_views"] = total_pv

    results: list[dict[str, Optional[float]]] = []
    for _, vals in aggregated.items():
        results.append(
            {
                "page_path": vals["page_path"],
                "page_views": vals["page_views"],
                "avg_engagement_time": vals["avg_engagement_time"],
                "bounce_rate": vals["bounce_rate"],
            }
        )

    return results


def ingest_ga4_page_daily_for_project(
    db: Session,
    project: models.Project,
    target_date: date,
) -> int:
    """
    填充指定 project + 日期的 ga4_page_daily。
    返回写入/更新的记录数量。
    """
    if not project.ga4_property_id:
        raise ValueError(f"Project {project.project_key} 未配置 ga4_property_id")

    rows = fetch_ga4_page_daily(project.ga4_property_id, target_date)

    # 为保证幂等性，先清空该 project + date 的旧数据，再写入新结果，避免唯一键冲突。
    (
        db.query(models.Ga4PageDaily)
        .filter(
            models.Ga4PageDaily.project_id == project.id,
            models.Ga4PageDaily.date == target_date,
        )
        .delete(synchronize_session=False)
    )

    if not rows:
        db.commit()
        return 0

    for item in rows:
        page_path = str(item["page_path"])

        record = models.Ga4PageDaily(
            project_id=project.id,
            date=target_date,
            page_path=page_path,
            page_views=int(item["page_views"] or 0),
            avg_engagement_time=float(item["avg_engagement_time"] or 0.0),
            bounce_rate=float(item["bounce_rate"] or 0.0),
        )
        db.add(record)

    db.commit()
    return len(rows)


