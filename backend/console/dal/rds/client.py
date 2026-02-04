from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.config import settings
from backend.constant import app_env as app_env_const

if settings.app_env == app_env_const.DEV or settings.app_env == app_env_const.PROD:
    engine = create_engine(
        settings.sqlalchemy_database_url, pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Get database session generator"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
