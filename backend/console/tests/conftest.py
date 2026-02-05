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


def _execute_sql_files(engine) -> None:
    sql_dir = Path(__file__).resolve().parents[1] / "dal" / "rds" / "sql"
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
    sql = re.sub(r"`", "", sql)
    sql = re.sub(r"COMMENT\s+'[^']*'", "", sql, flags=re.IGNORECASE)
    sql = re.sub(
        r"UNIQUE\s+KEY\s+\w+\s*\(([^)]+)\)",
        r"UNIQUE (\1)",
        sql,
        flags=re.IGNORECASE,
    )
    sql = re.sub(
        r"ENGINE\s*=\s*\w+\s*DEFAULT\s+CHARSET\s*=\s*\w+(\s*COMMENT\s*=\s*'[^']*')?",
        "",
        sql,
        flags=re.IGNORECASE,
    )
    sql = re.sub(r"ON\s+UPDATE\s+CURRENT_TIMESTAMP",
                 "", sql, flags=re.IGNORECASE)
    sql = re.sub(
        r"bigint\(\d+\)\s+unsigned\s+NOT\s+NULL\s+AUTO_INCREMENT",
        "INTEGER",
        sql,
        flags=re.IGNORECASE,
    )
    sql = re.sub(r"bigint\(\d+\)\s+unsigned",
                 "INTEGER", sql, flags=re.IGNORECASE)
    sql = re.sub(r"tinyint\(\d+\)", "INTEGER", sql, flags=re.IGNORECASE)
    sql = re.sub(r"varchar\(\d+\)", "TEXT", sql, flags=re.IGNORECASE)
    return sql


def _validate_models_match_db(engine) -> None:
    inspector = inspect(engine)
    db_tables = set(inspector.get_table_names())

    for table_name, table in Base.metadata.tables.items():
        if table_name not in db_tables:
            raise AssertionError(
                f"Table '{table_name}' is missing in database.")

        db_columns = {col["name"] for col in inspector.get_columns(table_name)}
        model_columns = set(table.columns.keys())
        missing_columns = model_columns - db_columns
        if missing_columns:
            raise AssertionError(
                f"Table '{table_name}' is missing columns: {sorted(missing_columns)}"
            )