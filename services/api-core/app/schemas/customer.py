import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class CustomerResponse(BaseModel):
    id: uuid.UUID
    name: str | None
    phone: str | None
    email: str | None
    tags: list[str]
    created_at: datetime


class CustomerDetailResponse(CustomerResponse):
    custom_fields: dict[str, Any]
    conversation_ids: list[uuid.UUID]
    booking_ids: list[uuid.UUID]


class CustomerUpdateRequest(BaseModel):
    tags: list[str] | None = None
    custom_fields: dict[str, Any] | None = None
    name: str | None = Field(default=None, max_length=200)
    email: str | None = Field(default=None, max_length=320)


class Pagination(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int


class PaginatedCustomers(BaseModel):
    items: list[CustomerResponse]
    pagination: Pagination
