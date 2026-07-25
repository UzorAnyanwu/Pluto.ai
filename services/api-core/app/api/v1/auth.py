"""Auth endpoints — see docs/api/openapi.yaml's `Auth` tag for the contract and
docs/architecture/04-security-and-compliance.md §1 for the design rationale (refresh rotation +
reuse detection, RS256 access tokens, argon2 password hashing).
"""

import re
import uuid
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Request, Response
from pluto_core.db.base import TenantContext, session_scope, set_tenant_context
from pluto_core.db.enums import BusinessRole, BusinessStatus
from pluto_core.db.models.tenancy import Business, RefreshToken, User
from pluto_core.db.uuid7 import uuid7
from pluto_core.security.jwt import create_access_token
from pluto_core.security.passwords import hash_password, verify_password
from pluto_core.security.refresh_tokens import generate_refresh_token, hash_refresh_token
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import ApiCoreSettings, get_jwt_keys, get_settings
from app.errors import ConflictError, UnauthorizedError
from app.schemas.auth import AuthTokenPair, LoginRequest, RegisterRequest, UserSummary
from app.security.rate_limit import enforce_rate_limit

router = APIRouter(prefix="/auth", tags=["Auth"])

REFRESH_COOKIE_NAME = "pluto_refresh_token"
_SLUG_INVALID_CHARS = re.compile(r"[^a-z0-9]+")


def _slugify(name: str, *, uniqueness_suffix: str) -> str:
    base = _SLUG_INVALID_CHARS.sub("-", name.lower()).strip("-")[:80] or "business"
    return f"{base}-{uniqueness_suffix}"


def _set_refresh_cookie(response: Response, raw_token: str, settings: ApiCoreSettings) -> None:
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=raw_token,
        max_age=settings.refresh_token_ttl_seconds,
        httponly=True,
        secure=settings.environment != "development",
        samesite="strict",
        path="/v1/auth",
    )


async def _issue_token_pair(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    business_id: uuid.UUID,
    email: str,
    role: str,
    request: Request,
    settings: ApiCoreSettings,
    replaces_token_id: uuid.UUID | None = None,
) -> tuple[AuthTokenPair, str]:
    private_key, _ = get_jwt_keys()
    access_token = create_access_token(
        user_id=user_id,
        business_id=business_id,
        role=role,
        private_key=private_key,
        issuer=settings.jwt_issuer,
        ttl_seconds=settings.access_token_ttl_seconds,
    )

    raw_refresh = generate_refresh_token()
    refresh_row = RefreshToken(
        id=uuid7(),
        user_id=user_id,
        business_id=business_id,
        token_hash=hash_refresh_token(raw_refresh),
        expires_at=datetime.now(UTC) + timedelta(seconds=settings.refresh_token_ttl_seconds),
        user_agent=request.headers.get("User-Agent"),
        ip_address=request.client.host if request.client else None,
    )
    session.add(refresh_row)

    if replaces_token_id is not None:
        # Flush the INSERT of the new row before the UPDATE below references its id as a
        # foreign key — without this, SQLAlchemy has no reason to order the two statements
        # correctly (nothing models `replaced_by_id` as an ORM relationship) and can emit the
        # UPDATE first, which Postgres rejects since the row it points at doesn't exist yet.
        await session.flush()
        old = await session.get(RefreshToken, replaces_token_id)
        if old is not None:
            old.revoked_at = datetime.now(UTC)
            old.replaced_by_id = refresh_row.id

    await session.commit()

    pair = AuthTokenPair(
        access_token=access_token,
        expires_in=settings.access_token_ttl_seconds,
        user=UserSummary(id=user_id, email=email, role=role, business_id=business_id),
    )
    return pair, raw_refresh


@router.post("/register", status_code=201)
async def register(payload: RegisterRequest, request: Request, response: Response) -> AuthTokenPair:
    settings = get_settings()
    client_ip = request.client.host if request.client else "unknown"
    await enforce_rate_limit(f"register:{client_ip}", limit=5, window_seconds=3600)

    async with session_scope(None) as probe:
        existing = await probe.execute(
            text("SELECT 1 FROM auth_resolve_business_by_email(:email)"), {"email": payload.email}
        )
        if existing.first() is not None:
            raise ConflictError("An account with this email already exists")

    business_id = uuid7()
    user_id = uuid7()
    ctx = TenantContext(business_id=business_id, user_id=user_id, role=BusinessRole.owner.value)

    async with session_scope(ctx) as session:
        business = Business(
            id=business_id,
            name=payload.business_name,
            # The *trailing* hex characters, not the leading ones: a UUIDv7's leading bits are
            # timestamp-derived (that's the whole point of it — see pluto_core/db/uuid7.py), so
            # two registrations milliseconds apart would otherwise get near-identical prefixes
            # and collide on the slug's uniqueness constraint. The trailing characters come from
            # the random tail and don't have this problem.
            slug=_slugify(payload.business_name, uniqueness_suffix=str(business_id).replace("-", "")[-8:]),
            timezone=payload.timezone,
            status=BusinessStatus.trial,
        )
        user = User(
            id=user_id,
            business_id=business_id,
            email=payload.email,
            hashed_password=hash_password(payload.password),
            role=BusinessRole.owner,
            accepted_at=datetime.now(UTC),
        )
        session.add_all([business, user])
        await session.flush()

        pair, raw_refresh = await _issue_token_pair(
            session,
            user_id=user_id,
            business_id=business_id,
            email=payload.email,
            role=BusinessRole.owner.value,
            request=request,
            settings=settings,
        )

    _set_refresh_cookie(response, raw_refresh, settings)
    return pair


@router.post("/login")
async def login(payload: LoginRequest, request: Request, response: Response) -> AuthTokenPair:
    settings = get_settings()
    client_ip = request.client.host if request.client else "unknown"
    await enforce_rate_limit(f"login:{client_ip}", limit=10, window_seconds=300)
    await enforce_rate_limit(f"login-email:{payload.email}", limit=10, window_seconds=900)

    async with session_scope(None) as session:
        result = await session.execute(
            text("SELECT business_id, user_id, hashed_password, role FROM auth_resolve_business_by_email(:email)"),
            {"email": payload.email},
        )
        row = result.first()

        # Constant-shape response whether the email exists or not — verifying against a dummy
        # hash when it doesn't keeps timing similar and, more importantly, keeps the error
        # message identical, so this endpoint never reveals whether an email is registered.
        if row is None or not verify_password(payload.password, row.hashed_password):
            raise UnauthorizedError("Invalid email or password")

        pair, raw_refresh = await _issue_token_pair(
            session,
            user_id=row.user_id,
            business_id=row.business_id,
            email=payload.email,
            role=row.role,
            request=request,
            settings=settings,
        )

    _set_refresh_cookie(response, raw_refresh, settings)
    return pair


@router.post("/refresh")
async def refresh(request: Request, response: Response) -> AuthTokenPair:
    settings = get_settings()
    raw_token = request.cookies.get(REFRESH_COOKIE_NAME)
    if not raw_token:
        raise UnauthorizedError("Missing refresh token")

    token_hash = hash_refresh_token(raw_token)

    async with session_scope(None) as session:
        result = await session.execute(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
        stored = result.scalar_one_or_none()

        if stored is None:
            raise UnauthorizedError("Invalid refresh token")

        if stored.revoked_at is not None:
            # Reuse of an already-rotated token: a strong signal the token was stolen. Revoke
            # every active refresh token for this user and force a full re-login — see
            # docs/architecture/04-security-and-compliance.md §1.
            now = datetime.now(UTC)
            active_tokens = (
                await session.execute(
                    select(RefreshToken).where(
                        RefreshToken.user_id == stored.user_id, RefreshToken.revoked_at.is_(None)
                    )
                )
            ).scalars()
            for token_row in active_tokens:
                token_row.revoked_at = now
            await session.commit()
            raise UnauthorizedError("Refresh token has already been used — please log in again")

        if stored.expires_at < datetime.now(UTC):
            raise UnauthorizedError("Refresh token has expired")

        # We don't yet know the user's *current* role (the refresh token row doesn't store it —
        # roles can change between issuance and refresh), so resolve it fresh via `users` before
        # minting a new access token, once we have enough to set the RLS tenant context.
        set_tenant_context(TenantContext(business_id=stored.business_id, user_id=stored.user_id, role=""))
        await session.execute(
            text("SELECT set_config('app.current_tenant', :tid, true)"), {"tid": str(stored.business_id)}
        )
        user = await session.get(User, stored.user_id)
        if user is None or user.deleted_at is not None:
            raise UnauthorizedError("Account no longer exists")

        pair, raw_new_refresh = await _issue_token_pair(
            session,
            user_id=user.id,
            business_id=user.business_id,
            email=user.email,
            role=user.role.value,
            request=request,
            settings=settings,
            replaces_token_id=stored.id,
        )

    _set_refresh_cookie(response, raw_new_refresh, settings)
    return pair


@router.post("/logout", status_code=204)
async def logout(request: Request, response: Response) -> None:
    raw_token = request.cookies.get(REFRESH_COOKIE_NAME)
    if raw_token:
        token_hash = hash_refresh_token(raw_token)
        async with session_scope(None) as session:
            result = await session.execute(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
            stored = result.scalar_one_or_none()
            if stored is not None and stored.revoked_at is None:
                stored.revoked_at = datetime.now(UTC)
                await session.commit()

    response.delete_cookie(REFRESH_COOKIE_NAME, path="/v1/auth")
