"""AI agent configuration — see the `AI Agent Config` tag in docs/api/openapi.yaml and
docs/architecture/03-ai-and-voice-architecture.md §1. `test-call` (which needs a live Twilio
integration) is intentionally not implemented here — see PROJECT_STATUS.md technical debt.
"""

from fastapi import APIRouter, Depends
from pluto_core.db.base import TenantContext
from pluto_core.db.models.ai_agent import AiAgentConfig
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_tenant_context, get_db, require_role
from app.schemas.ai_agent_config import AiAgentConfigInput, AiAgentConfigResponse, EscalationRules

router = APIRouter(prefix="/businesses/me/ai-agent-config", tags=["AI Agent Config"])

_DEFAULT_SYSTEM_PROMPT = (
    "You are a helpful AI receptionist. A business owner has not yet configured your instructions."
)


def _to_response(config: AiAgentConfig) -> AiAgentConfigResponse:
    return AiAgentConfigResponse(
        id=str(config.id),
        version=config.version,
        system_prompt=config.system_prompt,
        voice_id=config.voice_id,
        language=config.language,
        enabled_tools=config.enabled_tools,
        escalation_rules=EscalationRules(**config.escalation_rules) if config.escalation_rules else EscalationRules(),
    )


async def _get_or_create(db: AsyncSession, ctx: TenantContext) -> AiAgentConfig:
    """Every business gets a working-defaults config the moment it's first read — matches the
    onboarding flow (docs/product/02-user-flows.md §1), where the AI must be usable in a
    degraded-but-functional mode even before the owner configures anything.
    """
    result = await db.execute(select(AiAgentConfig).where(AiAgentConfig.business_id == ctx.business_id))
    config = result.scalar_one_or_none()
    if config is not None:
        return config

    config = AiAgentConfig(business_id=ctx.business_id, system_prompt=_DEFAULT_SYSTEM_PROMPT)
    db.add(config)
    await db.commit()
    await db.refresh(config)
    return config


@router.get("", response_model=AiAgentConfigResponse)
async def get_ai_agent_config(
    ctx: TenantContext = Depends(get_current_tenant_context),
    db: AsyncSession = Depends(get_db),
) -> AiAgentConfigResponse:
    return _to_response(await _get_or_create(db, ctx))


@router.put("", response_model=AiAgentConfigResponse)
async def update_ai_agent_config(
    payload: AiAgentConfigInput,
    ctx: TenantContext = Depends(require_role("owner", "admin")),
    db: AsyncSession = Depends(get_db),
) -> AiAgentConfigResponse:
    config = await _get_or_create(db, ctx)

    config.system_prompt = payload.system_prompt
    config.voice_id = payload.voice_id
    config.language = payload.language
    config.enabled_tools = payload.enabled_tools
    config.escalation_rules = payload.escalation_rules.model_dump()
    config.version += 1

    await db.commit()
    await db.refresh(config)
    return _to_response(config)
