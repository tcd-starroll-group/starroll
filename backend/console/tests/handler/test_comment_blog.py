import asyncio
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from backend.console.handler import comment_blog as comment_blog_module


def test_comment_blog_missing_comment_text_raises_400():
    payload = SimpleNamespace(blog_id="1", comment_text="")
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(comment_blog_module.api_comment_blog_post(payload))

    assert exc_info.value.status_code == 400
    assert "commentText" in exc_info.value.detail
