from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app import models
from app.services.ga4_service import (
    ingest_ga4_daily_for_project,
    ingest_ga4_channel_daily_for_project,
    ingest_ga4_page_daily_for_project,
)
from app.services.gsc_service import (
    ingest_gsc_daily_for_project,
    ingest_gsc_query_daily_for_project,
    ingest_gsc_page_daily_for_project,
)
from app.services.yandex_service import (
    ingest_yandex_daily_for_project,
    ingest_yandex_query_daily_for_project,
)


router = APIRouter(prefix="/api/admin/ingest", tags=["admin-ingest"])


@router.post("/ga4-daily")
def ingest_ga4_daily(
    project_key: str = Query(..., description="项目唯一 key，对应 projects.project_key"),
    target_date: date = Query(..., description="拉取数据的日期，例如 2026-03-10"),
    db: Session = Depends(get_db),
):
    """
    无权限版：手动触发某个项目在指定日期的 GA4 日汇总数据采集。
    后续可替换为定时任务或批量任务入口。
    """
    project = (
        db.query(models.Project)
        .filter(models.Project.project_key == project_key)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="project 不存在")

    try:
        record = ingest_ga4_daily_for_project(db, project, target_date)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "project_key": project.project_key,
        "date": str(target_date),
        "data": {
            "dau": record.dau,
            "sessions": record.sessions,
            "page_views": record.page_views,
            "avg_engagement_time": record.avg_engagement_time,
            "engagement_rate": record.engagement_rate,
            "bounce_rate": record.bounce_rate,
        },
    }


@router.post("/gsc-daily")
def ingest_gsc_daily(
    project_key: str = Query(..., description="项目唯一 key，对应 projects.project_key"),
    target_date: date = Query(..., description="拉取数据的日期，例如 2026-03-10"),
    db: Session = Depends(get_db),
):
    """
    无权限版：手动触发某个项目在指定日期的 GSC 日汇总数据采集。
    """
    project = (
        db.query(models.Project)
        .filter(models.Project.project_key == project_key)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="project 不存在")

    try:
        record = ingest_gsc_daily_for_project(db, project, target_date)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "project_key": project.project_key,
        "date": str(target_date),
        "data": {
            "impressions": record.impressions,
            "clicks": record.clicks,
            "ctr": record.ctr,
            "avg_position": record.avg_position,
        },
    }


@router.post("/ga4-channel-daily")
def ingest_ga4_channel_daily(
    project_key: str = Query(..., description="项目唯一 key，对应 projects.project_key"),
    target_date: date = Query(..., description="拉取数据的日期，例如 2026-03-10"),
    db: Session = Depends(get_db),
):
    """
    无权限版：采集 GA4 渠道维度数据并写入 ga4_channel_daily。
    """
    project = (
        db.query(models.Project)
        .filter(models.Project.project_key == project_key)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="project 不存在")

    try:
        count = ingest_ga4_channel_daily_for_project(db, project, target_date)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "project_key": project.project_key,
        "date": str(target_date),
        "rows_affected": count,
    }


@router.post("/ga4-page-daily")
def ingest_ga4_page_daily(
    project_key: str = Query(..., description="项目唯一 key，对应 projects.project_key"),
    target_date: date = Query(..., description="拉取数据的日期，例如 2026-03-10"),
    db: Session = Depends(get_db),
):
    """
    无权限版：采集 GA4 页面维度数据并写入 ga4_page_daily。
    """
    project = (
        db.query(models.Project)
        .filter(models.Project.project_key == project_key)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="project 不存在")

    try:
        count = ingest_ga4_page_daily_for_project(db, project, target_date)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "project_key": project.project_key,
        "date": str(target_date),
        "rows_affected": count,
    }


@router.post("/gsc-query-daily")
def ingest_gsc_query_daily(
    project_key: str = Query(..., description="项目唯一 key，对应 projects.project_key"),
    target_date: date = Query(..., description="拉取数据的日期，例如 2026-03-10"),
    db: Session = Depends(get_db),
):
    """
    无权限版：采集 GSC 关键词维度数据并写入 gsc_query_daily。
    """
    project = (
        db.query(models.Project)
        .filter(models.Project.project_key == project_key)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="project 不存在")

    try:
        count = ingest_gsc_query_daily_for_project(db, project, target_date)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "project_key": project.project_key,
        "date": str(target_date),
        "rows_affected": count,
    }


@router.post("/gsc-page-daily")
def ingest_gsc_page_daily(
    project_key: str = Query(..., description="项目唯一 key，对应 projects.project_key"),
    target_date: date = Query(..., description="拉取数据的日期，例如 2026-03-10"),
    db: Session = Depends(get_db),
):
    """
    无权限版：采集 GSC 页面维度数据并写入 gsc_page_daily。
    """
    project = (
        db.query(models.Project)
        .filter(models.Project.project_key == project_key)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="project 不存在")

    try:
        count = ingest_gsc_page_daily_for_project(db, project, target_date)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "project_key": project.project_key,
        "date": str(target_date),
        "rows_affected": count,
    }


@router.post("/yandex-daily")
def ingest_yandex_daily(
    project_key: str = Query(..., description="项目唯一 key，对应 projects.project_key"),
    target_date: date = Query(..., description="拉取数据的日期，例如 2026-03-10"),
    db: Session = Depends(get_db),
):
    """
    无权限版：手动触发某个项目在指定日期的 Yandex 日汇总数据采集。
    若 Yandex 未配置或返回 RESOURCE_NOT_FOUND，则安全返回无数据说明。
    """
    project = (
        db.query(models.Project)
        .filter(models.Project.project_key == project_key)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="project 不存在")

    record = ingest_yandex_daily_for_project(db, project, target_date)
    if record is None:
        # 按需求：RESOURCE_NOT_FOUND 等情况安全忽略，不视为错误
        return {
            "project_key": project.project_key,
            "date": str(target_date),
            "data": None,
            "message": "Yandex 暂无可用数据或尚未配置，将安全忽略",
        }

    return {
        "project_key": project.project_key,
        "date": str(target_date),
        "data": {
            "impressions": record.impressions,
            "clicks": record.clicks,
            "ctr": record.ctr,
            "avg_position": record.avg_position,
        },
    }


@router.post("/yandex-query-daily")
def ingest_yandex_query_daily(
    project_key: str = Query(..., description="项目唯一 key，对应 projects.project_key"),
    target_date: date = Query(..., description="拉取数据的日期，例如 2026-03-10"),
    db: Session = Depends(get_db),
):
    """
    无权限版：采集 Yandex 查询词维度数据并写入 yandex_query_daily。
    当前实现为占位逻辑，需要在明确 Yandex API 后补齐。
    """
    project = (
        db.query(models.Project)
        .filter(models.Project.project_key == project_key)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="project 不存在")

    count = ingest_yandex_query_daily_for_project(db, project, target_date)

    return {
        "project_key": project.project_key,
        "date": str(target_date),
        "rows_affected": count,
    }


