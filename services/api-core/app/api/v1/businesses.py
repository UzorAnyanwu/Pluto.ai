"""Business profile + team management — see the `Businesses` and `Team` tags in
docs/api/openapi.yaml and the RBAC matrix in
docs/architecture/04-security-and-compliance.md §2 (owner/admin manage; staff/read_only can view
but not mutate; the owner can never be demoted or removed through this API).
"""

import secrets
import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from pluto_core.db.base import TenantContext
from pluto_core.db.enums import BusinessRole
from pluto_core.db.models.tenancy import Business, User
from pluto_core.db.uuid7 import uuid7
from pluto_core.security.passwords import hash_password
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_tenant_context, get_db, require_role
from app.errors import ConflictError, ForbiddenError, NotFoundError
from app.schemas.business import (
    BusinessResponse,
    BusinessUpdateRequest,
    TeamMemberInviteRequest,
    TeamMemberResponse,
    TeamMemberRoleUpdateRequest,
)

router = APIRouter(prefix="/businesses/me", tags=["Businesses"])
team_router = APIRouter(prefix="/businesses/me/team", tags=["Team"])


def _to_business_response(business: Business) -> BusinessResponse:
    return BusinessResponse(
        id=business.id,
        name=business.name,
        slug=business.slug,
        industry=business.industry,
        timezone=business.timezone,
        operating_hours=business.operating_hours,
        status=business.status.value,
        version=business.version,
        created_at=business.created_at,
    )


def _to_team_member_response(user: User) -> TeamMemberResponse:
    return TeamMemberResponse(
        user_id=user.id,
        email=user.email,
        role=user.role.value,
        status="active" if user.accepted_at is not None else "invited",
        invited_at=user.invited_at,
    )


@router.get("", response_model=BusinessResponse)
async def get_business(
    ctx: TenantContext = Depends(get_current_tenant_context),
    db: AsyncSession = Depends(get_db),
) -> BusinessResponse:
    business = await db.get(Business, ctx.business_id)
    if business is None:
        # Should be unreachable for a validly-authenticated request — the JWT's business_id came
        # from a row that existed at issuance time — but a business could theoretically have
        # been hard-deleted (GDPR erasure) since. Fail explicitly rather than let a None slip
        # through to the response model.
        raise NotFoundError("Business not found")
    return _to_business_response(business)


@router.patch("", response_model=BusinessResponse)
async def update_business(
    payload: BusinessUpdateRequest,
    ctx: TenantContext = Depends(require_role("owner", "admin")),
    db: AsyncSession = Depends(get_db),
) -> BusinessResponse:
    update_fields = payload.model_dump(exclude_unset=True, exclude={"version"})

    result = await db.execute(
        update(Business)
        .where(Business.id == ctx.business_id, Business.version == payload.version)
        .values(**update_fields, version=Business.version + 1)
        .returning(Business)
    )
    business = result.scalar_one_or_none()
    if business is None:
        raise ConflictError(
            "Business was modified by someone else — refresh and try again",
            details={"expected_version": payload.version},
        )
    await db.commit()
    return _to_business_response(business)


@team_router.get("", response_model=list[TeamMemberResponse])
async def list_team(
    ctx: TenantContext = Depends(get_current_tenant_context),
    db: AsyncSession = Depends(get_db),
) -> list[TeamMemberResponse]:
    result = await db.execute(
        select(User).where(User.business_id == ctx.business_id, User.deleted_at.is_(None))
    )
    return [_to_team_member_response(u) for u in result.scalars().all()]


@team_router.post("", status_code=201, response_model=TeamMemberResponse)
async def invite_team_member(
    payload: TeamMemberInviteRequest,
    ctx: TenantContext = Depends(require_role("owner", "admin")),
    db: AsyncSession = Depends(get_db),
) -> TeamMemberResponse:
    # No email-invitation flow exists yet (would need outbound email infrastructure this repo
    # doesn't have — see PROJECT_STATUS.md technical debt). The invited row is created with an
    # unusable random password so the account exists and is visible in the team list, but cannot
    # be logged into until a real accept-invite flow (which sets a real password) is built.
    placeholder_password = hash_password(secrets.token_urlsafe(32))

    user = User(
        id=uuid7(),
        business_id=ctx.business_id,
        email=payload.email,
        hashed_password=placeholder_password,
        role=BusinessRole(payload.role),
        invited_at=datetime.now(UTC),
    )
    db.add(user)
    try:
        await db.commit()
    except IntegrityError as exc:
        raise ConflictError("A team member with this email already exists") from exc

    return _to_team_member_response(user)


@team_router.patch("/{user_id}", response_model=TeamMemberResponse)
async def update_team_member_role(
    user_id: uuid.UUID,
    payload: TeamMemberRoleUpdateRequest,
    ctx: TenantContext = Depends(require_role("owner", "admin")),
    db: AsyncSession = Depends(get_db),
) -> TeamMemberResponse:
    result = await db.execute(
        select(User).where(
            User.id == user_id, User.business_id == ctx.business_id, User.deleted_at.is_(None)
        )
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise NotFoundError("Team member not found")
    if user.role == BusinessRole.owner:
        raise ForbiddenError("Cannot demote/remove the business owner")

    user.role = BusinessRole(payload.role)
    await db.commit()
    return _to_team_member_response(user)


@team_router.delete("/{user_id}", status_code=204)
async def remove_team_member(
    user_id: uuid.UUID,
    ctx: TenantContext = Depends(require_role("owner", "admin")),
    db: AsyncSession = Depends(get_db),
) -> None:
    result = await db.execute(
        select(User).where(
            User.id == user_id, User.business_id == ctx.business_id, User.deleted_at.is_(None)
        )
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise NotFoundError("Team member not found")
    if user.role == BusinessRole.owner:
        raise ForbiddenError("Cannot remove the business owner")

    user.deleted_at = datetime.now(UTC)
    await db.commit()
