from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy import JSON  # 或 from sqlalchemy.types import JSON
from typing import Dict, Any, Optional

Base = declarative_base()

class User(Base):
    """User table model definition"""
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, nullable=True)
    profile = Column(JSON, nullable=True, default=None, comment='User profile in JSON format')

    # -------------------------------------------------------
    # Database Operations
    # -------------------------------------------------------

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
        
        :param db: SQLAlchemy 会话
        :param username: 用户名
        :param profile: 要更新的 profile 数据（JSON 兼容的 dict）
        :return: 更新后的用户对象，或 None（如果用户不存在）
        """
        user = cls.get_by_username(db, username)
        if not user:
            return None
        
        try:
            user.profile = profile
            db.commit()
            db.refresh(user)  # 刷新以获取最新数据
            return user
        except SQLAlchemyError as e:
            db.rollback()  # 回滚事务
            raise ValueError(f"更新失败: {str(e)}")  # 或抛自定义异常