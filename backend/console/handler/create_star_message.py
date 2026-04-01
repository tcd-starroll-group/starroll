import logging

from fastapi import HTTPException

from openapi_server.models.star_message import StarMessage
from openapi_server.models.common_id import CommonID
from backend.console.dal.rds.star_messages import StarMessage as StarMessageDAL
from backend.console.dal.rds.client import db_context
from backend.console.utils.auth import get_current_user_id

logger = logging.getLogger(__name__)


async def api_create_star_message_post(star_message: StarMessage) -> CommonID:
    if not star_message.hip:
        raise HTTPException(status_code=400, detail="hip is required")
    if not star_message.var_from:
        raise HTTPException(status_code=400, detail="from is required")
    if not star_message.message:
        raise HTTPException(status_code=400, detail="message is required")

    user_id = get_current_user_id()

    with db_context() as db:
        record = StarMessageDAL.create(
            db=db,
            user_id=int(user_id),
            hip=star_message.hip,
            from_=star_message.var_from,
            message=star_message.message,
        )
        logger.info(
            f"StarMessage created: message_id={record.message_id} user_id={user_id} HIP={record.hip}")
        return CommonID(id=record.message_id)
