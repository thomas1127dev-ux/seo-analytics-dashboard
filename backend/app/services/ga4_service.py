from __future__ import annotations

import json
from datetime import date
from typing import Optional

from google.analytics.data_v1beta import (
    BetaAnalyticsDataClient,
    DateRange,
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


