import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import BaseModel


# 优先从当前目录或父级加载 .env 文件（用于本地开发）
load_dotenv()


class Settings(BaseModel):
    """应用配置，集中管理环境变量。"""

    # 通用
    env: str = os.getenv("NODE_ENV", "development")
    port: int = int(os.getenv("PORT", "4000"))
    frontend_origin: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")

    # 数据库（MySQL）
    db_host: str = os.getenv("DB_HOST", "127.0.0.1")
    db_port: int = int(os.getenv("DB_PORT", "3306"))
    db_user: str = os.getenv("DB_USER", "root")
    db_password: str = os.getenv("DB_PASSWORD", "")
    db_name: str = os.getenv("DB_NAME", "seo_analytics_dashboard")

    # Google Cloud Service Account
    google_service_account_json: str | None = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    google_application_credentials: str | None = os.getenv(
        "GOOGLE_APPLICATION_CREDENTIALS"
    )

    # GA4 / GSC / Yandex 基础配置占位
    ga4_property_id: str | None = os.getenv("GA4_PROPERTY_ID")
    gsc_site_url: str | None = os.getenv("GSC_SITE_URL")
    yandex_access_token: str | None = os.getenv("YANDEX_ACCESS_TOKEN")

    @property
    def sqlalchemy_database_uri(self) -> str:
        """
        生成 SQLAlchemy MySQL 连接 URI。
        使用 mysql+mysqldb 驱动（对应 mysqlclient）。
        """
        user = self.db_user
        password = self.db_password
        host = self.db_host
        port = self.db_port
        name = self.db_name

        if password:
            return f"mysql+mysqldb://{user}:{password}@{host}:{port}/{name}"
        return f"mysql+mysqldb://{user}@{host}:{port}/{name}"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


