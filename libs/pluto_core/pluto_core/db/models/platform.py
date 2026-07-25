"""Platform-wide tables: webhooks, API keys, feature flags, and the audit log. See
docs/architecture/02-data-model.md §2 and docs/architecture/04-security-and-compliance.md.
"""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import ARRAY, Boolean, DateTime, ForeignKey, String, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from pluto_core.db.base import Base, TenantScopedMixin, TimestampMixin, UUIDPKMixin
from pluto_core.db.enums import AuditActorType


class Webhook(UUIDPKMixin, TimestampMixin, TenantScopedMixin, Base):
    __tablename__ = "webhooks"

    target_url: Mapped[str] = mapped_column(String(2000), nullable=False)
    subscribed_events: Mapped[list[str]] = mapped_column(ARRAY(String(100)), nullable=False, default=list)
    # Only a hash is ever persisted; the raw secret is returned once at creation time and never
    # again — see docs/product/03-technical-specifications.md §7 and openapi.yaml's
    # `WebhookWithSecret` schema.
    secret_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    is_failing: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class ApiKey(UUIDPKMixin, TimestampMixin, TenantScopedMixin, Base):
    __tablename__ = "api_keys"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    prefix: Mapped[str] = mapped_column(String(8), nullable=False, index=True)
    hashed_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    scopes: Mapped[list[str]] = mapped_column(ARRAY(String(20)), nullable=False, default=list)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class FeatureFlag(UUIDPKMixin, TimestampMixin, Base):
    """Platform-wide default. Not tenant-scoped — this is the global definition; per-tenant
    overrides live in `FeatureFlagOverride`.
    """

    __tablename__ = "feature_flags"

    key: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    default_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class FeatureFlagOverride(UUIDPKMixin, TimestampMixin, TenantScopedMixin, Base):
    __tablename__ = "feature_flag_overrides"

    flag_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("feature_flags.id", ondelete="CASCADE"), nullable=False, index=True
    )
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False)


class AuditLog(UUIDPKMixin, Base):
    """Append-only — no update/delete grants at the DB role level for the application role (see
    the RLS/grants migration). One row per mutating action, platform-wide. Deliberately not
    `TenantScopedMixin`-restricted-by-RLS in the usual sense: platform staff must be able to
    write/read audit rows that reference any business (that's the whole point of an audit trail),
    so this table uses a permissive read policy for `platform_admin`/`platform_support` roles and
    a business-scoped policy for regular tenant users — see the RLS migration for the exact
    policies, which differ per-table.
    """

    __tablename__ = "audit_logs"

    actor_type: Mapped[AuditActorType] = mapped_column(
        SAEnum(AuditActorType, name="audit_actor_type", native_enum=True),
        nullable=False,
    )
    actor_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    business_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("businesses.id", ondelete="SET NULL"), nullable=True, index=True
    )
    before: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    after: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
