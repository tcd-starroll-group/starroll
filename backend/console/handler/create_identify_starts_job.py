import uuid
import logging
import base64
from datetime import datetime, timezone

from fastapi import HTTPException
from gen.py.src.openapi_server.models.api_create_identify_stars_job_post200_response import ApiCreateIdentifyStarsJobPost200Response
from gen.py.src.openapi_server.models.api_create_identify_stars_job_post_request import ApiCreateIdentifyStarsJobPostRequest
from gen.py.src.openapi_server.models.user_credentials import UserCredentials


from backend.console.dal.tos import upload_bytes
from backend.console.dal.rds.identify_stars_job import IdentifyStarsJob
from backend.console.dal.rds.client import get_db
from backend.constant import tos as tos_const
from backend.console.utils.auth import verify_access_token, verify_user_id_and_token
from backend.constant import star_identify as star_identify_const

logger = logging.getLogger(__name__)


async def api_create_identify_stars_job_post(
    request: ApiCreateIdentifyStarsJobPostRequest
) -> ApiCreateIdentifyStarsJobPost200Response:

    # Validate required fields
    if not request.user_id:
        logger.error("userID is missing")
        raise HTTPException(status_code=400, detail="userID is required")
    if not request.token:
        logger.error("token is missing")
        raise HTTPException(status_code=400, detail="token is required")
    if not request.image:
        logger.error("image is missing")
        raise HTTPException(status_code=400, detail="image is required")

    # Verify access token and user ID
    verify_user_id_and_token(request.token, request.user_id)

    logger.info(
        f"Token verification successful for user_id: {request.user_id}")

    # Decode base64 image
    try:
        image_bytes = base64.b64decode(request.image)
        logger.info(
            f"Successfully decoded base64 image: {len(image_bytes)} bytes")
    except Exception as e:
        logger.error(f"Failed to decode base64 image: {str(e)}")
        raise HTTPException(
            status_code=400, detail=f"Invalid base64 image data: {str(e)}")

    # Generate object key: userID/{timestamp}_{uuid}
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    random_suffix = uuid.uuid4().hex[:8]
    object_key = f"{request.user_id}/{timestamp}_{random_suffix}.jpg"
    logger.info(f"Generated object key: {object_key}")

    # Upload to MinIO
    logger.info(f"Uploading to bucket: {tos_const.IDENTIFY_STARS_BUCKET_NAME}")
    try:
        upload_bytes(
            data=image_bytes,
            object_name=object_key,
            bucket_name=tos_const.IDENTIFY_STARS_BUCKET_NAME,
            content_type="image/jpeg",
        )
        logger.info(f"Successfully uploaded image to MinIO: {object_key}")
    except Exception as e:
        logger.error(
            f"Failed to upload image to MinIO: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to upload image: {str(e)}")

    # Save job to database
    logger.info(f"Saving job to database for userID: {request.user_id}")
    db_session = next(get_db())
    try:
        job = IdentifyStarsJob.create(
            db=db_session,
            user_id=int(request.user_id),
            image_key=object_key,
            status=star_identify_const.STAR_IDENTIFY_JOB_STATUS_PENDING,
        )
        logger.info(f"Successfully created job with ID: {job.id}")
        return ApiCreateIdentifyStarsJobPost200Response(jobID=str(job.id))
    except Exception as e:
        logger.error(
            f"Failed to create job in database: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to create job: {str(e)}")
    finally:
        db_session.close()
