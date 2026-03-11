import logging
from fastapi import HTTPException
from gen.py.src.openapi_server.models.api_get_saved_blogs_post_request import ApiGetSavedBlogsPostRequest
from gen.py.src.openapi_server.models.api_list_blogs_post200_response import ApiListBlogsPost200Response
from gen.py.src.openapi_server.models.blog_preview import BlogPreview
from backend.console.dal.rds.blog import Blog
from backend.console.dal.rds.client import get_db
import backend.console.utils.auth as auth_module

logger = logging.getLogger(__name__)


async def api_list_user_blogs_post(request: ApiGetSavedBlogsPostRequest) -> ApiListBlogsPost200Response:
    """List all blogs posted by the authenticated user"""
    if not request.user_credentials:
        raise HTTPException(status_code=400, detail="userCredentials is required")

    user_id = request.user_credentials.user_id
    token = request.user_credentials.token
    auth_module.verify_user_id_and_token(token, user_id)

    _db_gen = get_db()
    db = next(_db_gen)
    try:
        blogs = Blog.list_by_user_id(db, int(user_id))
        previews = [
            BlogPreview(
                blogID=str(b.blog_id),
                title=b.title,
                imageURL=(b.image_urls[0] if b.image_urls else ""),
            )
            for b in blogs
        ]
        logger.info(f"Listed {len(previews)} blogs for user_id={user_id}")
        return ApiListBlogsPost200Response(blogsList=[p.model_dump(by_alias=True) for p in previews])
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list user blogs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to list user blogs")
    finally:
        try:
            next(_db_gen)
        except StopIteration:
            pass