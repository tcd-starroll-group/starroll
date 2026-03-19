import logging
from fastapi import HTTPException
<<<<<<< HEAD
from gen.py.src.openapi_server.models.api_get_saved_blogs_post_request import ApiGetSavedBlogsPostRequest
from gen.py.src.openapi_server.models.api_delete_blog_post200_response import ApiDeleteBlogPost200Response
from backend.console.dal.rds.blog import Blog
from backend.console.dal.rds.client import get_db
=======
from openapi_server.models.blog_id import BlogID
from backend.console.dal.rds.blog import Blog
from backend.console.dal.rds.client import db_context
>>>>>>> main
import backend.console.utils.auth as auth_module

logger = logging.getLogger(__name__)


<<<<<<< HEAD
async def api_delete_blog_post(request: ApiGetSavedBlogsPostRequest) -> ApiDeleteBlogPost200Response:
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
        deleted = Blog.soft_delete(db, blog_id=int(request.blog_id), user_id=int(user_id))
        if not deleted:
            raise HTTPException(status_code=404, detail="Blog not found or permission denied")

        logger.info(f"Blog deleted: blog_id={request.blog_id} user_id={user_id}")
        return ApiDeleteBlogPost200Response(blogID=request.blog_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete blog: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete blog")
    finally:
        try:
            next(_db_gen)
        except StopIteration:
            pass
=======
async def api_delete_blog_post(request: BlogID) -> BlogID:
    if not request.blog_id:
        raise HTTPException(status_code=400, detail="blogID is required")

    user_id = auth_module.get_current_user_id()

    with db_context() as db:
        deleted = Blog.soft_delete(db, blog_id=int(
            request.blog_id), user_id=int(user_id))
        if not deleted:
            raise HTTPException(
                status_code=404, detail="Blog not found or permission denied")

        logger.info(
            f"Blog deleted: blog_id={request.blog_id} user_id={user_id}")
        return BlogID(blogID=request.blog_id)
>>>>>>> main
