"""Proves Row-Level Security isolation through the actual application code path (pluto_core's
`session_scope`/ORM), complementing the raw-SQL proof done manually while building the RLS
migration. This is, per docs/product/03-technical-specifications.md §9, the single most
important test suite in this codebase — the entire multi-tenant security model
(docs/architecture/04-security-and-compliance.md §3) rests on RLS actually being enforced.
"""

import pytest
from pluto_core.db.base import TenantContext, session_scope
from pluto_core.db.models.tenancy import User
from sqlalchemy import select

pytestmark = pytest.mark.asyncio


async def _register_business(client, email: str) -> dict:
    resp = await client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "correct-horse-battery-staple",
            "business_name": f"Biz for {email}",
            "timezone": "UTC",
        },
    )
    assert resp.status_code == 201
    return resp.json()["user"]


async def test_tenant_can_only_see_its_own_user_rows(client):
    user_a = await _register_business(client, "tenant-a@example.com")
    user_b = await _register_business(client, "tenant-b@example.com")

    async with session_scope(
        TenantContext(business_id=user_a["business_id"], user_id=user_a["id"], role="owner")
    ) as session:
        rows = (await session.execute(select(User))).scalars().all()

    assert [str(r.business_id) for r in rows] == [user_a["business_id"]]
    assert [r.email for r in rows] == ["tenant-a@example.com"]

    async with session_scope(
        TenantContext(business_id=user_b["business_id"], user_id=user_b["id"], role="owner")
    ) as session:
        rows = (await session.execute(select(User))).scalars().all()

    assert [r.email for r in rows] == ["tenant-b@example.com"]


async def test_no_tenant_context_returns_no_rows() -> None:
    async with session_scope(None) as session:
        rows = (await session.execute(select(User))).scalars().all()

    assert rows == []


async def test_cannot_write_a_row_claiming_a_different_tenant(client):
    user_a = await _register_business(client, "writer-a@example.com")
    user_b = await _register_business(client, "writer-b@example.com")

    from pluto_core.db.enums import BusinessRole
    from pluto_core.db.uuid7 import uuid7

    async with session_scope(
        TenantContext(business_id=user_a["business_id"], user_id=user_a["id"], role="owner")
    ) as session:
        rogue = User(
            id=uuid7(),
            business_id=user_b["business_id"],  # claims tenant B while scoped as tenant A
            email="rogue@example.com",
            hashed_password="irrelevant",
            role=BusinessRole.staff,
        )
        session.add(rogue)
        with pytest.raises(Exception) as exc_info:
            await session.commit()
        assert "row-level security" in str(exc_info.value).lower()
