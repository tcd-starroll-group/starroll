from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base, Session

Base = declarative_base()

class User(Base):
    """User table model definition"""
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, nullable=True)

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