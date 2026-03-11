from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app import models, schemas
from app.auth.dependencies import get_current_user


router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("", response_model=list[schemas.ProjectOut])
def list_projects(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    返回当前用户可访问的 active 项目列表。
    - 管理员：返回所有 active 项目；
    - 普通用户：基于 user_project_permissions 做过滤。
    """
    base_query = db.query(models.Project).filter(models.Project.status == "active")

    if current_user.is_admin:
        projects = base_query.order_by(models.Project.id.asc()).all()
        return projects

    projects = (
        base_query.join(
            models.UserProjectPermission,
            models.UserProjectPermission.project_id == models.Project.id,
        )
        .filter(models.UserProjectPermission.user_id == current_user.id)
        .order_by(models.Project.id.asc())
        .all()
    )
    return projects


