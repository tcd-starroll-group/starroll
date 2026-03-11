import logging
from fastapi import HTTPException
from gen.py.src.openapi_server.models.api_list_blogs_post_request import ApiListBlogsPostRequest
from gen.py.src.openapi_server.models.api_list_blogs_post200_response import ApiListBlogsPost200Response
from gen.py.src.openapi_server.models.blog_preview import BlogPreview
from backend.console.dal.rds.blog import Blog
from backend.console.dal.rds.client import get_db

logger = logging.getLogger(__name__)


async def api_list_star_blogs_post(request: ApiListBlogsPostRequest) -> ApiListBlogsPost200Response:
    if not request.hip:
        raise HTTPException(status_code=400, detail="HIP is required")

    _db_gen = get_db()
    db = next(_db_gen)
    try:
        blogs = Blog.list_by_hip(db, int(request.hip))
        previews = [
            BlogPreview(
                blogID=str(b.blog_id),
                title=b.title,
                imageURL=(b.image_urls[0] if b.image_urls else ""),
            )
            for b in blogs
        ]
        logger.info(f"Listed {len(previews)} blogs for HIP={request.hip}")
        return ApiListBlogsPost200Response(blogsList=[p.model_dump(by_alias=True) for p in previews])
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list blogs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to list blogs")
    finally:
        try:
            next(_db_gen)
        except StopIteration:
            pass