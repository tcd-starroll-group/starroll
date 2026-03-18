import logging
from fastapi import HTTPException
from openapi_server.models.blog_id import BlogID
from backend.console.dal.rds.blog import Blog
from backend.console.dal.rds.blog_interactions import BlogSave
from backend.console.dal.rds.client import db_context
import backend.console.utils.auth as auth_module

logger = logging.getLogger(__name__)


async def api_save_blog_post(request: BlogID) -> BlogID:
    if not request.blog_id:
        raise HTTPException(status_code=400, detail="blogID is required")

    user_id = auth_module.get_current_user_id()

    with db_context() as db:
        blog = Blog.get_by_id(db, int(request.blog_id))
        if not blog:
            raise HTTPException(status_code=404, detail="Blog not found")

        if not BlogSave.exists(db, blog_id=int(request.blog_id), user_id=int(user_id)):
            BlogSave.create(db, blog_id=int(
                request.blog_id), user_id=int(user_id))
            logger.info(
                f"Blog saved: blog_id={request.blog_id} user_id={user_id}")
        else:
            logger.info(
                f"Blog already saved: blog_id={request.blog_id} user_id={user_id}")

        return BlogID(blogID=request.blog_id)
