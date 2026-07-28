"""Outbound webhooks. See the `Webhooks` tag in docs/api/openapi.yaml and
docs/product/03-technical-specifications.md §7 for the delivery/signing contract this table
supports — actual delivery (the background job that POSTs to `target_url` on a domain event) is
part of `services/workers`, not built yet; this module only owns the CRUD for registering them.
"""

import uuid

from fastapi import APIRouter, Depends
from pluto_core.db.base import TenantContext
from pluto_core.db.models.platform import Webhook
from pluto_core.db.uuid7 import uuid7
from pluto_core.security.secrets import generate_secret, hash_secret
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_tenant_context, get_db, require_role
from app.errors import NotFoundError
from app.schemas.webhook import WebhookCreateRequest, WebhookResponse, WebhookWithSecretResponse

router = APIRouter(prefix="/businesses/me/webhooks", tags=["Webhooks"])


def _to_response(webhook: Webhook) -> WebhookResponse:
    return WebhookResponse(
        id=webhook.id,
        target_url=webhook.target_url,
        subscribed_events=webhook.subscribed_events,
        is_failing=webhook.is_failing,
        created_at=webhook.created_at,
    )


@router.get("", response_model=list[WebhookResponse])
async def list_webhooks(
    ctx: TenantContext = Depends(get_current_tenant_context),
    db: AsyncSession = Depends(get_db),
) -> list[WebhookResponse]:
    result = await db.execute(select(Webhook).where(Webhook.business_id == ctx.business_id))
    return [_to_response(w) for w in result.scalars().all()]


@router.post("", status_code=201, response_model=WebhookWithSecretResponse)
async def create_webhook(
    payload: WebhookCreateRequest,
    ctx: TenantContext = Depends(require_role("owner", "admin")),
    db: AsyncSession = Depends(get_db),
) -> WebhookWithSecretResponse:
    raw_secret = generate_secret(prefix="whsec_")
    webhook = Webhook(
        id=uuid7(),
        business_id=ctx.business_id,
        target_url=str(payload.target_url),
        subscribed_events=payload.subscribed_events,
        secret_hash=hash_secret(raw_secret),
    )
    db.add(webhook)
    await db.commit()

    return WebhookWithSecretResponse(**_to_response(webhook).model_dump(), secret=raw_secret)


@router.delete("/{webhook_id}", status_code=204)
async def delete_webhook(
    webhook_id: uuid.UUID,
    ctx: TenantContext = Depends(require_role("owner", "admin")),
    db: AsyncSession = Depends(get_db),
) -> None:
    result = await db.execute(
        select(Webhook).where(Webhook.id == webhook_id, Webhook.business_id == ctx.business_id)
    )
    webhook = result.scalar_one_or_none()
    if webhook is None:
        raise NotFoundError("Webhook not found")

    await db.delete(webhook)
    await db.commit()
