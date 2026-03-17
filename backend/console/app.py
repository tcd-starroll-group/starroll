"""
Application entrypoint wrapper.

Owns the FastAPI app instance so that lifecycle hooks (lifespan) can be
added without touching the auto-generated openapi_server package.
"""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

import backend.console.dal as _dal
from gen.py.src.openapi_server.apis.chat_api import router as ChatApiRouter
from gen.py.src.openapi_server.apis.default_api import router as DefaultApiRouter


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

app.include_router(DefaultApiRouter)
app.include_router(ChatApiRouter)
