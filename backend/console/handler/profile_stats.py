import logging
from fastapi import HTTPException

from backend.console.dal.rds.user import User as UserDAL
from backend.console.dal.rds.identify_stars_job import IdentifyStarsJob as IdentifyStarsJobDAL
from backend.console.dal.rds.user_discovered_stars import UserDiscoveredStars as UserDiscoveredStarsDAL
from backend.console.dal.rds.client import db_context
from backend.console.utils.auth import get_current_user_id

logger = logging.getLogger(__name__)


async def api_get_profile_stats_post(request: any):

    user_id = int(get_current_user_id())

    with db_context() as db_session:
        user = UserDAL.get_by_id(db_session, user_id)
        if not user or user.is_deleted:
            raise HTTPException(status_code=404, detail="User not found")

        join_date_str = user.created_at.strftime("%b %Y") if user.created_at else "---"

        total_scans = IdentifyStarsJobDAL.count_all_time_scans(db_session, user_id)
        stars_discovered = UserDiscoveredStarsDAL.count_user_discoveries(db_session, user_id)

        rank = "Novice"
        if stars_discovered >= 200:
            rank = "Star Lord"
        elif stars_discovered >= 50:
            rank = "Astronomer"
        elif stars_discovered >= 10:
            rank = "Explorer"

        # Construct a safe dictionary for the frontend
        frontend_profile = dict(user.profile) if user.profile else {}
        if user.avatar_url:
            frontend_profile["avatar"] = user.avatar_url

        # Return a raw dictionary. FastAPI will serialize this perfectly to JSON
        return {
            "starsDiscovered": stars_discovered,
            "totalScans": total_scans,
            "rank": rank,
            "joinDate": join_date_str,
            "email": user.email,
            "profile": frontend_profile
        }