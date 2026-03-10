from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db import get_db
from app import models, schemas


router = APIRouter(prefix="/api/dashboard", tags=["dashboard-traffic"])


@router.get("/traffic-sources", response_model=schemas.TrafficSourcesResponse)
def get_traffic_sources(
    project_id: int = Query(..., description="项目 ID"),
    start_date: date = Query(..., description="开始日期"),
    end_date: date = Query(..., description="结束日期"),
    db: Session = Depends(get_db),
):
    """
    流量来源页接口。
    - 返回各渠道（channel）的会话/用户/PV 占比；
    - 返回按日期 + 渠道的 7 天 sessions 趋势。
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

    # 汇总各渠道在时间段内的总量
    agg_rows = (
        db.query(
            models.Ga4ChannelDaily.channel,
            func.coalesce(func.sum(models.Ga4ChannelDaily.sessions), 0).label(
                "sessions"
            ),
            func.coalesce(func.sum(models.Ga4ChannelDaily.users), 0).label("users"),
            func.coalesce(func.sum(models.Ga4ChannelDaily.page_views), 0).label(
                "page_views"
            ),
        )
        .filter(
            models.Ga4ChannelDaily.project_id == project_id,
            models.Ga4ChannelDaily.date >= start_date,
            models.Ga4ChannelDaily.date <= end_date,
        )
        .group_by(models.Ga4ChannelDaily.channel)
        .all()
    )

    total_sessions = sum(float(r.sessions) for r in agg_rows) or 1.0

    sources: list[schemas.TrafficSourceShare] = []
    for r in agg_rows:
        sources.append(
            schemas.TrafficSourceShare(
                channel=r.channel,
                sessions=float(r.sessions),
                users=float(r.users),
                page_views=float(r.page_views),
                ratio=float(r.sessions) / total_sessions,
            )
        )

    # 趋势：按日期 + 渠道的 sessions
    trend_rows = (
        db.query(
            models.Ga4ChannelDaily.date,
            models.Ga4ChannelDaily.channel,
            func.coalesce(models.Ga4ChannelDaily.sessions, 0).label("sessions"),
        )
        .filter(
            models.Ga4ChannelDaily.project_id == project_id,
            models.Ga4ChannelDaily.date >= start_date,
            models.Ga4ChannelDaily.date <= end_date,
        )
        .order_by(models.Ga4ChannelDaily.date.asc(), models.Ga4ChannelDaily.channel.asc())
        .all()
    )

    trend_points: list[schemas.TrafficTrendPoint] = [
        schemas.TrafficTrendPoint(
            date=r.date,
            channel=r.channel,
            sessions=float(r.sessions),
        )
        for r in trend_rows
    ]

    return schemas.TrafficSourcesResponse(
        project_id=project_id,
        start_date=start_date,
        end_date=end_date,
        sources=sources,
        trend_7d=trend_points,
    )

