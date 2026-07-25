"""Per-business AI agent configuration. See docs/architecture/03-ai-and-voice-architecture.md §1.

Per-customer memory (summarized history with a specific returning caller) is *not* stored here —
it lives on `Customer.memory_summary` (see models/crm.py), since memory is scoped to a customer,
not to the business-wide agent configuration.
"""

from typing import Any

from sqlalchemy import ARRAY, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from pluto_core.db.base import Base, TenantScopedMixin, TimestampMixin, UUIDPKMixin, VersionedMixin


class AiAgentConfig(UUIDPKMixin, TimestampMixin, TenantScopedMixin, VersionedMixin, Base):
    """One row per business (enforced by the unique constraint below). Updates go through the
    optimistic-concurrency `version` check — see docs/product/03-technical-specifications.md and
    the `PUT /businesses/me/ai-agent-config` contract in docs/api/openapi.yaml.
    """

    __tablename__ = "ai_agent_configs"
    __table_args__ = (UniqueConstraint("business_id", name="uq_ai_agent_configs_business"),)

    system_prompt: Mapped[str] = mapped_column(Text, nullable=False, default="")
    voice_id: Mapped[str] = mapped_column(String(100), nullable=False, default="default")
    language: Mapped[str] = mapped_column(String(10), nullable=False, default="en-US")
    enabled_tools: Mapped[list[str]] = mapped_column(ARRAY(String(100)), nullable=False, default=list)
    escalation_rules: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
