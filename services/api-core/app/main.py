"""FastAPI application factory for `api-core`. See
docs/architecture/01-system-architecture.md §3 for why this is a modular monolith and what is
and isn't allowed to live in it.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pluto_core.db.base import dispose_engine, init_engine

from app.api.v1.router import api_v1_router
from app.config import get_settings
from app.errors import RequestIdMiddleware, register_exception_handlers
from app.security.rate_limit import close_redis, init_redis


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    init_engine(str(settings.database_url))
    init_redis(str(settings.redis_url))
    yield
    await close_redis()
    await dispose_engine()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Pluto AI — Core API",
        version="1.0.0-mvp",
        lifespan=lifespan,
    )
    app.add_middleware(RequestIdMiddleware)
    register_exception_handlers(app)
    app.include_router(api_v1_router)
    return app


app = create_app()
