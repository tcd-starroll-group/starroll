import logging
from fastapi import HTTPException
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

        logger.info(
            f"listSavedBlogs: user_id={user_id} count={len(result)} "
            f"limit={limit}, offset={offset}, sort={sort}, order={order}"
        )
        return BlogsList(blogsList=result)
