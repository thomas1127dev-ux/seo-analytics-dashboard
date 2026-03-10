from __future__ import annotations

from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db import get_db
from app import models, schemas


router = APIRouter(prefix="/api/dashboard", tags=["dashboard-content"])


@router.get("/content", response_model=schemas.ContentPerformanceResponse)
def get_content_performance(
    project_id: int = Query(..., description="项目 ID"),
    start_date: date = Query(..., description="开始日期"),
    end_date: date = Query(..., description="结束日期"),
    limit: int = Query(20, description="返回 Top N 页面", ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    内容表现页接口。
    - 返回 Top N 页面：PV、平均参与时长、跳出率、7 天增长量。
    - 7 天增长量：当前区间总 PV 与前一等长区间总 PV 的差值。
    """
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date 不能晚于 end_date")

    project_exists = (
        db.query(models.Project.id)
        .filter(models.Project.id == project_id, models.Project.status == "active")
        .first()
    )
    if not project_exists:
        raise HTTPException(status_code=404, detail="project 不存在或已停用")

    days = (end_date - start_date).days + 1
    prev_end_date = start_date - timedelta(days=1)
    prev_start_date = prev_end_date - timedelta(days=days - 1)

    # 当前区间汇总
    current_rows = (
        db.query(
            models.Ga4PageDaily.page_path,
            func.coalesce(func.sum(models.Ga4PageDaily.page_views), 0).label(
                "page_views"
            ),
            func.coalesce(func.avg(models.Ga4PageDaily.avg_engagement_time), 0).label(
                "avg_engagement_time"
            ),
            func.coalesce(func.avg(models.Ga4PageDaily.bounce_rate), 0).label(
                "bounce_rate"
            ),
        )
        .filter(
            models.Ga4PageDaily.project_id == project_id,
            models.Ga4PageDaily.date >= start_date,
            models.Ga4PageDaily.date <= end_date,
        )
        .group_by(models.Ga4PageDaily.page_path)
        .order_by(func.sum(models.Ga4PageDaily.page_views).desc())
        .limit(limit)
        .all()
    )

    page_paths = [r.page_path for r in current_rows]

    if not page_paths:
        return schemas.ContentPerformanceResponse(
            project_id=project_id,
            start_date=start_date,
            end_date=end_date,
            pages=[],
        )

    # 前一周期的 PV，用于计算 7 天增长量
    prev_rows = (
        db.query(
            models.Ga4PageDaily.page_path,
            func.coalesce(func.sum(models.Ga4PageDaily.page_views), 0).label(
                "page_views"
            ),
        )
        .filter(
            models.Ga4PageDaily.project_id == project_id,
            models.Ga4PageDaily.date >= prev_start_date,
            models.Ga4PageDaily.date <= prev_end_date,
            models.Ga4PageDaily.page_path.in_(page_paths),
        )
        .group_by(models.Ga4PageDaily.page_path)
        .all()
    )

    prev_map = {r.page_path: float(r.page_views) for r in prev_rows}

    pages: list[schemas.ContentPageItem] = []
    for r in current_rows:
        current_pv = float(r.page_views)
        prev_pv = prev_map.get(r.page_path, 0.0)
        growth = current_pv - prev_pv

        pages.append(
            schemas.ContentPageItem(
                page_path=r.page_path,
                page_views=current_pv,
                avg_engagement_time=float(r.avg_engagement_time),
                bounce_rate=float(r.bounce_rate),
                growth_7d=growth,
            )
        )

    return schemas.ContentPerformanceResponse(
        project_id=project_id,
        start_date=start_date,
        end_date=end_date,
        pages=pages,
    )

