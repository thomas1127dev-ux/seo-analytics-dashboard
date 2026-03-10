from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.routers import (
    projects,
    admin_ingest,
    dashboard_overview,
    dashboard_traffic,
    dashboard_content,
    dashboard_google_seo,
)


def get_frontend_origins() -> list[str]:
    """
    返回允许的前端来源列表。
    - 优先读取 FRONTEND_ORIGIN（逗号分隔支持多个）。
    - 如果未配置，则在本地开发环境下允许 localhost:5173。
    """
    origin_env = os.getenv("FRONTEND_ORIGIN")
    if origin_env:
        # 支持多个 origin，以逗号分隔
        return [origin.strip() for origin in origin_env.split(",") if origin.strip()]

    # 默认开发环境
    return ["http://localhost:5173"]


app = FastAPI(title="SEO Analytics Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_frontend_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(projects.router)
app.include_router(admin_ingest.router)
app.include_router(dashboard_overview.router)
app.include_router(dashboard_traffic.router)
app.include_router(dashboard_content.router)
app.include_router(dashboard_google_seo.router)

@app.get("/health")
def health_check():
    """
    健康检查接口，用于探活与基础连通性检查。
    """
    return {"status": "ok"}


