import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from backend.console.dal.rds.user import User, Base


def test_create_user(db_session: Session):
    user = User.create(db_session, "alice", "hash1", "alice@example.com")

    assert user.id is not None
    assert user.username == "alice"
    assert user.password == "hash1"
    assert user.email == "alice@example.com"

    fetched = db_session.query(User).filter_by(username="alice").first()
    assert fetched is not None
    assert fetched.id == user.id


def test_get_by_id_found(db_session: Session):
    created = User.create(db_session, "bob", "hash2", "bob@example.com")

    fetched = User.get_by_id(db_session, created.id)
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.username == "bob"


def test_get_by_id_not_found(db_session: Session):
    result = User.get_by_id(db_session, 999999)
    assert result is None


def test_update_password_success(db_session: Session):
    created = User.create(db_session, "carol", "old_hash", "carol@example.com")

    updated = User.update_password(db_session, created.id, "new_hash")
    assert updated is True

    user = User.get_by_id(db_session, created.id)
    assert user is not None
    assert user.password == "new_hash"


def test_update_password_user_not_found(db_session: Session):
    updated = User.update_password(db_session, 999999, "whatever")
    assert updated is False
