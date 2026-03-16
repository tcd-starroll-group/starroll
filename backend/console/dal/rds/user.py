from datetime import datetime

from sqlalchemy import Boolean, DateTime,  Column, Integer, String
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy import JSON  # 或 from sqlalchemy.types import JSON
from sqlalchemy.exc import SQLAlchemyError
from typing import Dict, Any, Optional

Base = declarative_base()


class User(Base):
    """User table model definition"""
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, nullable=True)
    last_gps = Column(JSON, nullable=True, default=None,
                      comment='User last GPS location')
    profile = Column(JSON, nullable=True, default=None,
                     comment='User profile in JSON format')


    created_at = Column(DateTime, default=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)
    # -------------------------------------------------------
    # Database Operations
    # -------------------------------------------------------
    @classmethod
    def get_by_id(cls, db: Session, user_id: int):
        """Query user by ID"""
        return db.query(cls).filter(cls.id == user_id).first()
    
    @classmethod
    def get_by_username(cls, db: Session, username: str):
        """Query user by username"""
        return db.query(cls).filter(cls.username == username).first()

    @classmethod
    def create(cls, db: Session, username: str, password_hash: str, email: str):
        """Create a new user"""
        new_user = cls(
            username=username,
            password=password_hash,
            email=email
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    @classmethod
    def delete_by_username(cls, db: Session, username: str):
        """Delete user by username"""
        user = cls.get_by_username(db, username)
        if user:
            db.delete(user)
            db.commit()
            return True
        return False

    @classmethod
    def update_password(cls, db: Session, username: str, new_password_hash: str):
        """Update user password"""
        user = cls.get_by_username(db, username)
        if user:
            user.password = new_password_hash
            db.commit()
            return True
        return False

    @classmethod
    def edit_profile(cls, db: Session, username: str, profile: Dict[str, Any]) -> Optional["User"]:
        """
        更新用户 profile。

        :param db: SQLAlchemy 
        :param username: 
        :param profile: 
        :return: 
        """
        user = cls.get_by_username(db, username)
        if not user:
            return None

        try:
            user.profile = profile
            db.commit()
            db.refresh(user)
            return user
        except SQLAlchemyError as e:
            db.rollback()
            raise ValueError(f"更新失败: {str(e)}")

    @classmethod
    def update_last_gps(cls, db: Session, username: str, last_gps: Dict[str, Any]) -> Optional["User"]:
        """Update the user's latest GPS payload."""
        user = cls.get_by_username(db, username)
        if not user:
            return None

        try:
            user.last_gps = last_gps
            db.commit()
            db.refresh(user)
            return user
        except SQLAlchemyError as e:
            db.rollback()
            raise ValueError(f"更新失败: {str(e)}")

    @classmethod
    def get_by_email(cls, db_session: Session, email: str):
        return db_session.query(cls).filter(cls.email == email).first()

    @classmethod
    def list_with_email(cls, db: Session):
        """List users that can receive recommendation emails."""
        return db.query(cls).filter(
            cls.email.is_not(None),
            cls.email != ""
        ).all()

    @classmethod
    def update_password_by_email(cls, db: Session, email: str, new_password_hash: str):
        """Update user password by email"""
        user = cls.get_by_email(db, email)
        if user:
            user.password = new_password_hash
            db.commit()
            return True
        return False
