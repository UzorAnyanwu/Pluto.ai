"""CRM + conversations. See docs/architecture/02-data-model.md §2.

`ConversationEvent` is the one deliberate exception to "no full event sourcing" (data model doc
§4): replaying exactly what an AI agent did during a call — in order, with tool-call inputs and
outputs — is a real, recurring debugging/compliance need, so the conversation/call state machine
is event-sourced while everything else uses soft-delete + audit-log + optimistic-concurrency.
"""

import uuid
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import ARRAY, DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pluto_core.db.base import Base, SoftDeleteMixin, TenantScopedMixin, TimestampMixin, UUIDPKMixin
from pluto_core.db.enums import (
    CallDirection,
    ConversationChannel,
    ConversationStatus,
    LeadQualificationStatus,
    MessageRole,
    Sentiment,
)


class Customer(UUIDPKMixin, TimestampMixin, SoftDeleteMixin, TenantScopedMixin, Base):
    __tablename__ = "customers"
    __table_args__ = (
        Index(
            "uq_customers_business_phone",
            "business_id",
            "phone",
            unique=True,
            postgresql_where="phone IS NOT NULL",
        ),
    )

    name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String(50)), nullable=False, default=list)
    custom_fields: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    memory_summary: Mapped[str | None] = mapped_column(
        Text, nullable=True, doc="Rolling AI-generated summary of this customer's history, used "
        "to give the AI continuity across returning calls — see AI architecture doc §1."
    )

    # No ORM relationship to Booking here: Booking lives in models/scheduling.py and a
    # cross-module relationship would create a module-import-order dependency for no real
    # benefit — the repository layer queries `Booking.customer_id` directly instead.
    conversations: Mapped[list["Conversation"]] = relationship(back_populates="customer")


class Conversation(UUIDPKMixin, TimestampMixin, TenantScopedMixin, Base):
    __tablename__ = "conversations"

    customer_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("customers.id", ondelete="SET NULL"), nullable=True, index=True
    )
    channel: Mapped[ConversationChannel] = mapped_column(
        SAEnum(ConversationChannel, name="conversation_channel", native_enum=True), nullable=False
    )
    status: Mapped[ConversationStatus] = mapped_column(
        SAEnum(ConversationStatus, name="conversation_status", native_enum=True),
        nullable=False,
        default=ConversationStatus.active,
    )
    sentiment: Mapped[Sentiment | None] = mapped_column(
        SAEnum(Sentiment, name="sentiment", native_enum=True), nullable=True
    )
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    customer: Mapped[Optional["Customer"]] = relationship(back_populates="conversations")
    messages: Mapped[list["Message"]] = relationship(back_populates="conversation", cascade="all, delete-orphan")
    call: Mapped[Optional["Call"]] = relationship(back_populates="conversation", uselist=False)


class Message(UUIDPKMixin, TenantScopedMixin, Base):
    __tablename__ = "messages"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[MessageRole] = mapped_column(
        SAEnum(MessageRole, name="message_role", native_enum=True), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    tool_calls: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    conversation: Mapped["Conversation"] = relationship(back_populates="messages")


class Call(UUIDPKMixin, TimestampMixin, TenantScopedMixin, Base):
    __tablename__ = "calls"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    twilio_call_sid: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    direction: Mapped[CallDirection] = mapped_column(
        SAEnum(CallDirection, name="call_direction", native_enum=True), nullable=False
    )
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    from_number: Mapped[str] = mapped_column(String(20), nullable=False)
    to_number: Mapped[str] = mapped_column(String(20), nullable=False)

    conversation: Mapped["Conversation"] = relationship(back_populates="call")
    recording: Mapped[Optional["CallRecording"]] = relationship(back_populates="call", uselist=False)
    transcript: Mapped[Optional["CallTranscript"]] = relationship(back_populates="call", uselist=False)


class CallRecording(UUIDPKMixin, TimestampMixin, TenantScopedMixin, Base):
    __tablename__ = "call_recordings"

    call_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("calls.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    s3_object_key: Mapped[str] = mapped_column(String(500), nullable=False)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    call: Mapped["Call"] = relationship(back_populates="recording")


class CallTranscript(UUIDPKMixin, TimestampMixin, TenantScopedMixin, Base):
    __tablename__ = "call_transcripts"

    call_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("calls.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    full_text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    utterances: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB, nullable=False, default=list, doc="Per-utterance text + start/end timestamps"
    )

    call: Mapped["Call"] = relationship(back_populates="transcript")


class Lead(UUIDPKMixin, TimestampMixin, TenantScopedMixin, Base):
    __tablename__ = "leads"

    customer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    conversation_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True
    )
    source: Mapped[ConversationChannel] = mapped_column(
        SAEnum(ConversationChannel, name="lead_source_channel", native_enum=True), nullable=False
    )
    qualification_status: Mapped[LeadQualificationStatus] = mapped_column(
        SAEnum(LeadQualificationStatus, name="lead_qualification_status", native_enum=True),
        nullable=False,
        default=LeadQualificationStatus.new,
    )
    extracted_fields: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)


class ConversationEvent(UUIDPKMixin, TenantScopedMixin, Base):
    """Append-only. No `updated_at`/soft-delete — an event, once written, is immutable."""

    __tablename__ = "conversation_events"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    event_type: Mapped[str] = mapped_column(
        String(100), nullable=False, doc="e.g. state_entered, tool_called, escalated, transferred"
    )
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
