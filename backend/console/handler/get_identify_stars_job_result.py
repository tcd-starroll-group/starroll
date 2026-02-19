import logging
from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.console.dal.rds.identify_stars_job import IdentifyStarsJob
from backend.console.dal.rds.client import get_db
from backend.console.utils.auth import verify_user_id_and_token

# Note: Ensure these import paths match your generated gen/ directory
from gen.py.src.openapi_server.models.api_get_identify_stars_job_result_post_request import ApiGetIdentifyStarsJobResultPostRequest
from gen.py.src.openapi_server.models.api_get_identify_stars_job_result_post200_response import ApiGetIdentifyStarsJobResultPost200Response

logger = logging.getLogger(__name__)

async def api_get_identify_stars_job_result_post(
    request: ApiGetIdentifyStarsJobResultPostRequest
) -> ApiGetIdentifyStarsJobResultPost200Response:

    # 1. Verification of User
    if not request.user_credentials:
        raise HTTPException(status_code=400, detail="User credentials missing")
    
    verify_user_id_and_token(request.user_credentials.token, request.user_credentials.user_id)

    # 2. Database Lookup
    db_session = next(get_db())
    try:
        # Cast jobID to int since your DB uses BigInteger
        job = IdentifyStarsJob.get_by_id(db_session, int(request.job_id))

        # 3. Security & Existence Check
        if not job:
            logger.error(f"Job {request.job_id} not found")
            raise HTTPException(status_code=404, detail="Job not found")
        
        if job.user_id != int(request.user_credentials.user_id):
            logger.warning(f"Unauthorized access attempt: User {request.user_credentials.user_id} on Job {job.id}")
            raise HTTPException(status_code=403, detail="Not authorized to view this job")

        # 4. Construct Response 
        # The schema expects a list: identifyStarsJobsList
        return ApiGetIdentifyStarsJobResultPost200Response(
            identify_stars_jobs_list=[{
                "id": str(job.id),
                "status": job.status,
                "result": job.result, # This pulls the JSON data directly
                "image_key": job.image_key,
                "created_at": job.created_at.isoformat() if job.created_at else None
            }]
        )

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid jobID format")
    finally:
        db_session.close()