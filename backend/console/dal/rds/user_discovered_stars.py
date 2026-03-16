from sqlalchemy import Column, BigInteger, TIMESTAMP, func
from backend.console.dal.rds.user import Base

class UserDiscoveredStars(Base):
    __tablename__ = 'user_discovered_stars'

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='Discovery ID (Primary Key)')
    user_id = Column(BigInteger, nullable=False, comment='User ID')
    hip_id = Column(BigInteger, nullable=False, comment='Star HIP ID')
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), comment='Creation timestamp')

    @classmethod
    def count_user_discoveries(cls, db_session, user_id: int) -> int:
        """
        Counts the total number of unique stars a user has discovered.
        Because of the UNIQUE KEY in the database, a simple count is safe and fast.
        """
        return db_session.query(cls).filter(cls.user_id == user_id).count()