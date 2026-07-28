"""Request/response models for the `Businesses` and `Team` tags in docs/api/openapi.yaml."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field


class BusinessResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    industry: str | None
    timezone: str
    operating_hours: dict[str, Any]
    status: str
    version: int
    created_at: datetime


class BusinessUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    industry: str | None = Field(default=None, max_length=100)
    timezone: str | None = Field(default=None, min_length=1, max_length=64)
    operating_hours: dict[str, Any] | None = None
    version: int = Field(description="Required — optimistic concurrency check, see technical specifications §10.")


class TeamMemberResponse(BaseModel):
    user_id: uuid.UUID
    email: str
    role: str
    status: str  # "invited" | "active" — derived from accepted_at, not stored directly
    invited_at: datetime | None


class TeamMemberInviteRequest(BaseModel):
    email: EmailStr
    role: str = Field(pattern="^(admin|staff|read_only)$")


class TeamMemberRoleUpdateRequest(BaseModel):
    role: str = Field(pattern="^(admin|staff|read_only)$")
