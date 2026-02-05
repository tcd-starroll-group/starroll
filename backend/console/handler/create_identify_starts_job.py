from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Response,
    Security,
    status,
)
from openapi_server.models.api_create_identify_stars_job_post200_response import ApiCreateIdentifyStarsJobPost200Response
from openapi_server.models.user_credentials import UserCredentials

from openapi_server.apis.default_api_base import BaseDefaultApi

from openapi_server.models.extra_models import TokenModel  # noqa: F401
from pydantic import Field, StrictBytes, StrictStr
from typing import Any, Optional, Tuple, Union
from typing_extensions import Annotated

async def api_create_identify_stars_job_post(
    image: Annotated[Union[StrictBytes, StrictStr, Tuple[StrictStr, StrictBytes]], Field(description="Image file to identify stars (JPEG, PNG, etc.)")] = Form(None, description="Image file to identify stars (JPEG, PNG, etc.)"),
    user_credentials: Optional[UserCredentials] = Form(None, description=""),
) -> ApiCreateIdentifyStarsJobPost200Response:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().api_create_identify_stars_job_post(image, user_credentials)

