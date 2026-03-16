from typing import List, Optional

from sqlalchemy import BigInteger, Column, SmallInteger, String, TIMESTAMP, Float, text
from sqlalchemy.orm import Session, declarative_base

Base = declarative_base()


class ObservationSite(Base):
    """Candidate observation sites maintained by the project."""
    __tablename__ = "observation_site"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    light_pollution_score = Column(Float, nullable=False, default=50.0)
    description = Column(String(512), nullable=True, default="")
    is_active = Column(SmallInteger, nullable=False, default=1)
    created_at = Column(TIMESTAMP, nullable=False,
                        server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text(
        "CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    @classmethod
    def list_active(cls, db: Session) -> List["ObservationSite"]:
        return db.query(cls).filter(cls.is_active == 1).all()

    @classmethod
    def get_by_id(cls, db: Session, site_id: int) -> Optional["ObservationSite"]:
        return db.query(cls).filter(
            cls.id == site_id,
            cls.is_active == 1
        ).first()
