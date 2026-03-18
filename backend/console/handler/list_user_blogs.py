import logging
from typing import Any, Dict, Optional
from fastapi import HTTPException
from openapi_server.models.blogs_list import BlogsList
from openapi_server.models.blog_preview import BlogPreview
from backend.console.dal.rds.blog import Blog
from backend.console.dal.rds.client import db_context
import backend.console.utils.auth as auth_module
from backend.constant.sort import SORT_BY_CREATE_TIME, SORT_ORDER_DESC

logger = logging.getLogger(__name__)
SUPPORTED_SORT_FIELDS = {SORT_BY_CREATE_TIME, "createTime",
                         "createdAt", "created_at", "likeNumber", "commentNumber"}


async def api_list_user_blogs_post(body: Optional[Dict[str, Any]]) -> BlogsList:
    """List all blogs posted by the authenticated user"""
    user_id = auth_module.get_current_user_id()
    payload = body or {}

    sort = payload.get("sort")
    if sort and sort not in SUPPORTED_SORT_FIELDS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported sort field: {sort}. "
                f"Supported fields: {', '.join(sorted(SUPPORTED_SORT_FIELDS))}"
            ),
        )

    limit = payload.get("limit", 20)
    offset = payload.get("offset", 0)
    sort = sort if sort is not None else SORT_BY_CREATE_TIME
    order = payload.get("order", SORT_ORDER_DESC)

    with db_context() as db:
        blogs = Blog.list_by_user_id(
            db,
            int(user_id),
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
            f"Listed {len(previews)} blogs for user_id={user_id}, "
            f"limit={limit}, offset={offset}, sort={sort}, order={order}"
        )
        return BlogsList(blogsList=[p.model_dump(by_alias=True) for p in previews])
