from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    Float,
    UniqueConstraint,
)

from .db import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_key = Column(String(64), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    domain = Column(String(255), nullable=False)
    ga4_property_id = Column(String(64), nullable=True)
    gsc_property = Column(String(255), nullable=True)
    yandex_host = Column(String(255), nullable=True)
    status = Column(String(32), nullable=False, default="active")

    created_at = Column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class Ga4Daily(Base):
    __tablename__ = "ga4_daily"
    __table_args__ = (
        UniqueConstraint("project_id", "date", name="uq_ga4_daily_project_date"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)

    dau = Column(Integer, nullable=True)
    sessions = Column(Integer, nullable=True)
    page_views = Column(Integer, nullable=True)
    avg_engagement_time = Column(Float, nullable=True)
    engagement_rate = Column(Float, nullable=True)
    bounce_rate = Column(Float, nullable=True)


class GscDaily(Base):
    __tablename__ = "gsc_daily"
    __table_args__ = (
        UniqueConstraint("project_id", "date", name="uq_gsc_daily_project_date"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)

    impressions = Column(Integer, nullable=True)
    clicks = Column(Integer, nullable=True)
    ctr = Column(Float, nullable=True)
    avg_position = Column(Float, nullable=True)


class YandexDaily(Base):
    __tablename__ = "yandex_daily"
    __table_args__ = (
        UniqueConstraint("project_id", "date", name="uq_yandex_daily_project_date"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)

    impressions = Column(Integer, nullable=True)
    clicks = Column(Integer, nullable=True)
    ctr = Column(Float, nullable=True)
    avg_position = Column(Float, nullable=True)


