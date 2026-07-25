"""Billing. See docs/architecture/02-data-model.md §2 and docs/product/02-user-flows.md §6.

`Subscription.agency_id` allows an Agency to be billed for its whole portfolio (white-label
billing model, deferred to Phase 4 per docs/product/01-business-requirements.md) — the column
exists now so that data model doesn't need a breaking migration when that ships.
"""

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from pluto_core.db.base import Base, TimestampMixin, UUIDPKMixin
from pluto_core.db.enums import SubscriptionStatus


class Subscription(UUIDPKMixin, TimestampMixin, Base):
    """Not `TenantScopedMixin`: a subscription can belong to a business OR an agency (exactly one
    of the two — enforced by the check constraint), so it can't hang off a single `business_id`
    RLS policy the way ordinary tenant tables do. Access control for this table is enforced at the
    application/repository layer rather than a blanket business_id RLS policy.
    """

    __tablename__ = "subscriptions"
    __table_args__ = (
        CheckConstraint(
            "(business_id IS NOT NULL) != (agency_id IS NOT NULL)",
            name="ck_subscriptions_exactly_one_owner",
        ),
    )

    business_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("businesses.id", ondelete="CASCADE"), nullable=True, index=True
    )
    agency_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("agencies.id", ondelete="CASCADE"), nullable=True, index=True
    )
    stripe_subscription_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    plan_id: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[SubscriptionStatus] = mapped_column(
        SAEnum(SubscriptionStatus, name="subscription_status", native_enum=True), nullable=False
    )
    current_period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class Invoice(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "invoices"

    subscription_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("subscriptions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    stripe_invoice_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    amount_due: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="usd")
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class UsageRecord(UUIDPKMixin, Base):
    """One row per metered usage event (a call, an SMS sent), reconciled against Stripe usage
    records at period end — see docs/architecture/02-data-model.md §2.
    """

    __tablename__ = "usage_records"

    subscription_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("subscriptions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    metric: Mapped[str] = mapped_column(
        String(50), nullable=False, doc="e.g. call_minutes, sms_sent, ai_tokens"
    )
    quantity: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    reconciled: Mapped[bool] = mapped_column(nullable=False, default=False)
