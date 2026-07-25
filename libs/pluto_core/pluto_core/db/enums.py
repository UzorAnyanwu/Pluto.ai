"""Enumerations shared across models. Backed by native Postgres ENUM types (not plain strings) so
invalid values are rejected at the database layer, not just in application validation — defense in
depth per the general security posture in docs/architecture/04-security-and-compliance.md.
"""

import enum


class BusinessStatus(enum.StrEnum):
    trial = "trial"
    active = "active"
    past_due = "past_due"
    suspended = "suspended"


class BusinessRole(enum.StrEnum):
    """Roles scoped to a single business — see docs/architecture/04-security-and-compliance.md §2."""

    owner = "owner"
    admin = "admin"
    staff = "staff"
    read_only = "read_only"


class PlatformRole(enum.StrEnum):
    platform_admin = "platform_admin"
    platform_support = "platform_support"


class AgencyRole(enum.StrEnum):
    agency_admin = "agency_admin"
    agency_staff = "agency_staff"


class KnowledgeSourceType(enum.StrEnum):
    pdf = "pdf"
    docx = "docx"
    csv = "csv"
    url = "url"
    manual_text = "manual_text"
    faq = "faq"


class KnowledgeSourceStatus(enum.StrEnum):
    pending = "pending"
    indexing = "indexing"
    ready = "ready"
    failed = "failed"


class ConversationChannel(enum.StrEnum):
    voice = "voice"
    whatsapp = "whatsapp"
    sms = "sms"
    web_chat = "web_chat"
    email = "email"


class ConversationStatus(enum.StrEnum):
    active = "active"
    completed = "completed"
    escalated = "escalated"


class Sentiment(enum.StrEnum):
    positive = "positive"
    neutral = "neutral"
    negative = "negative"


class MessageRole(enum.StrEnum):
    customer = "customer"
    agent = "agent"
    system = "system"
    tool = "tool"


class CallDirection(enum.StrEnum):
    inbound = "inbound"
    outbound = "outbound"


class LeadQualificationStatus(enum.StrEnum):
    new = "new"
    qualified = "qualified"
    disqualified = "disqualified"
    converted = "converted"


class BookingStatus(enum.StrEnum):
    confirmed = "confirmed"
    cancelled = "cancelled"
    completed = "completed"
    no_show = "no_show"


class CalendarProvider(enum.StrEnum):
    google = "google"
    outlook = "outlook"
    calendly = "calendly"


class CalendarSyncStatus(enum.StrEnum):
    connected = "connected"
    error = "error"
    disconnected = "disconnected"


class WorkflowRunStatus(enum.StrEnum):
    running = "running"
    succeeded = "succeeded"
    failed = "failed"


class SubscriptionStatus(enum.StrEnum):
    trialing = "trialing"
    active = "active"
    past_due = "past_due"
    canceled = "canceled"


class ApiKeyScope(enum.StrEnum):
    read = "read"
    write = "write"


class AuditActorType(enum.StrEnum):
    user = "user"
    system = "system"
    api_key = "api_key"
    platform_staff = "platform_staff"
