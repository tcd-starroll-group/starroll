from sqlalchemy import Column, Integer, BigInteger, String, JSON, TIMESTAMP, SmallInteger, text
from sqlalchemy.orm import declarative_base, Session
from backend.constant.sort import SORT_ORDER_ASC, SORT_ORDER_DESC
from backend.constant.star_identify import STAR_IDENTIFY_JOB_STATUS_PENDING

Base = declarative_base()


class IdentifyStarsJob(Base):
    """Identify stars jobs table model definition"""
    __tablename__ = "identify_stars_jobs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False,
                        server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text(
        "CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    image_key = Column(String(512), nullable=False)
    status = Column(String(16), nullable=False)
    result = Column(JSON, nullable=True)
    is_deleted = Column(SmallInteger, nullable=False, default=0)
    astronomy_net_job_id = Column(
        BigInteger, nullable=True, comment="Astronomy.net job ID")

    # -------------------------------------------------------
    # Database Operations
    # -------------------------------------------------------

    @classmethod
    def get_by_id(cls, db: Session, job_id: int):
        """Query job by ID"""
        return db.query(cls).filter(cls.id == job_id, cls.is_deleted == 0).first()

    @classmethod
    def list_by_user_id(cls, db: Session, user_id: int, limit: int = 20, offset: int = 0, order: str = SORT_ORDER_DESC):
        """List jobs for a specific user"""
        query = db.query(cls).filter(
            cls.user_id == user_id,
            cls.is_deleted == 0
        )

        # Apply sorting (with ID as secondary sort for deterministic ordering)
        if order == SORT_ORDER_ASC:
            query = query.order_by(cls.created_at.asc(), cls.id.asc())
        else:
            query = query.order_by(cls.created_at.desc(), cls.id.desc())

        return query.offset(offset).limit(limit).all()

    @classmethod
    def list_by_job_status(cls, db: Session, statuses: list, limit: int = 20, offset: int = 0, order: str = SORT_ORDER_DESC):
        """
        List jobs for specific statuses.

        Args:
            db: Database session.
            statuses: List of statuses to filter by.
            limit: Maximum number of results to return.
            offset: Number of results to skip.
            order: Sorting order (ASC or DESC).

        Returns:
            List of jobs matching the given statuses.
        """
        query = db.query(cls).filter(
            cls.status.in_(statuses),
            cls.is_deleted == 0
        )

        # Apply sorting (with ID as secondary sort for deterministic ordering)
        if order == SORT_ORDER_ASC:
            query = query.order_by(cls.created_at.asc(), cls.id.asc())
        else:
            query = query.order_by(cls.created_at.desc(), cls.id.desc())

        return query.offset(offset).limit(limit).all()

    @classmethod
    def create(cls, db: Session, user_id: int, image_key: str, status: str = STAR_IDENTIFY_JOB_STATUS_PENDING):
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
    def soft_delete(cls, db: Session, job_id: int):
        """Soft delete a job"""
        job = cls.get_by_id(db, job_id)
        if job:
            job.is_deleted = 1
            db.commit()
            return True
        return False

    @classmethod
    def update(cls, db: Session, job_id: int, **kwargs):
        """
        Update the fields of an IdentifyStarsJob instance in the database.

        Args:
            db: Database session.
            job_id: ID of the job to update.
            **kwargs: Fields to update and their new values.

        Returns:
            True if the update was successful, False otherwise.
        """
        job = cls.get_by_id(db, job_id)
        if job:
            for key, value in kwargs.items():
                if hasattr(job, key):
                    setattr(job, key, value)
            db.commit()
            return True
        return False
