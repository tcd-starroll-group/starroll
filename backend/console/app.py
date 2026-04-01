"""
Application entrypoint wrapper.

Owns the FastAPI app instance so that lifecycle hooks (lifespan) can be
added without touching the auto-generated openapi_server package.
"""
from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
import backend.console.dal as _dal
from backend.console.utils.auth import (
    reset_current_token_payload,
    set_current_token_payload,
    verify_access_token,
)
from openapi_server.apis.chat_api import router as ChatApiRouter
from openapi_server.apis.default_api import router as DefaultApiRouter


logger = logging.getLogger(__name__)

AUTH_ACTION_WHITELIST = {
    "userLogin",
    "userReg",
    "usernameVerify",
    "resetPassword",
    "resetPasswordSendCode",
    "getStarMessage",
    "health",
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    # Flush the Kafka producer's internal buffer before the process exits.
    # Without this, buffered messages are silently dropped on shutdown.
    # KafkaClient.close() calls producer.flush(timeout=10) then cleans up.
    if _dal._kafka_client is not None:
        await asyncio.to_thread(_dal._kafka_client.close)


app = FastAPI(
    title="StarRoll API",
    description="star roll backend console",
    version="1.0.0",
    lifespan=lifespan,
)
Instrumentator().instrument(app).expose(app)


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if request.method == "OPTIONS":
        return await call_next(request)

    if not request.url.path.startswith("/api/"):
        return await call_next(request)

    action = request.url.path.removeprefix("/api/").split("/")[0]
    if action in AUTH_ACTION_WHITELIST:
        return await call_next(request)

    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return JSONResponse(status_code=401, content={"detail": "Authorization header required"})

    if auth_header.startswith("Bearer "):
        token = auth_header[len("Bearer "):].strip()
    else:
        token = auth_header.strip()

    if not token:
        return JSONResponse(status_code=401, content={"detail": "Invalid Authorization header"})

    payload, is_valid = verify_access_token(token)
    if not is_valid or payload is None:
        return JSONResponse(status_code=401, content={"detail": "Invalid or expired token"})

    context_token = set_current_token_payload(payload)
    try:
        return await call_next(request)
    finally:
        reset_current_token_payload(context_token)

app.include_router(DefaultApiRouter)
app.include_router(ChatApiRouter)
