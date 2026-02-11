from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.config import settings
from backend.constant import app_env as app_env_const

engine = None
SessionLocal = None

if settings.app_env == app_env_const.DEV or settings.app_env == app_env_const.PROD:
    engine = create_engine(
        settings.sqlalchemy_database_url,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        pool_recycle=3600,  # Recycle connections after 1 hour
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Get database session generator"""
    if SessionLocal is None:
        raise RuntimeError("Database not configured for this environment")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def dispose_engine():
    """Dispose all database connections (should be called on app shutdown)"""
    global engine
    if engine is not None:
        engine.dispose()
