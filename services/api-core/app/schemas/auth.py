"""Request/response models for /auth/* — mirrors the schemas in docs/api/openapi.yaml exactly;
the OpenAPI spec is the contract (docs/product/03-technical-specifications.md §10), these are its
implementation.
"""

import uuid

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=256)
    business_name: str = Field(min_length=1, max_length=200)
    timezone: str = Field(min_length=1, max_length=64)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserSummary(BaseModel):
    id: uuid.UUID
    email: str
    role: str
    business_id: uuid.UUID


class AuthTokenPair(BaseModel):
    access_token: str
    expires_in: int
    user: UserSummary
