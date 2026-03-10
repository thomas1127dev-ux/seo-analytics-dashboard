from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app import models
from app.services.ga4_service import ingest_ga4_daily_for_project


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


