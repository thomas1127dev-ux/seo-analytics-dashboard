#!/usr/bin/env python3
"""
OpenClaw Skill 入口：部署、升级、状态查询。
输出为单行 JSON，便于 OpenClaw 解析。
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def get_project_root() -> Path:
    root = Path(__file__).resolve().parent.parent.parent
    return root


def get_deploy_dir() -> Path:
    return get_project_root() / "deploy"


def run_compose(deploy_dir: Path, args: list[str]) -> tuple[bool, str]:
    for cmd in ("docker compose", "docker-compose"):
        try:
            result = subprocess.run(
                [*cmd.split(), *args],
                cwd=deploy_dir,
                capture_output=True,
                text=True,
                timeout=300,
            )
            out = (result.stdout or "").strip() + "\n" + (result.stderr or "").strip()
            return result.returncode == 0, out
        except FileNotFoundError:
            continue
        except subprocess.TimeoutExpired:
            return False, "执行超时"
    return False, "未找到 docker compose 或 docker-compose 命令"


def get_backend_url(deploy_dir: Path) -> str:
    env_file = deploy_dir / ".env"
    port = "4000"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("BACKEND_PORT=") and "=" in line:
                port = line.split("=", 1)[1].strip().strip('"').strip("'") or "4000"
                break
    return f"http://localhost:{port}"


def get_frontend_url(deploy_dir: Path) -> str:
    env_file = deploy_dir / ".env"
    port = "5173"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("FRONTEND_PORT=") and "=" in line:
                port = line.split("=", 1)[1].strip().strip('"').strip("'") or "5173"
                break
    return f"http://localhost:{port}"


def check_health(url: str) -> bool:
    try:
        import urllib.request
        req = urllib.request.urlopen(f"{url}/health", timeout=5)
        return req.status == 200 and b"ok" in req.read().lower()
    except Exception:
        return False


def cmd_deploy(deploy_dir: Path, env: str, config_path: Path) -> dict:
    env_file = deploy_dir / ".env"
    example = deploy_dir / ".env.example"
    if not env_file.exists() and example.exists():
        import shutil
        shutil.copy(example, env_file)

    if not env_file.exists():
        return {
            "status": "failed",
            "error_code": "MISSING_ENV",
            "message": "缺少 .env 文件，请从 .env.example 复制并填写配置",
        }

    ok, out = run_compose(deploy_dir, ["up", "-d", "--build"])
    if not ok:
        return {
            "status": "failed",
            "error_code": "DOCKER_ERROR",
            "message": "容器启动或构建失败",
            "detail": out[:500] if out else "",
        }

    # 迁移（忽略失败，可能后端尚未就绪）
    run_compose(deploy_dir, ["exec", "-T", "backend", "uv", "run", "alembic", "upgrade", "head"])

    backend_url = get_backend_url(deploy_dir)
    frontend_url = get_frontend_url(deploy_dir)
    healthy = check_health(backend_url)

    return {
        "status": "success" if healthy else "degraded",
        "env": env,
        "backend_url": backend_url,
        "frontend_url": frontend_url,
        "health_ok": healthy,
        "message": "部署完成" if healthy else "部署完成，但后端健康检查未通过，请稍后重试或查看日志",
    }


def cmd_upgrade(deploy_dir: Path, env: str, config_path: Path) -> dict:
    return cmd_deploy(deploy_dir, env, config_path)


def cmd_status(deploy_dir: Path, env: str, config_path: Path) -> dict:
    ok, out = run_compose(deploy_dir, ["ps"])
    if not ok:
        return {
            "status": "failed",
            "error_code": "DOCKER_ERROR",
            "message": "无法获取容器状态",
            "detail": out[:300] if out else "",
        }

    backend_url = get_backend_url(deploy_dir)
    frontend_url = get_frontend_url(deploy_dir)
    healthy = check_health(backend_url)

    return {
        "status": "success",
        "env": env,
        "backend_url": backend_url,
        "frontend_url": frontend_url,
        "health_ok": healthy,
        "message": "运行正常" if healthy else "后端健康检查未通过",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="OpenClaw Skill: SEO 看板部署与状态")
    parser.add_argument("command", choices=["deploy", "upgrade", "status"], help="子命令")
    parser.add_argument("--env", default="dev", help="环境标识")
    parser.add_argument("--config", default=None, help="openclaw-skill.yaml 路径")
    args = parser.parse_args()

    root = get_project_root()
    deploy_dir = get_deploy_dir()
    if not deploy_dir.is_dir():
        result = {
            "status": "failed",
            "error_code": "NO_DEPLOY_DIR",
            "message": f"未找到 deploy 目录: {deploy_dir}",
        }
        print(json.dumps(result, ensure_ascii=False))
        return 1

    config_path = Path(args.config) if args.config else (deploy_dir / "openclaw-skill.yaml")

    handlers = {"deploy": cmd_deploy, "upgrade": cmd_upgrade, "status": cmd_status}
    result = handlers[args.command](deploy_dir, args.env, config_path)

    print(json.dumps(result, ensure_ascii=False))
    return 0 if result.get("status") in ("success", "degraded") else 1


if __name__ == "__main__":
    sys.exit(main())
