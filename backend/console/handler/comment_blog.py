import logging
from fastapi import HTTPException
from openapi_server.models.api_comment_blog_post_request import ApiCommentBlogPostRequest
from openapi_server.models.api_comment_blog_post200_response import ApiCommentBlogPost200Response
from backend.console.dal.rds.blog import Blog
from backend.console.dal.rds.blog_comment import BlogComment
from backend.console.dal.rds.client import db_context
import backend.console.utils.auth as auth_module

logger = logging.getLogger(__name__)


async def api_comment_blog_post(request: ApiCommentBlogPostRequest) -> ApiCommentBlogPost200Response:
    if not request.blog_id:
        raise HTTPException(status_code=400, detail="blogID is required")
    if not request.comment_text:
        raise HTTPException(status_code=400, detail="commentText is required")

    user_id = auth_module.get_current_user_id()

    with db_context() as db:
        blog = Blog.get_by_id(db, int(request.blog_id))
        if not blog:
            raise HTTPException(status_code=404, detail="Blog not found")

        comment = BlogComment.create(
            db=db,
            blog_id=int(request.blog_id),
            user_id=int(user_id),
            content=request.comment_text,
        )
        Blog.increment_comment_count(db, int(request.blog_id))

        logger.info(
            f"Comment created: comment_id={comment.comment_id} blog_id={request.blog_id}")
        return ApiCommentBlogPost200Response(commentID=str(comment.comment_id))
