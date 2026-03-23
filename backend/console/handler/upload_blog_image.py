import base64
import uuid
import logging
from datetime import datetime, timezone, timedelta

from fastapi import HTTPException
from openapi_server.models.api_upload_blog_image_post_request import ApiUploadBlogImagePostRequest
from openapi_server.models.api_upload_blog_image_post200_response import ApiUploadBlogImagePost200Response

from backend.console.dal.tos import upload_bytes, get_presigned_get_url
from backend.constant import tos as tos_const
import backend.console.utils.auth as auth_module

logger = logging.getLogger(__name__)


async def api_upload_blog_image_post(
    request: ApiUploadBlogImagePostRequest,
) -> ApiUploadBlogImagePost200Response:
    if not request:
        raise HTTPException(status_code=400, detail="request body is required")
    if not request.image:
        raise HTTPException(status_code=400, detail="image is required")

    user_id = auth_module.get_current_user_id()

    # Decode base64 image
    try:
        image_bytes = base64.b64decode(request.image)
    except Exception as e:
        logger.error(f"Failed to decode base64 image: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid base64 image data: {e}")

    # Generate object key: {user_id}/{timestamp}_{uuid}.jpg
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    random_suffix = uuid.uuid4().hex[:8]
    object_key = f"{user_id}/{timestamp}_{random_suffix}.jpg"

    # Upload to MinIO
    try:
        upload_bytes(
            data=image_bytes,
            object_name=object_key,
            bucket_name=tos_const.BLOG_IMAGES_BUCKET_NAME,
            content_type="image/jpeg",
        )
        logger.info(f"Uploaded blog image: {object_key}")
    except Exception as e:
        logger.error(f"Failed to upload blog image: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {e}")

    # Generate presigned URL (7 days)
    try:
        image_url = get_presigned_get_url(
            object_name=object_key,
            bucket_name=tos_const.BLOG_IMAGES_BUCKET_NAME,
            expires=timedelta(days=7),
        )
    except Exception as e:
        logger.error(f"Failed to generate presigned URL: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate image URL: {e}")

    return ApiUploadBlogImagePost200Response(imageURL=image_url)
