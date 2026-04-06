import os
from pathlib import Path
from typing import Generator

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session


def _get_mysql_url() -> str:
    host = os.getenv("MYSQL_HOST", "127.0.0.1")
    port = os.getenv("MYSQL_PORT", "3306")
    user = os.getenv("MYSQL_USER", "test_user")
    password = os.getenv("MYSQL_PASSWORD", "test_password")
    db = os.getenv("MYSQL_DB_NAME", "console")
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}"


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    """Provide a MySQL DB session for each test, with schema recreated from SQL files."""
    engine = create_engine(_get_mysql_url())
    _execute_sql_files(engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def _execute_sql_files(engine) -> None:
    sql_dir = Path(__file__).resolve().parents[1] / "dal" / "rds" / "sql"
    if not sql_dir.exists():
        raise FileNotFoundError(f"SQL directory not found: {sql_dir}")

    for sql_path in sorted(sql_dir.glob("*.sql")):
        raw_sql = sql_path.read_text(encoding="utf-8")
        statements = [s.strip() for s in raw_sql.split(";") if s.strip()]
        with engine.begin() as conn:
            for stmt in statements:
                conn.execute(text(stmt))


# ==================== MinIO Test Fixtures ====================

@pytest.fixture(scope="session")
def minio_settings():
    """Provide MinIO connection settings for tests."""
    import os
    return {
        "endpoint": os.getenv("MINIO_ENDPOINT", "localhost:9000"),
        "access_key": os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
        "secret_key": os.getenv("MINIO_SECRET_KEY", "minioadmin"),
        "secure": os.getenv("MINIO_SECURE", "false").lower() == "true",
    }


@pytest.fixture(scope="session")
def minio_client(minio_settings):
    """Provide a MinIO client instance for the entire test session."""
    from minio import Minio

    client = Minio(
        minio_settings["endpoint"],
        access_key=minio_settings["access_key"],
        secret_key=minio_settings["secret_key"],
        secure=minio_settings["secure"],
    )

    return client


@pytest.fixture
def test_bucket(minio_client):
    """Create and clean up a test bucket for each test."""
    import uuid
    from minio.error import S3Error

    bucket_name = f"test-bucket-{uuid.uuid4().hex[:8]}"

    # Create bucket
    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)

    yield bucket_name

    # Cleanup: remove all objects then remove bucket
    try:
        objects = minio_client.list_objects(bucket_name, recursive=True)
        for obj in objects:
            minio_client.remove_object(bucket_name, obj.object_name)
        minio_client.remove_bucket(bucket_name)
    except S3Error:
        pass  # Ignore cleanup errors
