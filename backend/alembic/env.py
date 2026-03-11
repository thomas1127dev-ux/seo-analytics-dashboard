from __future__ import annotations

from sqlalchemy import engine_from_config, pool
from alembic import context

import os
import sys

# 确保后端根目录在 Python 路径中，这样可以正确导入 `app` 包
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.db import Base
from app.config import get_settings
from app import models  # noqa: F401  导入以注册模型到 Base.metadata


# 读取 alembic.ini 的配置
config = context.config


def get_url() -> str:
    settings = get_settings()
    return settings.sqlalchemy_database_uri


target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """以 offline 模式运行迁移（生成 SQL 脚本）。"""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """以 online 模式运行迁移（直接连库执行）。"""
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

