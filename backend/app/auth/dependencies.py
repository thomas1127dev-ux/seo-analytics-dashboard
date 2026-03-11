from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.db import get_db
from app import models
from app.auth.security import decode_access_token


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    """
    从 Bearer Token 中解析当前登录用户。
    """
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的访问令牌",
        )

    sub = payload.get("sub")
    if sub is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的访问令牌",
        )

    try:
        user_id = int(sub)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的访问令牌",
        )

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已被禁用",
        )

    return user


def ensure_project_access(
    project_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> models.Project:
    """
    统一的项目访问权限校验。
    - 检查项目是否存在且为 active；
    - 检查当前用户是否有权访问该 project。
    """
    project = (
        db.query(models.Project)
        .filter(models.Project.id == project_id, models.Project.status == "active")
        .first()
    )
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="project 不存在或已停用",
        )

    # 系统管理员拥有所有项目访问权
    if current_user.is_admin:
        return project

    # 首版按用户-项目直接授权表校验，后续可扩展部门/小组模型
    has_direct_permission = (
        db.query(models.UserProjectPermission.id)
        .filter(
            models.UserProjectPermission.user_id == current_user.id,
            models.UserProjectPermission.project_id == project_id,
        )
        .first()
    )
    if has_direct_permission:
        return project

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="当前用户无权访问该项目",
    )

