"""Locations, bookable services/employees, calendar connections, and bookings. See
docs/architecture/02-data-model.md §2 and docs/product/02-user-flows.md §3.
"""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from pluto_core.db.base import (
    Base,
    SoftDeleteMixin,
    TenantScopedMixin,
    TimestampMixin,
    UUIDPKMixin,
    VersionedMixin,
)
from pluto_core.db.enums import BookingStatus, CalendarProvider, CalendarSyncStatus


class Location(UUIDPKMixin, TimestampMixin, SoftDeleteMixin, TenantScopedMixin, Base):
    __tablename__ = "locations"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    timezone: Mapped[str] = mapped_column(String(64), nullable=False, default="UTC")
    phone_number_e164: Mapped[str | None] = mapped_column(String(20), nullable=True)
    operating_hours: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)


class Service(UUIDPKMixin, TimestampMixin, SoftDeleteMixin, TenantScopedMixin, Base):
    """What can be booked, and what it costs — surfaced to the AI as a bookable/quotable tool
    input per docs/architecture/03-ai-and-voice-architecture.md §1.
    """

    __tablename__ = "services"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_minutes: Mapped[int] = mapped_column(nullable=False, default=30)
    price_amount: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    price_currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")


class Employee(UUIDPKMixin, TimestampMixin, SoftDeleteMixin, TenantScopedMixin, Base):
    __tablename__ = "employees"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    location_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("locations.id", ondelete="SET NULL"), nullable=True
    )
    bookable: Mapped[bool] = mapped_column(nullable=False, default=True)


class CalendarConnection(UUIDPKMixin, TimestampMixin, TenantScopedMixin, Base):
    __tablename__ = "calendar_connections"

    provider: Mapped[CalendarProvider] = mapped_column(
        SAEnum(CalendarProvider, name="calendar_provider", native_enum=True), nullable=False
    )
    sync_status: Mapped[CalendarSyncStatus] = mapped_column(
        SAEnum(CalendarSyncStatus, name="calendar_sync_status", native_enum=True),
        nullable=False,
        default=CalendarSyncStatus.connected,
    )
    # Encrypted at the application layer (envelope encryption via KMS) before being written here —
    # see docs/architecture/04-security-and-compliance.md §5. This column stores ciphertext only.
    encrypted_oauth_tokens: Mapped[str] = mapped_column(Text, nullable=False)
    external_account_email: Mapped[str | None] = mapped_column(String(320), nullable=True)


class Booking(UUIDPKMixin, TimestampMixin, TenantScopedMixin, VersionedMixin, Base):
    __tablename__ = "bookings"

    customer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    service_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("services.id", ondelete="RESTRICT"), nullable=False
    )
    employee_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("employees.id", ondelete="SET NULL"), nullable=True
    )
    location_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("locations.id", ondelete="SET NULL"), nullable=True
    )
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[BookingStatus] = mapped_column(
        SAEnum(BookingStatus, name="booking_status", native_enum=True),
        nullable=False,
        default=BookingStatus.confirmed,
    )
    external_calendar_event_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    recurrence_rule: Mapped[str | None] = mapped_column(
        String(500), nullable=True, doc="RFC 5545 RRULE string, if this booking recurs"
    )
