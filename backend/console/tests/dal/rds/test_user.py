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


def test_get_by_username_found(db_session: Session):
    created = User.create(db_session, "bob", "hash2", "bob@example.com")

    fetched = User.get_by_username(db_session, "bob")
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.username == "bob"


def test_get_by_username_not_found(db_session: Session):
    result = User.get_by_username(db_session, "nonexistent")
    assert result is None


def test_update_password_success(db_session: Session):
    User.create(db_session, "carol", "old_hash", "carol@example.com")

    updated = User.update_password(db_session, "carol", "new_hash")
    assert updated is True

    user = User.get_by_username(db_session, "carol")
    assert user is not None
    assert user.password == "new_hash"


def test_update_password_user_not_found(db_session: Session):
    updated = User.update_password(db_session, "ghost", "whatever")
    assert updated is False


def test_delete_by_username_success(db_session: Session):
    User.create(db_session, "dave", "hash3", "dave@example.com")

    deleted = User.delete_by_username(db_session, "dave")
    assert deleted is True

    user = User.get_by_username(db_session, "dave")
    assert user is None


def test_delete_by_username_user_not_found(db_session: Session):
    deleted = User.delete_by_username(db_session, "missing")
    assert deleted is False
