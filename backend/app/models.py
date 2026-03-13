from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    Float,
    UniqueConstraint,
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import relationship

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


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_admin = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)

    created_at = Column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False)


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, autoincrement=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    name = Column(String(255), nullable=False)

    department = relationship("Department")


class UserDepartment(Base):
    __tablename__ = "user_departments"
    __table_args__ = (
        UniqueConstraint("user_id", "department_id", name="uq_user_department"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)

    user = relationship("User")
    department = relationship("Department")


class UserGroup(Base):
    __tablename__ = "user_groups"
    __table_args__ = (
        UniqueConstraint("user_id", "group_id", name="uq_user_group"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)

    user = relationship("User")
    group = relationship("Group")


class UserProjectPermission(Base):
    __tablename__ = "user_project_permissions"
    __table_args__ = (
        UniqueConstraint("user_id", "project_id", name="uq_user_project_permission"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    user = relationship("User")
    project = relationship("Project")


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

    # 新增 GA4 指标：新用户、老用户及 1–7 日留存人数
    new_users = Column(Integer, nullable=True)
    returning_users = Column(Integer, nullable=True)
    retention_d1 = Column(Integer, nullable=True)
    retention_d2 = Column(Integer, nullable=True)
    retention_d3 = Column(Integer, nullable=True)
    retention_d4 = Column(Integer, nullable=True)
    retention_d5 = Column(Integer, nullable=True)
    retention_d6 = Column(Integer, nullable=True)
    retention_d7 = Column(Integer, nullable=True)


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


class Ga4ChannelDaily(Base):
    __tablename__ = "ga4_channel_daily"
    __table_args__ = (
        UniqueConstraint(
            "project_id", "date", "channel", name="uq_ga4_channel_project_date_channel"
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    channel = Column(String(64), nullable=False, index=True)

    sessions = Column(Integer, nullable=True)
    users = Column(Integer, nullable=True)
    page_views = Column(Integer, nullable=True)


class Ga4PageDaily(Base):
    __tablename__ = "ga4_page_daily"
    __table_args__ = (
        UniqueConstraint(
            "project_id", "date", "page_path", name="uq_ga4_page_project_date_path"
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    page_path = Column(String(512), nullable=False, index=True)

    page_views = Column(Integer, nullable=True)
    avg_engagement_time = Column(Float, nullable=True)
    bounce_rate = Column(Float, nullable=True)


class GscQueryDaily(Base):
    __tablename__ = "gsc_query_daily"
    __table_args__ = (
        UniqueConstraint(
            "project_id", "date", "query", name="uq_gsc_query_project_date_query"
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    query = Column(String(512), nullable=False, index=True)

    impressions = Column(Integer, nullable=True)
    clicks = Column(Integer, nullable=True)
    ctr = Column(Float, nullable=True)
    avg_position = Column(Float, nullable=True)


class GscPageDaily(Base):
    __tablename__ = "gsc_page_daily"
    __table_args__ = (
        UniqueConstraint(
            "project_id", "date", "page", name="uq_gsc_page_project_date_page"
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    page = Column(String(512), nullable=False, index=True)

    impressions = Column(Integer, nullable=True)
    clicks = Column(Integer, nullable=True)
    ctr = Column(Float, nullable=True)
    avg_position = Column(Float, nullable=True)


class YandexQueryDaily(Base):
    __tablename__ = "yandex_query_daily"
    __table_args__ = (
        UniqueConstraint(
            "project_id", "date", "query", name="uq_yandex_query_project_date_query"
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    query = Column(String(512), nullable=False, index=True)

    impressions = Column(Integer, nullable=True)
    clicks = Column(Integer, nullable=True)
    ctr = Column(Float, nullable=True)


