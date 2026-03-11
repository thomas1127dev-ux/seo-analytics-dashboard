from __future__ import annotations

from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db import get_db
from app import models, schemas
from app.auth.dependencies import ensure_project_access


router = APIRouter(prefix="/api/dashboard", tags=["dashboard-overview"])


def _build_metric_with_trend(
    rows: list[tuple[date, float]], start_date: date, end_date: date
) -> schemas.MetricWithTrend:
    # 将查询结果映射为字典，便于按日期查找
    value_by_date = {d: v for d, v in rows}

    trend_points: list[schemas.DailyPoint] = []
    cursor = start_date
    while cursor <= end_date:
        trend_points.append(
            schemas.DailyPoint(date=cursor, value=value_by_date.get(cursor))
        )
        cursor += timedelta(days=1)

    current_value = value_by_date.get(end_date)
    yesterday = end_date - timedelta(days=1)
    yesterday_value = value_by_date.get(yesterday)

    return schemas.MetricWithTrend(
        current=current_value,
        yesterday=yesterday_value,
        trend_7d=trend_points,
    )


@router.get("/overview", response_model=schemas.OverviewResponse)
def get_overview(
    project_id: int = Query(..., description="项目 ID"),
    start_date: date = Query(..., description="开始日期"),
    end_date: date = Query(..., description="结束日期"),
    db: Session = Depends(get_db),
    project: models.Project = Depends(ensure_project_access),
):
    """
    总览页聚合接口。
    - 返回 GA4 / GSC / Yandex 的汇总指标 + 7 天趋势 + 与昨日对比。
    - 仅按 project_id 过滤，不做用户权限校验。
    """
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date 不能晚于 end_date")

    # GA4
    ga4_rows = (
        db.query(
            models.Ga4Daily.date,
            func.coalesce(models.Ga4Daily.dau, 0).label("dau"),
            func.coalesce(models.Ga4Daily.sessions, 0).label("sessions"),
            func.coalesce(models.Ga4Daily.page_views, 0).label("page_views"),
            models.Ga4Daily.avg_engagement_time,
            models.Ga4Daily.engagement_rate,
            models.Ga4Daily.bounce_rate,
        )
        .filter(
            models.Ga4Daily.project_id == project_id,
            models.Ga4Daily.date >= start_date,
            models.Ga4Daily.date <= end_date,
        )
        .order_by(models.Ga4Daily.date.asc())
        .all()
    )

    ga4_dau_series = [(r.date, float(r.dau)) for r in ga4_rows]
    ga4_sessions_series = [(r.date, float(r.sessions)) for r in ga4_rows]
    ga4_page_views_series = [(r.date, float(r.page_views)) for r in ga4_rows]
    ga4_avg_time_series = [
        (r.date, float(r.avg_engagement_time) if r.avg_engagement_time is not None else 0.0)
        for r in ga4_rows
    ]
    ga4_engagement_rate_series = [
        (r.date, float(r.engagement_rate) if r.engagement_rate is not None else 0.0)
        for r in ga4_rows
    ]
    ga4_bounce_rate_series = [
        (r.date, float(r.bounce_rate) if r.bounce_rate is not None else 0.0)
        for r in ga4_rows
    ]

    ga4_metrics = schemas.Ga4OverviewMetrics(
        dau=_build_metric_with_trend(ga4_dau_series, start_date, end_date),
        sessions=_build_metric_with_trend(ga4_sessions_series, start_date, end_date),
        page_views=_build_metric_with_trend(ga4_page_views_series, start_date, end_date),
        avg_engagement_time=_build_metric_with_trend(
            ga4_avg_time_series, start_date, end_date
        ),
        engagement_rate=_build_metric_with_trend(
            ga4_engagement_rate_series, start_date, end_date
        ),
        bounce_rate=_build_metric_with_trend(
            ga4_bounce_rate_series, start_date, end_date
        ),
    )

    # GSC
    gsc_rows = (
        db.query(
            models.GscDaily.date,
            func.coalesce(models.GscDaily.impressions, 0).label("impressions"),
            func.coalesce(models.GscDaily.clicks, 0).label("clicks"),
            models.GscDaily.ctr,
            models.GscDaily.avg_position,
        )
        .filter(
            models.GscDaily.project_id == project_id,
            models.GscDaily.date >= start_date,
            models.GscDaily.date <= end_date,
        )
        .order_by(models.GscDaily.date.asc())
        .all()
    )

    gsc_impressions_series = [(r.date, float(r.impressions)) for r in gsc_rows]
    gsc_clicks_series = [(r.date, float(r.clicks)) for r in gsc_rows]
    gsc_ctr_series = [
        (r.date, float(r.ctr) if r.ctr is not None else 0.0) for r in gsc_rows
    ]
    gsc_position_series = [
        (r.date, float(r.avg_position) if r.avg_position is not None else 0.0)
        for r in gsc_rows
    ]

    gsc_metrics = schemas.SearchOverviewMetrics(
        impressions=_build_metric_with_trend(
            gsc_impressions_series, start_date, end_date
        ),
        clicks=_build_metric_with_trend(gsc_clicks_series, start_date, end_date),
        ctr=_build_metric_with_trend(gsc_ctr_series, start_date, end_date),
        avg_position=_build_metric_with_trend(
            gsc_position_series, start_date, end_date
        ),
    )

    # Yandex
    yandex_rows = (
        db.query(
            models.YandexDaily.date,
            func.coalesce(models.YandexDaily.impressions, 0).label("impressions"),
            func.coalesce(models.YandexDaily.clicks, 0).label("clicks"),
            models.YandexDaily.ctr,
            models.YandexDaily.avg_position,
        )
        .filter(
            models.YandexDaily.project_id == project_id,
            models.YandexDaily.date >= start_date,
            models.YandexDaily.date <= end_date,
        )
        .order_by(models.YandexDaily.date.asc())
        .all()
    )

    yandex_impressions_series = [(r.date, float(r.impressions)) for r in yandex_rows]
    yandex_clicks_series = [(r.date, float(r.clicks)) for r in yandex_rows]
    yandex_ctr_series = [
        (r.date, float(r.ctr) if r.ctr is not None else 0.0) for r in yandex_rows
    ]
    yandex_position_series = [
        (r.date, float(r.avg_position) if r.avg_position is not None else 0.0)
        for r in yandex_rows
    ]

    yandex_metrics = schemas.SearchOverviewMetrics(
        impressions=_build_metric_with_trend(
            yandex_impressions_series, start_date, end_date
        ),
        clicks=_build_metric_with_trend(yandex_clicks_series, start_date, end_date),
        ctr=_build_metric_with_trend(yandex_ctr_series, start_date, end_date),
        avg_position=_build_metric_with_trend(
            yandex_position_series, start_date, end_date
        ),
    )

    return schemas.OverviewResponse(
        project_id=project_id,
        start_date=start_date,
        end_date=end_date,
        ga4=ga4_metrics,
        gsc=gsc_metrics,
        yandex=yandex_metrics,
    )

