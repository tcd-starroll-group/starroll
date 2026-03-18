import asyncio

import pytest
from fastapi import HTTPException

from backend.console.handler import list_identify_stars_jobs as list_jobs_module
from openapi_server.models.pagination_query import PaginationQuery


def test_list_identify_stars_jobs_unsupported_sort_returns_400(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(list_jobs_module, "get_current_user_id", lambda: 1)

    payload = PaginationQuery(
        limit=10, offset=0, sort="bad_field", order="desc")
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(list_jobs_module.api_list_identify_stars_jobs_post(payload))

    assert exc_info.value.status_code == 400
