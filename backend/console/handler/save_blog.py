import logging
from fastapi import HTTPException
from gen.py.src.openapi_server.models.api_get_saved_blogs_post_request import ApiGetSavedBlogsPostRequest
from gen.py.src.openapi_server.models.api_delete_blog_post200_response import ApiDeleteBlogPost200Response
from backend.console.dal.rds.blog import Blog
from backend.console.dal.rds.blog_interactions import BlogSave
from backend.console.dal.rds.client import get_db
import backend.console.utils.auth as auth_module

logger = logging.getLogger(__name__)


async def api_save_blog_post(request: ApiGetSavedBlogsPostRequest) -> ApiDeleteBlogPost200Response:
    if not request.user_credentials:
        raise HTTPException(status_code=400, detail="userCredentials is required")
    if not request.blog_id:
        raise HTTPException(status_code=400, detail="blogID is required")

    user_id = request.user_credentials.user_id
    token = request.user_credentials.token
    auth_module.verify_user_id_and_token(token, user_id)

    _db_gen = get_db()
    db = next(_db_gen)
    try:
        blog = Blog.get_by_id(db, int(request.blog_id))
        if not blog:
            raise HTTPException(status_code=404, detail="Blog not found")

        if not BlogSave.exists(db, blog_id=int(request.blog_id), user_id=int(user_id)):
            BlogSave.create(db, blog_id=int(request.blog_id), user_id=int(user_id))
            logger.info(f"Blog saved: blog_id={request.blog_id} user_id={user_id}")
        else:
            logger.info(f"Blog already saved: blog_id={request.blog_id} user_id={user_id}")

        return ApiDeleteBlogPost200Response(blogID=request.blog_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to save blog: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to save blog")
    finally:
        try:
            next(_db_gen)
        except StopIteration:
            pass