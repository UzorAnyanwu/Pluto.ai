"""Tenancy hierarchy: Platform -> Agency -> Business -> Users. See
docs/architecture/02-data-model.md §1-2.

Platform staff and agency staff are deliberately modeled as separate tables from business `User`,
not a role flag on a shared table — see docs/architecture/02-data-model.md §2: this is a stronger
isolation guarantee than a role check, since platform/agency staff simply aren't reachable through
any RLS policy scoped to `business_id`.
"""

import uuid
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pluto_core.db.base import Base, SoftDeleteMixin, TimestampMixin, UUIDPKMixin, VersionedMixin
from pluto_core.db.enums import AgencyRole, BusinessRole, BusinessStatus, PlatformRole


class Agency(UUIDPKMixin, TimestampMixin, SoftDeleteMixin, VersionedMixin, Base):
    """A white-label reseller. Optional — a Business may have no Agency (agency_id null on
    Business means "direct Pluto AI customer"). Not tenant-scoped itself (there is no parent to
    scope it to); it is the tenant root for its own RLS policy — see the agency-scoped policy in
    the RLS migration.
    """

    __tablename__ = "agencies"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    branding: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    billing_terms: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)

    businesses: Mapped[list["Business"]] = relationship(back_populates="agency")
    agency_users: Mapped[list["AgencyUser"]] = relationship(back_populates="agency")


class Business(UUIDPKMixin, TimestampMixin, SoftDeleteMixin, VersionedMixin, Base):
    __tablename__ = "businesses"

    agency_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("agencies.id", ondelete="SET NULL"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    industry: Mapped[str | None] = mapped_column(String(100), nullable=True)
    timezone: Mapped[str] = mapped_column(String(64), nullable=False, default="UTC")
    operating_hours: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    status: Mapped[BusinessStatus] = mapped_column(
        SAEnum(BusinessStatus, name="business_status", native_enum=True),
        nullable=False,
        default=BusinessStatus.trial,
    )

    agency: Mapped[Optional["Agency"]] = relationship(back_populates="businesses")
    users: Mapped[list["User"]] = relationship(back_populates="business", cascade="all, delete-orphan")


class User(UUIDPKMixin, TimestampMixin, SoftDeleteMixin, VersionedMixin, Base):
    """A human member of a business — the primary actor type for the MVP dashboard and API."""

    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("business_id", "email", name="uq_users_business_email"),)

    business_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    email: Mapped[str] = mapped_column(String(320), nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[BusinessRole] = mapped_column(
        SAEnum(BusinessRole, name="business_role", native_enum=True), nullable=False
    )
    invited_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    business: Mapped["Business"] = relationship(back_populates="users")


class PlatformUser(UUIDPKMixin, TimestampMixin, SoftDeleteMixin, VersionedMixin, Base):
    """Internal Pluto AI staff. Deliberately not tenant-scoped and not RLS-restricted by
    `business_id` — access to tenant data from this actor type is only ever granted through the
    explicit, audited support-access flow (docs/product/02-user-flows.md §7), never ambiently.
    """

    __tablename__ = "platform_users"

    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[PlatformRole] = mapped_column(
        SAEnum(PlatformRole, name="platform_role", native_enum=True), nullable=False
    )


class AgencyUser(UUIDPKMixin, TimestampMixin, SoftDeleteMixin, VersionedMixin, Base):
    __tablename__ = "agency_users"
    __table_args__ = (UniqueConstraint("agency_id", "email", name="uq_agency_users_agency_email"),)

    agency_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("agencies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[AgencyRole] = mapped_column(
        SAEnum(AgencyRole, name="agency_role", native_enum=True), nullable=False
    )

    agency: Mapped["Agency"] = relationship(back_populates="agency_users")


class RefreshToken(UUIDPKMixin, TimestampMixin, Base):
    """Backs JWT refresh rotation + reuse detection — see
    docs/architecture/04-security-and-compliance.md §1. Only the hash is stored, never the raw
    token (same principle as password storage: a leaked database must not yield usable tokens).
    Not tenant-scoped via TenantScopedMixin/RLS: a refresh token lookup happens *before* a tenant
    context exists (it's how the tenant context gets established), so it is looked up by
    `token_hash` directly with an application-layer `business_id` check, not RLS.
    """

    __tablename__ = "refresh_tokens"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    business_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    replaced_by_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("refresh_tokens.id", ondelete="SET NULL"), nullable=True
    )
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
