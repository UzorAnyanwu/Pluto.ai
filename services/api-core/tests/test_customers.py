import pytest
from pluto_core.db.base import TenantContext, session_scope
from pluto_core.db.models.crm import Customer
from pluto_core.db.uuid7 import uuid7
from tests.helpers import auth_headers, mint_token, register

pytestmark = pytest.mark.asyncio


async def _seed_customer(business_id: str, user_id: str, **fields) -> str:
    customer_id = uuid7()
    defaults = {
        "id": customer_id,
        "business_id": business_id,
        "name": "Alice Example",
        "phone": "+15550001111",
        "email": None,
        "tags": [],
        "custom_fields": {},
    }
    defaults.update(fields)

    async with session_scope(TenantContext(business_id=business_id, user_id=user_id, role="owner")) as db:
        db.add(Customer(**defaults))
        await db.commit()

    return str(customer_id)


async def test_list_customers_empty_by_default(client):
    body = await register(client)
    resp = await client.get("/businesses/me/customers", headers=auth_headers(body["access_token"]))
    assert resp.status_code == 200
    data = resp.json()
    assert data["items"] == []
    assert data["pagination"]["total_items"] == 0


async def test_list_customers_search_and_pagination(client):
    body = await register(client)
    business_id, user_id = body["user"]["business_id"], body["user"]["id"]
    await _seed_customer(business_id, user_id, name="Alice Anderson", phone="+15550001111")
    await _seed_customer(business_id, user_id, name="Bob Baker", phone="+15550002222")

    headers = auth_headers(body["access_token"])

    all_resp = await client.get("/businesses/me/customers", headers=headers)
    assert all_resp.json()["pagination"]["total_items"] == 2

    search_resp = await client.get("/businesses/me/customers", headers=headers, params={"q": "Alice"})
    names = [c["name"] for c in search_resp.json()["items"]]
    assert names == ["Alice Anderson"]

    paged_resp = await client.get(
        "/businesses/me/customers", headers=headers, params={"page": 1, "page_size": 1}
    )
    paged = paged_resp.json()
    assert len(paged["items"]) == 1
    assert paged["pagination"]["total_pages"] == 2


async def test_list_customers_filters_by_tag(client):
    body = await register(client)
    business_id, user_id = body["user"]["business_id"], body["user"]["id"]
    await _seed_customer(business_id, user_id, name="Tagged", phone="+15550001111", tags=["vip"])
    await _seed_customer(business_id, user_id, name="Untagged", phone="+15550002222", tags=[])

    resp = await client.get(
        "/businesses/me/customers", headers=auth_headers(body["access_token"]), params={"tag": "vip"}
    )
    names = [c["name"] for c in resp.json()["items"]]
    assert names == ["Tagged"]


async def test_get_customer_detail(client):
    body = await register(client)
    business_id, user_id = body["user"]["business_id"], body["user"]["id"]
    customer_id = await _seed_customer(business_id, user_id, custom_fields={"budget": "500"})

    resp = await client.get(f"/businesses/me/customers/{customer_id}", headers=auth_headers(body["access_token"]))
    assert resp.status_code == 200
    data = resp.json()
    assert data["custom_fields"] == {"budget": "500"}
    assert data["conversation_ids"] == []
    assert data["booking_ids"] == []


async def test_get_customer_not_found(client):
    body = await register(client)
    resp = await client.get(f"/businesses/me/customers/{uuid7()}", headers=auth_headers(body["access_token"]))
    assert resp.status_code == 404


async def test_update_customer_tags_and_custom_fields(client):
    body = await register(client)
    business_id, user_id = body["user"]["business_id"], body["user"]["id"]
    customer_id = await _seed_customer(business_id, user_id)

    resp = await client.patch(
        f"/businesses/me/customers/{customer_id}",
        headers=auth_headers(body["access_token"]),
        json={"tags": ["vip", "returning"], "custom_fields": {"notes": "prefers afternoons"}},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["tags"] == ["vip", "returning"]
    assert data["custom_fields"] == {"notes": "prefers afternoons"}


async def test_read_only_cannot_update_customer(client):
    body = await register(client)
    business_id, user_id = body["user"]["business_id"], body["user"]["id"]
    customer_id = await _seed_customer(business_id, user_id)

    read_only_token = mint_token(user_id=user_id, business_id=business_id, role="read_only")
    resp = await client.patch(
        f"/businesses/me/customers/{customer_id}",
        headers=auth_headers(read_only_token),
        json={"tags": ["vip"]},
    )
    assert resp.status_code == 403


async def test_customers_are_tenant_isolated(client):
    owner_a = await register(client, email="tenant-a@example.com")
    owner_b = await register(client, email="tenant-b@example.com")
    customer_id = await _seed_customer(owner_a["user"]["business_id"], owner_a["user"]["id"])

    resp = await client.get(
        f"/businesses/me/customers/{customer_id}", headers=auth_headers(owner_b["access_token"])
    )
    assert resp.status_code == 404
