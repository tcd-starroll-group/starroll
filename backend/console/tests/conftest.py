import os
from pathlib import Path
from typing import Generator

import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, Session

from backend.console.dal.rds.user import User, Base


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    """Provide a fresh MySQL DB session for each test in UT environment."""
    engine = create_engine(_mysql_test_url(), pool_pre_ping=True)
    _execute_sql_files(engine)
    _validate_models_match_db(engine)
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
        # Split by semicolon
        statements = [s.strip() for s in raw_sql.split(";") if s.strip()]
        with engine.begin() as conn:
            for stmt in statements:
                conn.execute(text(stmt))


def _mysql_test_url() -> str:
    host = os.getenv("MYSQL_HOST", "127.0.0.1")
    port = os.getenv("MYSQL_PORT", "3306")
    user = os.getenv("MYSQL_USER", "test_user")
    password = os.getenv("MYSQL_PASSWORD", "test_password")
    db_name = os.getenv("MYSQL_DB_NAME", "console")
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}"


def _validate_models_match_db(engine) -> None:
    inspector = inspect(engine)
    db_tables = set(inspector.get_table_names())

    for table_name, table in Base.metadata.tables.items():
        if table_name not in db_tables:
            continue

        db_columns = {col["name"] for col in inspector.get_columns(table_name)}
        model_columns = set(table.columns.keys())
        missing_columns = model_columns - db_columns
        if missing_columns:
            raise AssertionError(
                f"Table '{table_name}' is missing columns: {sorted(missing_columns)}"
            )


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
