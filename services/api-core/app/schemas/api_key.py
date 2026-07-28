import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

ALLOWED_SCOPES = {"read", "write"}


class ApiKeyResponse(BaseModel):
    id: uuid.UUID
    name: str
    prefix: str
    scopes: list[str]
    last_used_at: datetime | None
    created_at: datetime


class ApiKeyWithSecretResponse(ApiKeyResponse):
    secret: str = Field(description="Shown once only — store it now, it cannot be retrieved again.")


class ApiKeyCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    scopes: list[str] = Field(min_length=1)

    @field_validator("scopes")
    @classmethod
    def _validate_scopes(cls, value: list[str]) -> list[str]:
        unknown = set(value) - ALLOWED_SCOPES
        if unknown:
            raise ValueError(f"Unknown scope(s): {sorted(unknown)}")
        return value
