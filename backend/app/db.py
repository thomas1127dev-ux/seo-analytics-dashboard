from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, DeclarativeBase

from .config import get_settings


class Base(DeclarativeBase):
    """SQLAlchemy 声明式基类。"""


def _create_engine():
    settings = get_settings()
    engine = create_engine(
        settings.sqlalchemy_database_uri,
        echo=settings.env == "development",
        pool_pre_ping=True,
    )
    return engine


engine = _create_engine()
SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)


def get_db():
    """
    FastAPI 依赖：在请求生命周期内提供一个数据库会话。
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


