import logging
from fastapi import HTTPException
from gen.py.src.openapi_server.models.api_create_blog_post_request import ApiCreateBlogPostRequest
from gen.py.src.openapi_server.models.api_create_blog_post200_response import ApiCreateBlogPost200Response
from backend.console.dal.rds.blog import Blog
from backend.console.dal.rds.client import get_db
import backend.console.utils.auth as auth_module

logger = logging.getLogger(__name__)


async def api_create_blog_post(request: ApiCreateBlogPostRequest) -> ApiCreateBlogPost200Response:
    if not request.user_credentials:
        raise HTTPException(status_code=400, detail="userCredentials is required")
    if not request.hip:
        raise HTTPException(status_code=400, detail="HIP is required")
    if not request.title:
        raise HTTPException(status_code=400, detail="title is required")

    user_id = request.user_credentials.user_id
    token = request.user_credentials.token
    auth_module.verify_user_id_and_token(token, user_id)

    _db_gen = get_db()
    db = next(_db_gen)
    try:
        blog = Blog.create(
            db=db,
            user_id=int(user_id),
            hip=int(request.hip),
            title=request.title,
            content=request.content or "",
            image_urls=request.image_url_list or [],
        )
        logger.info(f"Blog created: blog_id={blog.blog_id} user_id={user_id} HIP={request.hip}")
        return ApiCreateBlogPost200Response(blogID=str(blog.blog_id), messages="Post Successful")
    except Exception as e:
        logger.error(f"Failed to create blog: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create blog")
    finally:
        try:
            next(_db_gen)
        except StopIteration:
            pass