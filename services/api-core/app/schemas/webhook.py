import uuid
from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl, field_validator

ALLOWED_WEBHOOK_EVENTS = {
    "call.completed",
    "booking.created",
    "booking.cancelled",
    "lead.qualified",
    "conversation.escalated",
}


class WebhookResponse(BaseModel):
    id: uuid.UUID
    target_url: str
    subscribed_events: list[str]
    is_failing: bool
    created_at: datetime


class WebhookWithSecretResponse(WebhookResponse):
    secret: str = Field(description="Shown once — used to verify X-Pluto-Signature on delivered payloads.")


class WebhookCreateRequest(BaseModel):
    target_url: HttpUrl
    subscribed_events: list[str] = Field(min_length=1)

    @field_validator("subscribed_events")
    @classmethod
    def _validate_events(cls, value: list[str]) -> list[str]:
        unknown = set(value) - ALLOWED_WEBHOOK_EVENTS
        if unknown:
            raise ValueError(f"Unknown event type(s): {sorted(unknown)}")
        return value
