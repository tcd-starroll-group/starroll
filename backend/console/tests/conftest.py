import re
from pathlib import Path
from typing import Generator

import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool  # [Added critical import]
from fastapi.testclient import TestClient

import backend.console.dal.rds.client as rds_client
from backend.console.dal.rds.client import get_db
from backend.console.dal.rds.user import User, Base
from gen.py.src.openapi_server.main import app


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    """Provide a fresh in-memory SQLite DB session for each test."""
    # Use StaticPool to ensure the database stays in memory during tests,
    # preventing data loss when connections are closed.
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool 
    )
    
    _execute_sql_files(engine)
    _validate_models_match_db(engine)
    
    TestingSessionLocal = sessionmaker(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_session) -> Generator[TestClient, None, None]:
    """
    Create a test client.
    Manually patch SessionLocal to resolve NameError issues.
    """
    
    # Manually inject SessionLocal into the rds_client module
    original_session_local = getattr(rds_client, "SessionLocal", None)
    rds_client.SessionLocal = lambda: db_session

    # Also configure dependency_overrides for FastAPI
    def override_get_db():
        try:
            yield db_session
        finally:
            # Note: Although session.close() is called here, memory data 
            # is preserved because StaticPool is used.
            pass
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as c:
        yield c
    
    # Cleanup after tests
    app.dependency_overrides.clear()
    if original_session_local:
        rds_client.SessionLocal = original_session_local
    else:
        del rds_client.SessionLocal


def _execute_sql_files(engine) -> None:
    """Find and execute SQL initialization files, converting them to SQLite syntax."""
    sql_dir = Path(__file__).resolve().parents[1] / "dal" / "rds" / "sql"
    if not sql_dir.exists():
         sql_dir = Path(__file__).resolve().parents[2] / "dal" / "rds" / "sql"

    if not sql_dir.exists():
        raise FileNotFoundError(f"SQL directory not found: {sql_dir}")

    for sql_path in sorted(sql_dir.glob("*.sql")):
        raw_sql = sql_path.read_text(encoding="utf-8")
        normalized_sql = _normalize_mysql_to_sqlite(raw_sql)
        statements = [s.strip()
                      for s in normalized_sql.split(";") if s.strip()]
        with engine.begin() as conn:
            for stmt in statements:
                conn.execute(text(stmt))


def _normalize_mysql_to_sqlite(sql: str) -> str:
    """Regex-based utility to convert MySQL dialect SQL to SQLite compatible syntax."""
    sql = re.sub(r"`", "", sql)
    sql = re.sub(r"COMMENT\s+'[^']*'", "", sql, flags=re.IGNORECASE)
    sql = re.sub(r"UNIQUE\s+KEY\s+\w+\s*\(([^)]+)\)", r"UNIQUE (\1)", sql, flags=re.IGNORECASE)
    sql = re.sub(r"ENGINE\s*=\s*\w+\s*DEFAULT\s+CHARSET\s*=\s*\w+(\s*COMMENT\s*=\s*'[^']*')?", "", sql, flags=re.IGNORECASE)
    sql = re.sub(r"ON\s+UPDATE\s+CURRENT_TIMESTAMP", "", sql, flags=re.IGNORECASE)
    sql = re.sub(r"bigint\(\d+\)\s+unsigned\s+NOT\s+NULL\s+AUTO_INCREMENT", "INTEGER", sql, flags=re.IGNORECASE)
    sql = re.sub(r"bigint\(\d+\)\s+unsigned", "INTEGER", sql, flags=re.IGNORECASE)
    sql = re.sub(r"tinyint\(\d+\)", "INTEGER", sql, flags=re.IGNORECASE)
    sql = re.sub(r"varchar\(\d+\)", "TEXT", sql, flags=re.IGNORECASE)
    return sql


def _validate_models_match_db(engine) -> None:
    """Verify that the SQL-created schema matches the SQLAlchemy models."""
    inspector = inspect(engine)
    db_tables = set(inspector.get_table_names())

    for table_name, table in Base.metadata.tables.items():
        if table_name not in db_tables:
            raise AssertionError(f"Table '{table_name}' is missing in database.")
        db_columns = {col["name"] for col in inspector.get_columns(table_name)}
        model_columns = set(table.columns.keys())
        missing_columns = model_columns - db_columns
        if missing_columns:
            raise AssertionError(f"Table '{table_name}' is missing columns: {sorted(missing_columns)}")