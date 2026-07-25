"""Test configuration.

Per docs/product/03-technical-specifications.md §9: integration tests run against a real
Postgres instance with RLS enabled — never a mocked database — because RLS enforcement is
precisely the behavior that matters most to get right, and a mock can't tell you whether a real
policy is missing or misconfigured.
"""

import os
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
os.environ.setdefault("JWT_PRIVATE_KEY_PATH", str(_REPO_ROOT / "secrets" / "jwt_private_key.pem"))
os.environ.setdefault("JWT_PUBLIC_KEY_PATH", str(_REPO_ROOT / "secrets" / "jwt_public_key.pem"))
os.environ.setdefault(
    "DATABASE_URL", "postgresql+asyncpg://pluto_app:pluto_app_dev_password@localhost:5432/pluto_ai_dev"
)
os.environ.setdefault(
    "MIGRATION_DATABASE_URL", "postgresql+psycopg://macbookpro@localhost:5432/pluto_ai_dev"
)
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/1")

import psycopg  # noqa: E402
import pytest_asyncio  # noqa: E402
from app.config import get_settings  # noqa: E402
from app.main import app  # noqa: E402
from app.security.rate_limit import close_redis, init_redis  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402
from pluto_core.db.base import dispose_engine, init_engine  # noqa: E402

_ADMIN_DATABASE_URL = "postgresql://macbookpro@localhost:5432/pluto_ai_dev"


@pytest_asyncio.fixture(autouse=True)
async def _service_lifecycle():
    """Function-scoped, not session-scoped: pytest-asyncio gives each test function its own
    event loop by default, and an asyncpg connection pool is bound to the loop it was created on
    — a session-scoped engine would be handed to a different loop on the second test and fail
    with exactly the confusing "attached to a different loop" error this avoids.
    """
    settings = get_settings()
    init_engine(str(settings.database_url))
    init_redis(str(settings.redis_url))
    yield
    await close_redis()
    await dispose_engine()


@pytest_asyncio.fixture(autouse=True)
async def _clean_database(_service_lifecycle):
    """Runs before every test, and explicitly depends on `_service_lifecycle` so the engine/redis
    client it needs are guaranteed to exist first — two same-scoped autouse fixtures have no
    ordering guarantee otherwise. Uses a direct connection as the migration/owner role — the only
    role that bypasses RLS by default — since cleanup must see and remove rows across every
    tenant, which `pluto_app` (by design) cannot do without a tenant context.
    """
    with psycopg.connect(_ADMIN_DATABASE_URL, autocommit=True) as conn, conn.cursor() as cur:
        cur.execute("TRUNCATE businesses, agencies, platform_users RESTART IDENTITY CASCADE;")
    # Redis rate-limit counters would otherwise leak between tests and cause spurious 429s.
    from app.security.rate_limit import get_redis

    await get_redis().flushdb()
    yield


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver/v1") as ac:
        yield ac
