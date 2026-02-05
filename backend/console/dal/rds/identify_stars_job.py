from sqlalchemy import Column, Integer, BigInteger, String, JSON, TIMESTAMP, SmallInteger, text
from sqlalchemy.orm import declarative_base, Session

Base = declarative_base()

class IdentifyStarsJob(Base):
    """Identify stars jobs table model definition"""
    __tablename__ = "identify_stars_jobs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    image_key = Column(String(512), nullable=False)
    status = Column(String(16), nullable=False)
    result = Column(JSON, nullable=True)
    is_deleted = Column(SmallInteger, nullable=False, default=0)

    # -------------------------------------------------------
    # Database Operations
    # -------------------------------------------------------

    @classmethod
    def get_by_id(cls, db: Session, job_id: int):
        """Query job by ID"""
        return db.query(cls).filter(cls.id == job_id, cls.is_deleted == 0).first()

    @classmethod
    def list_by_user_id(cls, db: Session, user_id: int, limit: int = 20, offset: int = 0):
        """List jobs for a specific user"""
        return db.query(cls).filter(
            cls.user_id == user_id, 
            cls.is_deleted == 0
        ).order_by(cls.created_at.desc()).offset(offset).limit(limit).all()

    @classmethod
    def create(cls, db: Session, user_id: int, image_key: str, status: str = "PENDING"):
        """Create a new identify stars job"""
        new_job = cls(
            user_id=user_id,
            image_key=image_key,
            status=status
        )
        db.add(new_job)
        db.commit()
        db.refresh(new_job)
        return new_job

    @classmethod
    def update_status(cls, db: Session, job_id: int, status: str, result: dict = None):
        """Update job status and result"""
        job = cls.get_by_id(db, job_id)
        if job:
            job.status = status
            if result is not None:
                job.result = result
            db.commit()
            return True
        return False

    @classmethod
    def soft_delete(cls, db: Session, job_id: int):
        """Soft delete a job"""
        job = cls.get_by_id(db, job_id)
        if job:
            job.is_deleted = 1
            db.commit()
            return True
        return False
