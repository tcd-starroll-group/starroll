from datetime import datetime, timezone
import logging
from fastapi import HTTPException, Body
from openapi_server.models.api_list_identify_stars_jobs_post200_response import ApiListIdentifyStarsJobsPost200Response
from openapi_server.models.pagination_query import PaginationQuery


from backend.console.dal.rds.identify_stars_job import IdentifyStarsJob
from backend.console.dal.rds.client import db_context
from backend.console.utils.auth import get_current_user_id
from backend.constant.sort import SORT_BY_CREATE_TIME, SORT_ORDER_DESC, SORT_ORDER_ASC

logger = logging.getLogger(__name__)


async def api_list_identify_stars_jobs_post(
    request: PaginationQuery,
) -> ApiListIdentifyStarsJobsPost200Response:
    """List identify stars jobs for a user"""

    user_id = get_current_user_id()

    # Get pagination parameters
    limit = request.limit if request.limit is not None else 20
    offset = request.offset if request.offset is not None else 0
    order = request.order if request.order is not None else SORT_ORDER_DESC

    # Validate sort field (only 'create_time' is supported)
    if request.sort and request.sort != SORT_BY_CREATE_TIME:
        logger.error(f"Unsupported sort field: {request.sort}")
        raise HTTPException(
            status_code=400,
            detail=f"Only '{SORT_BY_CREATE_TIME}' is supported for sorting")

    logger.info(
        f"Listing jobs for user_id: {user_id}, "
        f"limit: {limit}, offset: {offset}, order: {order}")

    # Query database
    with db_context() as db_session:
        db_jobs = IdentifyStarsJob.list_by_user_id(
            db=db_session,
            user_id=int(user_id),
            limit=limit,
            offset=offset,
            order=order
        )

        logger.info(
            f"Found {len(db_jobs)} jobs for user {user_id}")

        # Convert database models to API models
        api_jobs = []
        for db_job in db_jobs:
            api_job = {
                "jobID": str(db_job.id),
                "status": db_job.status,
                "createTime": db_job.created_at.isoformat() if db_job.created_at else None,
                "updateTime": db_job.updated_at.isoformat() if db_job.updated_at else None
            }
            api_jobs.append(api_job)

        return ApiListIdentifyStarsJobsPost200Response(
            identify_stars_jobs_list=api_jobs
        )
