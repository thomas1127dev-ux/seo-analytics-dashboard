#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[info] 当前目录: $ROOT_DIR"

if ! command -v docker >/dev/null 2>&1; then
  echo "[error] 未找到 docker 命令，请先安装 Docker。" >&2
  exit 1
fi

if ! docker compose version >/dev/null 2>&1 && ! command -v docker-compose >/dev/null 2>&1; then
  echo "[error] 未找到 docker compose / docker-compose，请安装 docker compose 插件或 docker-compose。" >&2
  exit 1
fi

if [ ! -f ".env" ]; then
  echo "[info] 未找到 .env，正在从 .env.example 创建……"
  if [ -f ".env.example" ]; then
    cp .env.example .env
    echo "[info] 已在 deploy 目录创建 .env，请根据注释填写配置后重新运行本脚本。"
    exit 0
  else
    echo "[error] 缺少 .env.example 模板文件。" >&2
    exit 1
  fi
fi

echo "[info] 启动 / 更新容器……"
if docker compose version >/dev/null 2>&1; then
  docker compose up -d --build
else
  docker-compose up -d --build
fi

echo "[info] 容器已启动，后端健康检查请访问: http://localhost:${BACKEND_PORT:-4000}/health"

