import hashlib

from backend.console.dal.rds.user import User


def test_update_last_gps(db_session):
    hashed_password = hashlib.sha256("password123".encode()).hexdigest()
    user = User.create(db_session, "alice",
                       hashed_password, "alice@example.com")

    updated = user.set_last_gps(
        db_session,
        {"latitude": 30.2741, "longitude": 120.1551},
    )

    assert updated is not None
    assert updated.last_gps == {"latitude": 30.2741, "longitude": 120.1551}
