import pytest
from sqlalchemy.orm import Session
from backend.console.dal.rds.identify_stars_job import IdentifyStarsJob

def test_create_job(db_session: Session):
    job = IdentifyStarsJob.create(db_session, user_id=1, image_key="test_image.jpg")

    assert job.id is not None
    assert job.user_id == 1
    assert job.image_key == "test_image.jpg"
    assert job.status == "PENDING"
    assert job.is_deleted == 0

    fetched = db_session.query(IdentifyStarsJob).filter_by(id=job.id).first()
    assert fetched is not None
    assert fetched.image_key == "test_image.jpg"

def test_get_by_id(db_session: Session):
    created = IdentifyStarsJob.create(db_session, user_id=1, image_key="test.jpg")
    
    fetched = IdentifyStarsJob.get_by_id(db_session, created.id)
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.user_id == 1

def test_get_by_id_not_found(db_session: Session):
    result = IdentifyStarsJob.get_by_id(db_session, 999)
    assert result is None

def test_list_by_user_id(db_session: Session):
    IdentifyStarsJob.create(db_session, user_id=1, image_key="img1.jpg")
    IdentifyStarsJob.create(db_session, user_id=1, image_key="img2.jpg")
    IdentifyStarsJob.create(db_session, user_id=2, image_key="img3.jpg")

    jobs_user1 = IdentifyStarsJob.list_by_user_id(db_session, user_id=1)
    assert len(jobs_user1) == 2
    
    jobs_user2 = IdentifyStarsJob.list_by_user_id(db_session, user_id=2)
    assert len(jobs_user2) == 1

def test_update_status_and_result(db_session: Session):
    job = IdentifyStarsJob.create(db_session, user_id=1, image_key="test.jpg")
    
    test_result = {"stars": [{"name": "Polaris", "ra": 37.95, "dec": 89.26}]}
    updated = IdentifyStarsJob.update_status(db_session, job.id, status="COMPLETED", result=test_result)
    
    assert updated is True
    
    fetched = IdentifyStarsJob.get_by_id(db_session, job.id)
    assert fetched.status == "COMPLETED"
    assert fetched.result == test_result

def test_soft_delete(db_session: Session):
    job = IdentifyStarsJob.create(db_session, user_id=1, image_key="delete_me.jpg")
    
    deleted = IdentifyStarsJob.soft_delete(db_session, job.id)
    assert deleted is True
    
    # Should not be found by get_by_id because it filters is_deleted == 0
    fetched = IdentifyStarsJob.get_by_id(db_session, job.id)
    assert fetched is None
    
    # But still exists in DB
    raw_fetched = db_session.query(IdentifyStarsJob).filter_by(id=job.id).first()
    assert raw_fetched is not None
    assert raw_fetched.is_deleted == 1
