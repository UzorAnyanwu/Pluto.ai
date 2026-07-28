"""Business-issued API keys for external integrations. See the `API Keys` tag in
docs/api/openapi.yaml. Revocation sets `revoked_at` rather than deleting the row (the model has
no soft-delete mixin for this table — `revoked_at` *is* its deletion state, kept so `last_used_at`
history survives revocation for audit purposes).
"""

import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from pluto_core.db.base import TenantContext
from pluto_core.db.models.platform import ApiKey
from pluto_core.db.uuid7 import uuid7
from pluto_core.security.secrets import generate_secret, hash_secret
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_tenant_context, get_db, require_role
from app.errors import NotFoundError
from app.schemas.api_key import ApiKeyCreateRequest, ApiKeyResponse, ApiKeyWithSecretResponse

router = APIRouter(prefix="/businesses/me/api-keys", tags=["API Keys"])

_KEY_PREFIX = "plt_"


def _to_response(api_key: ApiKey) -> ApiKeyResponse:
    return ApiKeyResponse(
        id=api_key.id,
        name=api_key.name,
        prefix=api_key.prefix,
        scopes=api_key.scopes,
        last_used_at=api_key.last_used_at,
        created_at=api_key.created_at,
    )


@router.get("", response_model=list[ApiKeyResponse])
async def list_api_keys(
    ctx: TenantContext = Depends(get_current_tenant_context),
    db: AsyncSession = Depends(get_db),
) -> list[ApiKeyResponse]:
    result = await db.execute(
        select(ApiKey).where(ApiKey.business_id == ctx.business_id, ApiKey.revoked_at.is_(None))
    )
    return [_to_response(k) for k in result.scalars().all()]


@router.post("", status_code=201, response_model=ApiKeyWithSecretResponse)
async def create_api_key(
    payload: ApiKeyCreateRequest,
    ctx: TenantContext = Depends(require_role("owner", "admin")),
    db: AsyncSession = Depends(get_db),
) -> ApiKeyWithSecretResponse:
    raw_key = generate_secret(prefix=_KEY_PREFIX)
    api_key = ApiKey(
        id=uuid7(),
        business_id=ctx.business_id,
        name=payload.name,
        prefix=raw_key[:8],
        hashed_key=hash_secret(raw_key),
        scopes=payload.scopes,
    )
    db.add(api_key)
    await db.commit()

    return ApiKeyWithSecretResponse(**_to_response(api_key).model_dump(), secret=raw_key)


@router.delete("/{key_id}", status_code=204)
async def revoke_api_key(
    key_id: uuid.UUID,
    ctx: TenantContext = Depends(require_role("owner", "admin")),
    db: AsyncSession = Depends(get_db),
) -> None:
    result = await db.execute(
        select(ApiKey).where(
            ApiKey.id == key_id, ApiKey.business_id == ctx.business_id, ApiKey.revoked_at.is_(None)
        )
    )
    api_key = result.scalar_one_or_none()
    if api_key is None:
        raise NotFoundError("API key not found")

    api_key.revoked_at = datetime.now(UTC)
    await db.commit()
