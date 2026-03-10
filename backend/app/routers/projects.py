from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app import models, schemas

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("", response_model=list[schemas.ProjectOut])
def list_projects(db: Session = Depends(get_db)):
    """
    返回所有 active 项目列表。
    后续接入权限后，会在这里基于当前用户进行过滤。
    """
    projects = (
        db.query(models.Project)
        .filter(models.Project.status == "active")
        .order_by(models.Project.id.asc())
        .all()
    )
    return projects


