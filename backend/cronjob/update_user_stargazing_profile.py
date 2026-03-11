"""
Periodically aggregates each user's observation history and writes a
stargazing_profile summary into user.profile (JSON field).

Stored structure inside user.profile:
{
  ...,                              <- any existing profile fields are preserved
  "stargazing_profile": {
    "preferred_constellations": ["Orion", "Leo"],   <- top constellations by count
    "preferred_hours": [22, 23, 0],                 <- top observation hours (sorted)
    "observation_count": 42,
    "last_updated": "2026-03-09"
  }
}
"""

import json
import logging
from collections import Counter
from datetime import date

from backend.console.dal.rds.client import get_db
from backend.console.dal.rds.identify_stars_job import IdentifyStarsJob
from backend.console.dal.rds.user import User
from backend.console.handler.get_stargazing_recommendation import _extract_constellations_from_result
from backend.constant.star_identify import STAR_IDENTIFY_JOB_STATUS_SUCCEEDED

logger = logging.getLogger(__name__)

# How many recent jobs to consider per user
HISTORY_LIMIT = 200


def update_user_stargazing_profile_handler():
    """APScheduler entry point (synchronous)."""
    db_session = next(get_db())
    try:
        user_ids = IdentifyStarsJob.list_recent_user_ids(db_session, days=30)
        logger.info(f"Updating stargazing profiles for {len(user_ids)} active users")

        for user_id in user_ids:
            try:
                _update_one_user(db_session, user_id)
            except Exception as e:
                logger.error(f"Failed to update profile for user {user_id}: {e}")
    finally:
        db_session.close()


def _update_one_user(db_session, user_id: int):
    jobs = IdentifyStarsJob.list_by_user_id(db_session, user_id, limit=HISTORY_LIMIT)

    constellation_counter: Counter = Counter()
    hour_counter: Counter = Counter()

    succeeded_count = 0
    for job in jobs:
        if job.status != STAR_IDENTIFY_JOB_STATUS_SUCCEEDED:
            continue
        succeeded_count += 1
        if job.created_at:
            hour_counter[job.created_at.hour] += 1
        if job.result:
            try:
                data = json.loads(job.result) if isinstance(job.result, str) else job.result
                for constellation in _extract_constellations_from_result(data):
                    constellation_counter[constellation] += 1
            except Exception as e:
                logger.warning(f"Skipping job {job.id} result parse: {e}")

    # Top 5 constellations and top 3 observation hours
    preferred_constellations = [name for name, _ in constellation_counter.most_common(5)]
    preferred_hours = sorted(hour for hour, _ in hour_counter.most_common(3))

    stargazing_profile = {
        "preferred_constellations": preferred_constellations,
        "preferred_hours": preferred_hours,
        "observation_count": succeeded_count,
        "last_updated": date.today().isoformat(),
    }

    # Read current profile and merge (preserve any other existing fields)
    user = User.get_by_id(db_session, user_id)
    if not user:
        logger.warning(f"User {user_id} not found, skipping profile update")
        return

    # Copy the existing profile to avoid SQLAlchemy missing in-place dict mutations
    current_profile = dict(user.profile) if user.profile else {}
    current_profile["stargazing_profile"] = stargazing_profile

    User.update_profile_by_id(db_session, user_id, current_profile)
    logger.info(
        f"Updated stargazing profile for user {user_id}: "
        f"{len(jobs)} jobs, top constellations={preferred_constellations}"
    )
