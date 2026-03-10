from __future__ import annotations

from datetime import date
from typing import Optional

import requests
from sqlalchemy.orm import Session

from app.config import get_settings
from app import models


class YandexResourceNotFound(Exception):
    """用于标记 Yandex 接口返回 RESOURCE_NOT_FOUND 的业务异常。"""


def fetch_yandex_daily_summary(
    host: str,
    target_date: date,
) -> dict[str, Optional[float]]:
    """
    占位实现：根据公司最终选用的 Yandex 产品（Metrica / Webmaster），
    需要对接对应的 HTTP API。

    这里给出一个基础结构，演示如何处理 RESOURCE_NOT_FOUND 等错误码：
    - 若返回中包含 RESOURCE_NOT_FOUND，则抛出 YandexResourceNotFound，
      上层将安全忽略。
    - 若为其他错误，则抛出 RuntimeError。

    当前默认返回空 dict，表示暂未接好实际 Yandex 接口。
    """
    settings = get_settings()
    token = settings.yandex_access_token
    if not token:
        # 未配置 token 视为暂不接入 Yandex，返回空数据
        return {}

    # 下面保留一个伪代码结构，实际对接时需要根据公司提供的 API 文档调整：
    #
    # url = "https://api.webmaster.yandex.net/..."  # 或 Metrica API
    # headers = {"Authorization": f"OAuth {token}"}
    # params = {...}
    #
    # resp = requests.get(url, headers=headers, params=params, timeout=10)
    # if resp.status_code == 404 and "RESOURCE_NOT_FOUND" in resp.text:
    #     raise YandexResourceNotFound("Yandex RESOURCE_NOT_FOUND")
    # if not resp.ok:
    #     raise RuntimeError(f"Yandex API error: {resp.status_code} {resp.text}")
    #
    # data = resp.json()
    # 解析 data，返回 impressions / clicks / ctr / avg_position 等字段。

    return {}


def ingest_yandex_daily_for_project(
    db: Session,
    project: models.Project,
    target_date: date,
) -> Optional[models.YandexDaily]:
    """
    针对单个 project + 日期，从 Yandex 拉取数据并写入 / 更新 yandex_daily。
    若遇到 RESOURCE_NOT_FOUND 或未配置 token/host，安全返回 None。
    """
    if not project.yandex_host:
        return None

    try:
        metrics = fetch_yandex_daily_summary(project.yandex_host, target_date)
    except YandexResourceNotFound:
        # 公司要求：若接口返回 RESOURCE_NOT_FOUND，必须安全忽略
        return None

    if not metrics:
        # 无数据也直接忽略
        return None

    existing: Optional[models.YandexDaily] = (
        db.query(models.YandexDaily)
        .filter(
            models.YandexDaily.project_id == project.id,
            models.YandexDaily.date == target_date,
        )
        .first()
    )

    if existing:
        for key, value in metrics.items():
            setattr(existing, key, value)
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing

    record = models.YandexDaily(
        project_id=project.id,
        date=target_date,
        **metrics,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


