import logging
from fastapi import HTTPException
<<<<<<< HEAD
from gen.py.src.openapi_server.models.api_view_blog_post_request import ApiViewBlogPostRequest
from gen.py.src.openapi_server.models.blog import Blog as BlogModel
=======
from openapi_server.models.blog_id import BlogID
from openapi_server.models.blog import Blog as BlogModel
>>>>>>> main
from backend.console.dal.rds.blog import Blog
from backend.console.dal.rds.blog_comment import BlogComment
from backend.console.dal.rds.client import get_db

logger = logging.getLogger(__name__)


<<<<<<< HEAD
async def api_view_blog_post(request: ApiViewBlogPostRequest) -> BlogModel:
=======
async def api_view_blog_post(request: BlogID) -> BlogModel:
>>>>>>> main

    if not request.blog_id:
        raise HTTPException(status_code=400, detail="blogID is required")

    _db_gen = get_db()
    db = next(_db_gen)
    try:
        blog = Blog.get_by_id(db, int(request.blog_id))
        if not blog:
            raise HTTPException(status_code=404, detail="Blog not found")

        raw_comments = BlogComment.list_by_blog_id(db, blog.blog_id)
        comment_items = [
            {
                "commentID": str(c.comment_id),
                "commentText": c.content,
                "userID": str(c.user_id),
                "time": c.created_at.isoformat() if c.created_at else "",
            }
            for c in raw_comments
        ]

        return BlogModel(
            blogID=str(blog.blog_id),
            title=blog.title,
            imageURLList=blog.image_urls or [],
            content=blog.content or "",
            commentList=comment_items,
            commentNumber=blog.comment_count or 0,
            likeNumber=blog.like_count or 0,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to view blog: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve blog")
    finally:
        try:
            next(_db_gen)
        except StopIteration:
<<<<<<< HEAD
            pass
=======
            pass
>>>>>>> main
