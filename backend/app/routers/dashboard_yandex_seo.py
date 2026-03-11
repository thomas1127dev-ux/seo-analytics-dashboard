from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db import get_db
from app import models, schemas
from app.auth.dependencies import ensure_project_access


router = APIRouter(prefix="/api/dashboard/yandex-seo", tags=["dashboard-yandex-seo"])


@router.get("/summary", response_model=schemas.SearchOverviewMetrics)
def get_yandex_seo_summary(
    project_id: int = Query(..., description="项目 ID"),
    start_date: date = Query(..., description="开始日期"),
    end_date: date = Query(..., description="结束日期"),
    db: Session = Depends(get_db),
    project: models.Project = Depends(ensure_project_access),
):
    """
    Yandex SEO 汇总指标（展示、点击、CTR、平均排名 + 趋势）。
    结构与 Google SEO 保持一致。
    """
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date 不能晚于 end_date")

    rows = (
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

    from app.routers.dashboard_overview import _build_metric_with_trend

    impressions_series = [(r.date, float(r.impressions)) for r in rows]
    clicks_series = [(r.date, float(r.clicks)) for r in rows]
    ctr_series = [
        (r.date, float(r.ctr) if r.ctr is not None else 0.0) for r in rows
    ]
    position_series = [
        (r.date, float(r.avg_position) if r.avg_position is not None else 0.0)
        for r in rows
    ]

    return schemas.SearchOverviewMetrics(
        impressions=_build_metric_with_trend(
            impressions_series, start_date, end_date
        ),
        clicks=_build_metric_with_trend(clicks_series, start_date, end_date),
        ctr=_build_metric_with_trend(ctr_series, start_date, end_date),
        avg_position=_build_metric_with_trend(position_series, start_date, end_date),
    )


@router.get("/queries", response_model=schemas.SeoListResponse)
def get_yandex_seo_queries(
    project_id: int = Query(..., description="项目 ID"),
    start_date: date = Query(..., description="开始日期"),
    end_date: date = Query(..., description="结束日期"),
    limit: int = Query(100, ge=1, le=500, description="返回 Top N 查询词"),
    db: Session = Depends(get_db),
    project: models.Project = Depends(ensure_project_access),
):
    """
    Yandex SEO 关键词排行（不提供页面维度）。
    """
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date 不能晚于 end_date")

    rows = (
        db.query(
            models.YandexQueryDaily.query,
            func.coalesce(func.sum(models.YandexQueryDaily.clicks), 0).label("clicks"),
            func.coalesce(
                func.sum(models.YandexQueryDaily.impressions), 0
            ).label("impressions"),
            func.coalesce(func.avg(models.YandexQueryDaily.ctr), 0).label("ctr"),
        )
        .filter(
            models.YandexQueryDaily.project_id == project_id,
            models.YandexQueryDaily.date >= start_date,
            models.YandexQueryDaily.date <= end_date,
        )
        .group_by(models.YandexQueryDaily.query)
        .order_by(func.sum(models.YandexQueryDaily.clicks).desc())
        .limit(limit)
        .all()
    )

    items = [
        schemas.SeoItem(
            key=r.query,
            clicks=float(r.clicks),
            impressions=float(r.impressions),
            ctr=float(r.ctr),
            avg_position=0.0,  # Yandex 查询维度可能无平均排名，可视需求调整
        )
        for r in rows
    ]

    return schemas.SeoListResponse(
        project_id=project_id,
        start_date=start_date,
        end_date=end_date,
        items=items,
    )

