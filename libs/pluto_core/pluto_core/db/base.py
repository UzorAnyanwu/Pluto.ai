"""Declarative base, mixins, and session/engine wiring shared by every service that talks to
Postgres. See docs/architecture/02-data-model.md for the reasoning behind each mixin.
"""

import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import DateTime, Integer, func, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column

from pluto_core.db.uuid7 import uuid7


class Base(DeclarativeBase):
    """Declarative base for every ORM model across every service. A single shared `Base` means
    Alembic's autogenerate sees the full schema regardless of which service's code imported which
    model module — see libs/pluto_core/migrations/env.py.
    """


class UUIDPKMixin:
    """UUIDv7 primary key, generated application-side (not `gen_random_uuid()`), per Decision 4
    in the system architecture doc.
    """

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid7)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class SoftDeleteMixin:
    """`deleted_at IS NULL` is the default filter everywhere — see data model doc §4. Hard deletes
    only happen via the explicit GDPR-erasure job, never through this column.
    """

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )


class VersionedMixin:
    """Optimistic concurrency column. Enforcement (`UPDATE ... WHERE version = :expected`, bump
    on success) lives in the repository layer, not as a SQLAlchemy `version_id_col` mapper
    argument — that keeps mixin composition simple across the models module and matches the
    explicit conflict-response contract in docs/product/03-technical-specifications.md.
    """

    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


class TenantScopedMixin:
    """Every tenant-owned table gets a `business_id` foreign key. This column, combined with the
    Postgres RLS policy created in the same migration as the table (see migrations/versions/), is
    what makes cross-tenant data leakage impossible even if application code forgets a filter —
    see docs/architecture/04-security-and-compliance.md §3.
    """

    @declared_attr
    def business_id(cls) -> Mapped[uuid.UUID]:
        from sqlalchemy import ForeignKey

        return mapped_column(ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True)


# --------------------------------------------------------------------------------------------
# Tenant context propagation
#
# A request-scoped TenantContext is resolved once (from the JWT, per
# docs/architecture/04-security-and-compliance.md §3) and carried through a contextvar so that
# `get_session()` can issue `SET LOCAL app.current_tenant` at the start of every transaction
# without every call site having to thread it through manually. This is what RLS policies check
# against (`current_setting('app.current_tenant', true)`).
# --------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class TenantContext:
    business_id: uuid.UUID
    user_id: uuid.UUID
    role: str


_tenant_context: ContextVar[TenantContext | None] = ContextVar("_tenant_context", default=None)


def set_tenant_context(ctx: TenantContext | None) -> None:
    _tenant_context.set(ctx)


def get_tenant_context() -> TenantContext | None:
    return _tenant_context.get()


_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def init_engine(database_url: str, *, echo: bool = False) -> AsyncEngine:
    """Called once at service startup. Kept separate from module import time so tests can point
    at a different database without reloading the module.
    """
    global _engine, _session_factory
    _engine = create_async_engine(database_url, echo=echo, pool_pre_ping=True, pool_size=10, max_overflow=20)
    _session_factory = async_sessionmaker(_engine, expire_on_commit=False)
    return _engine


async def dispose_engine() -> None:
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
    _engine = None
    _session_factory = None


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Yields a session with the current TenantContext's business_id already applied as the RLS
    session variable for this transaction. Platform-level operations (no tenant context — e.g. a
    platform_admin listing all businesses) leave `app.current_tenant` unset, which RLS policies
    treat as "no rows visible" by design (see migrations for the exact policy), so cross-tenant
    reads must go through an explicit platform-scoped code path, never accidentally through the
    tenant-scoped one.
    """
    if _session_factory is None:
        raise RuntimeError("Database engine not initialized — call init_engine() at service startup.")

    session = _session_factory()
    try:
        ctx = get_tenant_context()
        if ctx is not None:
            await session.execute(
                text("SELECT set_config('app.current_tenant', :tenant_id, true)"),
                {"tenant_id": str(ctx.business_id)},
            )
        yield session
    finally:
        await session.close()


@asynccontextmanager
async def session_scope(ctx: TenantContext | None) -> AsyncGenerator[AsyncSession, None]:
    """For the narrow set of call sites that can't rely on the ambient request-scoped
    TenantContext because they run *before* one exists — registration (which mints a brand new
    business_id, then must scope its own inserts to it) and login (which has no tenant context at
    all until the credential lookup resolves one). See app/api/v1/auth.py for both uses.

    Every other code path should use the `get_session` FastAPI dependency instead, which reads
    the contextvar populated by the authentication middleware.
    """
    token = _tenant_context.set(ctx)
    try:
        async for session in get_session():
            yield session
    finally:
        _tenant_context.reset(token)
