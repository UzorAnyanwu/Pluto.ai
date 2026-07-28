"""CRM — customers. See the `Customers` tag in docs/api/openapi.yaml.

No `POST` endpoint exists (or is planned for MVP): customers are created as a side effect of a
conversation (a call, a WhatsApp message) per docs/architecture/02-data-model.md §2 — "every
interaction updates a Customer" — not created directly through this API. Until the voice/AI
pipeline exists to actually produce that side effect, there is no way to populate this table
except direct DB writes (which is exactly how this file's tests seed data — see
tests/test_customers.py).
"""

import uuid

from fastapi import APIRouter, Depends, Query
from pluto_core.db.base import TenantContext
from pluto_core.db.models.crm import Conversation, Customer
from pluto_core.db.models.scheduling import Booking
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_tenant_context, get_db, require_role
from app.errors import NotFoundError
from app.schemas.customer import (
    CustomerDetailResponse,
    CustomerResponse,
    CustomerUpdateRequest,
    PaginatedCustomers,
    Pagination,
)

router = APIRouter(prefix="/businesses/me/customers", tags=["Customers"])


def _to_response(customer: Customer) -> CustomerResponse:
    return CustomerResponse(
        id=customer.id,
        name=customer.name,
        phone=customer.phone,
        email=customer.email,
        tags=customer.tags,
        created_at=customer.created_at,
    )


async def _get_customer_or_404(db: AsyncSession, ctx: TenantContext, customer_id: uuid.UUID) -> Customer:
    result = await db.execute(
        select(Customer).where(
            Customer.id == customer_id,
            Customer.business_id == ctx.business_id,
            Customer.deleted_at.is_(None),
        )
    )
    customer = result.scalar_one_or_none()
    if customer is None:
        raise NotFoundError("Customer not found")
    return customer


async def _to_detail_response(db: AsyncSession, customer: Customer) -> CustomerDetailResponse:
    conversation_ids = (
        await db.execute(select(Conversation.id).where(Conversation.customer_id == customer.id))
    ).scalars().all()
    booking_ids = (await db.execute(select(Booking.id).where(Booking.customer_id == customer.id))).scalars().all()

    return CustomerDetailResponse(
        **_to_response(customer).model_dump(),
        custom_fields=customer.custom_fields,
        conversation_ids=list(conversation_ids),
        booking_ids=list(booking_ids),
    )


@router.get("", response_model=PaginatedCustomers)
async def list_customers(
    q: str | None = Query(default=None, description="Free-text search across name, phone, email"),
    tag: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    ctx: TenantContext = Depends(get_current_tenant_context),
    db: AsyncSession = Depends(get_db),
) -> PaginatedCustomers:
    filters = [Customer.business_id == ctx.business_id, Customer.deleted_at.is_(None)]
    if q:
        pattern = f"%{q}%"
        filters.append(
            or_(Customer.name.ilike(pattern), Customer.phone.ilike(pattern), Customer.email.ilike(pattern))
        )
    if tag:
        # SQLAlchemy's stubs don't disambiguate the ARRAY-specific `.any(value)` overload (Postgres
        # `value = ANY(array_column)`) from the ORM relationship `.any()` overload — this is the
        # correct, working, tested usage (see tests/test_customers.py::test_list_customers_filters_by_tag).
        filters.append(Customer.tags.any(tag))  # type: ignore[arg-type]

    total_items = await db.scalar(select(func.count()).select_from(Customer).where(*filters)) or 0
    total_pages = max(1, -(-total_items // page_size))  # ceil division

    result = await db.execute(
        select(Customer)
        .where(*filters)
        .order_by(Customer.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    customers = result.scalars().all()

    return PaginatedCustomers(
        items=[_to_response(c) for c in customers],
        pagination=Pagination(page=page, page_size=page_size, total_items=total_items, total_pages=total_pages),
    )


@router.get("/{customer_id}", response_model=CustomerDetailResponse)
async def get_customer(
    customer_id: uuid.UUID,
    ctx: TenantContext = Depends(get_current_tenant_context),
    db: AsyncSession = Depends(get_db),
) -> CustomerDetailResponse:
    customer = await _get_customer_or_404(db, ctx, customer_id)
    return await _to_detail_response(db, customer)


@router.patch("/{customer_id}", response_model=CustomerDetailResponse)
async def update_customer(
    customer_id: uuid.UUID,
    payload: CustomerUpdateRequest,
    ctx: TenantContext = Depends(require_role("owner", "admin", "staff")),
    db: AsyncSession = Depends(get_db),
) -> CustomerDetailResponse:
    customer = await _get_customer_or_404(db, ctx, customer_id)

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(customer, field, value)
    await db.commit()

    return await _to_detail_response(db, customer)
