import re
from pathlib import Path
from typing import Generator

import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, Session

from backend.console.dal.rds.user import User, Base


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    """Provide a fresh in-memory sqlite DB session for each test."""
    engine = create_engine("sqlite:///:memory:")
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
        normalized_sql = _normalize_mysql_to_sqlite(raw_sql)
        # Split by semicolon
        statements = [s.strip()
                      for s in normalized_sql.split(";") if s.strip()]
        with engine.begin() as conn:
            for stmt in statements:
                conn.execute(text(stmt))


def _normalize_mysql_to_sqlite(sql: str) -> str:
    # 1. Remove backticks
    sql = re.sub(r"`", "", sql)

    # 2. Remove comments
    sql = re.sub(r"COMMENT\s+'[^']*'", "", sql, flags=re.IGNORECASE)

    # 3. Handle UNIQUE KEY
    sql = re.sub(
        r"UNIQUE\s+KEY\s+\w+\s*\(([^)]+)\)",
        r"UNIQUE (\1)",
        sql,
        flags=re.IGNORECASE,
    )

    # 4. Remove MySQL specific table options (but keep the semicolon!)
    # Changed: stop before semicolon or newline
    sql = re.sub(
        r"ENGINE\s*=\s*\w+[^;]*",
        "",
        sql,
        flags=re.IGNORECASE,
    )

    # 5. Remove ON UPDATE CURRENT_TIMESTAMP
    sql = re.sub(r"ON\s+UPDATE\s+CURRENT_TIMESTAMP",
                 "", sql, flags=re.IGNORECASE)

    # 6. Convert types and handle AUTO_INCREMENT
    # SQLite uses INTEGER PRIMARY KEY AUTOINCREMENT
    sql = re.sub(r"bigint\(\d+\)\s+unsigned\s+NOT\s+NULL\s+AUTO_INCREMENT",
                 "INTEGER PRIMARY KEY AUTOINCREMENT", sql, flags=re.IGNORECASE)
    sql = re.sub(r"bigint\(\d+\)\s+unsigned",
                 "INTEGER", sql, flags=re.IGNORECASE)
    sql = re.sub(r"tinyint\(\d+\)", "INTEGER", sql, flags=re.IGNORECASE)
    sql = re.sub(r"varchar\(\d+\)", "TEXT", sql, flags=re.IGNORECASE)
    sql = re.sub(r"JSON", "TEXT", sql, flags=re.IGNORECASE)

    # 7. Remove internal INDEX/PRIMARY KEY definitions from CREATE TABLE
    lines = sql.split('\n')
    new_lines = []
    for i, line in enumerate(lines):
        # Match lines that are just INDEX / KEY / PRIMARY KEY definitions inside CREATE TABLE
        if re.search(r"^\s*(INDEX|KEY|PRIMARY\s+KEY)\s+\w*\s*\(", line, flags=re.IGNORECASE):
            # If the previous line ended with a comma, remove it
            if new_lines:
                prev_line = new_lines[-1].rstrip()
                if prev_line.endswith(','):
                    new_lines[-1] = prev_line[:-1]
            continue
        new_lines.append(line)
    sql = '\n'.join(new_lines)

    # 8. Remove trailing commas before closing CREATE TABLE parenthesis
    sql = re.sub(r",\s*\)", "\n)", sql, flags=re.MULTILINE)

    return sql


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
