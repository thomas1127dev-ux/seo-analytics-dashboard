#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/<org>/seo-analytics-dashboard.git"
TARGET_DIR="seo-analytics-dashboard"

if [ -d "$TARGET_DIR" ]; then
  echo "[info] 目标目录已存在：$TARGET_DIR，将直接进入并执行部署。"
else
  echo "[info] 正在从 GitHub 克隆仓库：$REPO_URL"
  git clone "$REPO_URL" "$TARGET_DIR"
fi

cd "$TARGET_DIR/deploy"

echo "[info] 当前目录：$(pwd)"
echo "[info] 即将执行一键部署脚本（如首次运行请先根据 .env.example 填写 .env）。"

bash scripts/deploy.sh

