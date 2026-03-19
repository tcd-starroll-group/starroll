import logging
from fastapi import HTTPException
<<<<<<< HEAD
from gen.py.src.openapi_server.models.api_get_saved_blogs_post_request import ApiGetSavedBlogsPostRequest
from gen.py.src.openapi_server.models.api_like_blog_post200_response import ApiLikeBlogPost200Response
from backend.console.dal.rds.blog import Blog
from backend.console.dal.rds.blog_interactions import BlogLike
from backend.console.dal.rds.client import get_db
=======
from openapi_server.models.blog_id import BlogID
from openapi_server.models.api_like_blog_post200_response import ApiLikeBlogPost200Response
from backend.console.dal.rds.blog import Blog
from backend.console.dal.rds.blog_interactions import BlogLike
from backend.console.dal.rds.client import db_context
>>>>>>> main
import backend.console.utils.auth as auth_module

logger = logging.getLogger(__name__)


<<<<<<< HEAD
async def api_like_blog_post(request: ApiGetSavedBlogsPostRequest) -> ApiLikeBlogPost200Response:
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
=======
async def api_like_blog_post(request: BlogID) -> ApiLikeBlogPost200Response:
    if not request.blog_id:
        raise HTTPException(status_code=400, detail="blogID is required")

    user_id = auth_module.get_current_user_id()

    with db_context() as db:
>>>>>>> main
        blog = Blog.get_by_id(db, int(request.blog_id))
        if not blog:
            raise HTTPException(status_code=404, detail="Blog not found")

        if not BlogLike.exists(db, blog_id=int(request.blog_id), user_id=int(user_id)):
<<<<<<< HEAD
            BlogLike.create(db, blog_id=int(request.blog_id), user_id=int(user_id))
            Blog.increment_like_count(db, int(request.blog_id))
            logger.info(f"Blog liked: blog_id={request.blog_id} user_id={user_id}")
        else:
            logger.info(f"Blog already liked: blog_id={request.blog_id} user_id={user_id}")
=======
            BlogLike.create(db, blog_id=int(
                request.blog_id), user_id=int(user_id))
            Blog.increment_like_count(db, int(request.blog_id))
            logger.info(
                f"Blog liked: blog_id={request.blog_id} user_id={user_id}")
        else:
            logger.info(
                f"Blog already liked: blog_id={request.blog_id} user_id={user_id}")
>>>>>>> main

        # Refresh to get updated like_count
        db.refresh(blog)
        return ApiLikeBlogPost200Response(blogID=request.blog_id, likeNumber=blog.like_count)
<<<<<<< HEAD
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to like blog: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to like blog")
    finally:
        try:
            next(_db_gen)
        except StopIteration:
            pass
=======
>>>>>>> main
