"""Shared FastAPI dependencies: tenant resolution from the JWT, the RLS-aware DB session, and
role-based access control. Every protected route depends on `get_current_tenant_context`
(directly or transitively via `get_db`) — there is no route that can obtain a database session
without a resolved tenant context, per docs/architecture/04-security-and-compliance.md §3.
"""

from collections.abc import AsyncGenerator, Callable

from fastapi import Depends, Request
from pluto_core.db.base import TenantContext, get_session, set_tenant_context
from pluto_core.security.jwt import TokenError, decode_access_token
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_jwt_keys, get_settings
from app.errors import ForbiddenError, UnauthorizedError


async def get_current_tenant_context(request: Request) -> TenantContext:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise UnauthorizedError("Missing or malformed Authorization header")

    token = auth_header.removeprefix("Bearer ").strip()
    _, public_key = get_jwt_keys()
    settings = get_settings()

    try:
        claims = decode_access_token(token, public_key=public_key, issuer=settings.jwt_issuer)
    except TokenError as exc:
        raise UnauthorizedError("Invalid or expired access token") from exc

    ctx = TenantContext(business_id=claims.business_id, user_id=claims.user_id, role=claims.role)
    set_tenant_context(ctx)
    return ctx


async def get_db(
    _ctx: TenantContext = Depends(get_current_tenant_context),
) -> AsyncGenerator[AsyncSession, None]:
    """Depends on `get_current_tenant_context` explicitly (not just relying on import order) so
    FastAPI always resolves the tenant context — and therefore sets the RLS session variable —
    before any query runs on this session.
    """
    async for session in get_session():
        yield session


def require_role(*allowed_roles: str) -> Callable[[TenantContext], TenantContext]:
    """Usage: `Depends(require_role("owner", "admin"))` — per the RBAC matrix in
    docs/architecture/04-security-and-compliance.md §2.
    """

    def _check(ctx: TenantContext = Depends(get_current_tenant_context)) -> TenantContext:
        if ctx.role not in allowed_roles:
            raise ForbiddenError(f"Role '{ctx.role}' cannot perform this action")
        return ctx

    return _check
