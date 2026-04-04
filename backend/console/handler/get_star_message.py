import logging

from fastapi import HTTPException

from openapi_server.models.star_message import StarMessage
from openapi_server.models.common_id import CommonID
from backend.console.dal.rds.star_messages import StarMessage as StarMessageDAL
from backend.console.dal.rds.client import db_context

logger = logging.getLogger(__name__)


async def api_get_star_message_post(common_id: CommonID) -> StarMessage:
    if not common_id.id:
        raise HTTPException(status_code=400, detail="id is required")

    with db_context() as db:
        record = StarMessageDAL.get_by_message_id(
            db=db, message_id=common_id.id)
        if not record:
            raise HTTPException(
                status_code=404, detail="Star message not found")

        return StarMessage(
            hip=record.hip,
            var_from=record.from_,
            message=record.message,
        )
