import logging
from fastapi import HTTPException
from openapi_server.models.api_create_blog_post_request import ApiCreateBlogPostRequest
from openapi_server.models.api_create_blog_post200_response import ApiCreateBlogPost200Response
from backend.console.dal.rds.blog import Blog
from backend.console.dal.rds.client import db_context
import backend.console.utils.auth as auth_module

logger = logging.getLogger(__name__)


async def api_create_blog_post(request: ApiCreateBlogPostRequest) -> ApiCreateBlogPost200Response:
    if not request.hip:
        raise HTTPException(status_code=400, detail="HIP is required")
    if not request.title:
        raise HTTPException(status_code=400, detail="title is required")

    user_id = auth_module.get_current_user_id()

    with db_context() as db:
        blog = Blog.create(
            db=db,
            user_id=int(user_id),
            hip=int(request.hip),
            title=request.title,
            content=request.content or "",
            image_urls=request.image_url_list or [],
        )
        logger.info(
            f"Blog created: blog_id={blog.blog_id} user_id={user_id} HIP={request.hip}")
        return ApiCreateBlogPost200Response(blogID=str(blog.blog_id), messages="Post Successful")
