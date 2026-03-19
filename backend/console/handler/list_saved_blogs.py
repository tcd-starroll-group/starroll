import logging
from fastapi import HTTPException
<<<<<<< HEAD
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
=======
from openapi_server.models.pagination_query import PaginationQuery
from openapi_server.models.blogs_list import BlogsList
from openapi_server.models.blog_preview import BlogPreview
from backend.console.dal.rds.blog import Blog
from backend.console.dal.rds.blog_interactions import BlogSave
from backend.console.dal.rds.client import db_context
import backend.console.utils.auth as auth_module
from backend.constant.sort import SORT_BY_CREATE_TIME, SORT_ORDER_DESC

logger = logging.getLogger(__name__)
SUPPORTED_SORT_FIELDS = {SORT_BY_CREATE_TIME,
                         "createTime", "createdAt", "created_at"}


async def api_list_saved_blogs_post(request: PaginationQuery) -> BlogsList:
    user_id = auth_module.get_current_user_id()

    sort = request.sort
    if sort and sort not in SUPPORTED_SORT_FIELDS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported sort field: {sort}. "
                f"Supported fields: {', '.join(sorted(SUPPORTED_SORT_FIELDS))}"
            ),
        )

    limit = request.limit if request.limit is not None else 20
    offset = request.offset if request.offset is not None else 0
    sort = sort if sort is not None else SORT_BY_CREATE_TIME
    order = request.order if request.order is not None else SORT_ORDER_DESC

    with db_context() as db:
        blog_ids = BlogSave.list_blog_ids_by_user(
            db,
            int(user_id),
            limit=limit,
            offset=offset,
            sort=sort,
            order=order,
        )
>>>>>>> main
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

<<<<<<< HEAD
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
=======
        logger.info(
            f"listSavedBlogs: user_id={user_id} count={len(result)} "
            f"limit={limit}, offset={offset}, sort={sort}, order={order}"
        )
        return BlogsList(blogsList=result)
>>>>>>> main
