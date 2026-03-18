import logging
from fastapi import HTTPException
from openapi_server.models.api_list_star_blogs_post_request import ApiListStarBlogsPostRequest
from openapi_server.models.blogs_list import BlogsList
from openapi_server.models.blog_preview import BlogPreview
from backend.console.dal.rds.blog import Blog
from backend.console.dal.rds.client import db_context
from backend.constant.sort import SORT_BY_CREATE_TIME, SORT_ORDER_DESC

logger = logging.getLogger(__name__)
SUPPORTED_SORT_FIELDS = {SORT_BY_CREATE_TIME, "createTime",
                         "createdAt", "created_at", "likeNumber", "commentNumber"}


async def api_list_star_blogs_post(request: ApiListStarBlogsPostRequest) -> BlogsList:
    if not request.hip:
        raise HTTPException(status_code=400, detail="HIP is required")

    if request.sort and request.sort not in SUPPORTED_SORT_FIELDS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported sort field: {request.sort}. "
                f"Supported fields: {', '.join(sorted(SUPPORTED_SORT_FIELDS))}"
            ),
        )

    limit = request.limit if request.limit is not None else 20
    offset = request.offset if request.offset is not None else 0
    sort = request.sort if request.sort is not None else SORT_BY_CREATE_TIME
    order = request.order if request.order is not None else SORT_ORDER_DESC

    with db_context() as db:
        blogs = Blog.list_by_hip(
            db,
            int(request.hip),
            limit=limit,
            offset=offset,
            sort=sort,
            order=order,
        )
        previews = [
            BlogPreview(
                blogID=str(b.blog_id),
                title=b.title,
                imageURL=(b.image_urls[0] if b.image_urls else ""),
            )
            for b in blogs
        ]
        logger.info(
            f"Listed {len(previews)} blogs for HIP={request.hip}, "
            f"limit={limit}, offset={offset}, sort={sort}, order={order}"
        )
        return BlogsList(blogsList=[p.model_dump(by_alias=True) for p in previews])
