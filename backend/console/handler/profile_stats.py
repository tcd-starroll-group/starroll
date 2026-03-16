import logging
from fastapi import HTTPException

from backend.console.dal.rds.user import User as UserDAL
from backend.console.dal.rds.identify_stars_job import IdentifyStarsJob as IdentifyStarsJobDAL
from backend.console.dal.rds.user_discovered_stars import UserDiscoveredStars as UserDiscoveredStarsDAL
from backend.console.dal.rds.client import get_db
from backend.console.utils.auth import verify_user_id_and_token

# Import generated OpenAPI models
from gen.py.src.openapi_server.models.profile_stats_request import ProfileStatsRequest
from gen.py.src.openapi_server.models.profile_stats_response import ProfileStatsResponse

logger = logging.getLogger(__name__)

async def api_get_profile_stats_post(
    request: ProfileStatsRequest
) -> ProfileStatsResponse:

    # 1. Auth check (Strict requirement)
    verify_user_id_and_token(request.user_credentials.token, request.user_credentials.user_id)

    db_session = next(get_db())
    try:
        user_id = int(request.user_credentials.user_id)

        # 2. Fetch User & Format Join Date
        user = UserDAL.get_by_id(db_session, user_id)
        if not user or user.is_deleted:
            raise HTTPException(status_code=404, detail="User not found")

        # Formats the date to look like "Oct 2023" or "Mar 2026"
        join_date_str = user.created_at.strftime("%b %Y") if user.created_at else "---"

        # 3. Fetch Metrics via DAL
        total_scans = IdentifyStarsJobDAL.count_all_time_scans(db_session, user_id)
        stars_discovered = UserDiscoveredStarsDAL.count_user_discoveries(db_session, user_id)

        # 4. Calculate Rank Gamification
        rank = "Novice"
        if stars_discovered >= 200:
            rank = "Star Lord"
        elif stars_discovered >= 50:
            rank = "Astronomer"
        elif stars_discovered >= 10:
            rank = "Explorer"

        # 5. Return Response
        return ProfileStatsResponse(
            starsDiscovered=stars_discovered,
            totalScans=total_scans,
            rank=rank,
            joinDate=join_date_str
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error("CRITICAL ERROR IN PROFILE STATS HANDLER", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Error: {str(e)}")
    finally:
        db_session.close()