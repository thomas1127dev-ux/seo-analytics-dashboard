from __future__ import annotations

from datetime import datetime, date
from typing import Optional, List

from pydantic import BaseModel


class ProjectBase(BaseModel):
    project_key: str
    name: str
    domain: str
    ga4_property_id: Optional[str] = None
    gsc_property: Optional[str] = None
    yandex_host: Optional[str] = None
    status: str


class ProjectOut(ProjectBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DailyPoint(BaseModel):
    date: date
    value: Optional[float]


class MetricWithTrend(BaseModel):
    current: Optional[float]
    yesterday: Optional[float]
    trend_7d: List[DailyPoint]


class Ga4OverviewMetrics(BaseModel):
    dau: MetricWithTrend
    sessions: MetricWithTrend
    page_views: MetricWithTrend
    avg_engagement_time: MetricWithTrend
    engagement_rate: MetricWithTrend
    bounce_rate: MetricWithTrend


class SearchOverviewMetrics(BaseModel):
    impressions: MetricWithTrend
    clicks: MetricWithTrend
    ctr: MetricWithTrend
    avg_position: MetricWithTrend


class OverviewResponse(BaseModel):
    project_id: int
    start_date: date
    end_date: date
    ga4: Ga4OverviewMetrics
    gsc: SearchOverviewMetrics
    yandex: SearchOverviewMetrics


class TrafficSourceShare(BaseModel):
    channel: str
    sessions: float
    users: float
    page_views: float
    ratio: float


class TrafficTrendPoint(BaseModel):
    date: date
    channel: str
    sessions: float


class TrafficSourcesResponse(BaseModel):
    project_id: int
    start_date: date
    end_date: date
    sources: list[TrafficSourceShare]
    trend_7d: list[TrafficTrendPoint]


class ContentPageItem(BaseModel):
    page_path: str
    page_views: float
    avg_engagement_time: float
    bounce_rate: float
    growth_7d: float


class ContentPerformanceResponse(BaseModel):
    project_id: int
    start_date: date
    end_date: date
    pages: list[ContentPageItem]


class SeoItem(BaseModel):
    key: str  # 关键词或页面
    clicks: float
    impressions: float
    ctr: float
    avg_position: float


class SeoListResponse(BaseModel):
    project_id: int
    start_date: date
    end_date: date
    items: list[SeoItem]


