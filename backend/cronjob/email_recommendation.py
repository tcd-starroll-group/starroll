import logging

from backend.console.dal.rds.client import db_context
from backend.console.dal.rds.user import User
from backend.console.handler.generate_email_recommendation import generate_recommendation_for_user
from backend.console.utils.email_sender import send_recommendation_email

logger = logging.getLogger(__name__)


def email_recommendation_handler():
    """Send recommendation emails to all users that have email and GPS data."""
    with db_context() as db_session:
        return _send_recommendations(db_session)


def _send_recommendations(db_session):
    users = User.list_with_email(db_session)
    result = {
        "processed": 0,
        "sent": 0,
        "skipped": 0,
        "failed": 0,
    }

    for user in users:
        result["processed"] += 1
        try:
            recommendation = generate_recommendation_for_user(db_session, user)
            if recommendation is None:
                result["skipped"] += 1
                logger.info(
                    "Skip recommendation email for user %s: GPS not found",
                    user.username,
                )
                continue

            if send_recommendation_email(user.email, recommendation):
                result["sent"] += 1
            else:
                result["failed"] += 1
        except Exception as exc:
            result["failed"] += 1
            logger.error(
                "Failed to send recommendation email for user %s: %s",
                user.username,
                exc,
                exc_info=True,
            )

    logger.info("Recommendation email job finished: %s", result)
    return result
