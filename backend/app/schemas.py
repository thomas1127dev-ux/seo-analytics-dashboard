from __future__ import annotations

from datetime import datetime
from typing import Optional

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


