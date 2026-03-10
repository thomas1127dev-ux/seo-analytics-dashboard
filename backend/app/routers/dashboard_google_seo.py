from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db import get_db
from app import models, schemas


router = APIRouter(prefix="/api/dashboard/google-seo", tags=["dashboard-google-seo"])


def _ensure_project(db: Session, project_id: int) -> None:
    exists = (
        db.query(models.Project.id)
        .filter(models.Project.id == project_id, models.Project.status == "active")
        .first()
    )
    if not exists:
        raise HTTPException(status_code=404, detail="project 不存在或已停用")


@router.get("/summary", response_model=schemas.SearchOverviewMetrics)
def get_google_seo_summary(
    project_id: int = Query(..., description="项目 ID"),
    start_date: date = Query(..., description="开始日期"),
    end_date: date = Query(..., description="结束日期"),
    db: Session = Depends(get_db),
):
    """
    Google SEO 汇总指标（展示、点击、CTR、平均排名 + 趋势）。
    复用与总览页相同的 SearchOverviewMetrics 结构。
    """
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date 不能晚于 end_date")

    _ensure_project(db, project_id)

    rows = (
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
def get_google_seo_queries(
    project_id: int = Query(..., description="项目 ID"),
    start_date: date = Query(..., description="开始日期"),
    end_date: date = Query(..., description="结束日期"),
    limit: int = Query(100, ge=1, le=500, description="返回 Top N 关键词"),
    db: Session = Depends(get_db),
):
    """
    Google SEO 关键词排行。
    """
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date 不能晚于 end_date")

    _ensure_project(db, project_id)

    rows = (
        db.query(
            models.GscQueryDaily.query,
            func.coalesce(func.sum(models.GscQueryDaily.clicks), 0).label("clicks"),
            func.coalesce(
                func.sum(models.GscQueryDaily.impressions), 0
            ).label("impressions"),
            func.coalesce(func.avg(models.GscQueryDaily.ctr), 0).label("ctr"),
            func.coalesce(
                func.avg(models.GscQueryDaily.avg_position), 0
            ).label("avg_position"),
        )
        .filter(
            models.GscQueryDaily.project_id == project_id,
            models.GscQueryDaily.date >= start_date,
            models.GscQueryDaily.date <= end_date,
        )
        .group_by(models.GscQueryDaily.query)
        .order_by(func.sum(models.GscQueryDaily.clicks).desc())
        .limit(limit)
        .all()
    )

    items = [
        schemas.SeoItem(
            key=r.query,
            clicks=float(r.clicks),
            impressions=float(r.impressions),
            ctr=float(r.ctr),
            avg_position=float(r.avg_position),
        )
        for r in rows
    ]

    return schemas.SeoListResponse(
        project_id=project_id,
        start_date=start_date,
        end_date=end_date,
        items=items,
    )


@router.get("/pages", response_model=schemas.SeoListResponse)
def get_google_seo_pages(
    project_id: int = Query(..., description="项目 ID"),
    start_date: date = Query(..., description="开始日期"),
    end_date: date = Query(..., description="结束日期"),
    limit: int = Query(100, ge=1, le=500, description="返回 Top N 页面"),
    db: Session = Depends(get_db),
):
    """
    Google SEO 页面排行。
    """
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date 不能晚于 end_date")

    _ensure_project(db, project_id)

    rows = (
        db.query(
            models.GscPageDaily.page,
            func.coalesce(func.sum(models.GscPageDaily.clicks), 0).label("clicks"),
            func.coalesce(
                func.sum(models.GscPageDaily.impressions), 0
            ).label("impressions"),
            func.coalesce(func.avg(models.GscPageDaily.ctr), 0).label("ctr"),
            func.coalesce(
                func.avg(models.GscPageDaily.avg_position), 0
            ).label("avg_position"),
        )
        .filter(
            models.GscPageDaily.project_id == project_id,
            models.GscPageDaily.date >= start_date,
            models.GscPageDaily.date <= end_date,
        )
        .group_by(models.GscPageDaily.page)
        .order_by(func.sum(models.GscPageDaily.clicks).desc())
        .limit(limit)
        .all()
    )

    items = [
        schemas.SeoItem(
            key=r.page,
            clicks=float(r.clicks),
            impressions=float(r.impressions),
            ctr=float(r.ctr),
            avg_position=float(r.avg_position),
        )
        for r in rows
    ]

    return schemas.SeoListResponse(
        project_id=project_id,
        start_date=start_date,
        end_date=end_date,
        items=items,
    )

