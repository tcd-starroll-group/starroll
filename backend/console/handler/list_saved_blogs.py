import logging
from fastapi import HTTPException
from gen.py.src.openapi_server.models.api_get_saved_blogs_post_request import ApiGetSavedBlogsPostRequest
from gen.py.src.openapi_server.models.api_get_saved_blogs_post200_response import ApiGetSavedBlogsPost200Response
from gen.py.src.openapi_server.models.blog_preview import BlogPreview
from backend.console.dal.rds.blog import Blog
from backend.console.dal.rds.blog_interactions import BlogSave
from backend.console.dal.rds.client import get_db
import backend.console.utils.auth as auth_module

logger = logging.getLogger(__name__)


async def api_list_saved_blogs_post(request: ApiGetSavedBlogsPostRequest) -> ApiGetSavedBlogsPost200Response:
    if not request.user_credentials:
        raise HTTPException(status_code=400, detail="userCredentials is required")


    user_id = request.user_credentials.user_id
    token = request.user_credentials.token
    auth_module.verify_user_id_and_token(token, user_id)

    _db_gen = get_db()
    db = next(_db_gen)
    try:
        blog_ids = BlogSave.list_blog_ids_by_user(db, int(user_id))
        result = []
        for bid in blog_ids:
            blog = Blog.get_by_id(db, bid)
            if blog:
                preview = BlogPreview(
                    blogID=str(blog.blog_id),
                    title=blog.title,
                    imageURL=(blog.image_urls[0] if blog.image_urls else ""),
                )
                result.append(preview.model_dump(by_alias=True))

        logger.info(f"listSavedBlogs: user_id={user_id} count={len(result)}")
        return ApiGetSavedBlogsPost200Response(blogsList=result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list saved blogs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to list saved blogs")
    finally:
        try:
            next(_db_gen)
        except StopIteration:
            pass
# Alias for compatibility with starroll_impl.py import
api_get_saved_blogs_post = api_list_saved_blogs_post