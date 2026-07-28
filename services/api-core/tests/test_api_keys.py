import pytest
from tests.helpers import auth_headers, mint_token, register

pytestmark = pytest.mark.asyncio


async def test_create_and_list_api_key(client):
    body = await register(client)
    headers = auth_headers(body["access_token"])

    create_resp = await client.post(
        "/businesses/me/api-keys",
        headers=headers,
        json={"name": "Zapier integration", "scopes": ["read"]},
    )
    assert create_resp.status_code == 201
    created = create_resp.json()
    assert created["secret"].startswith("plt_")
    assert created["prefix"] == created["secret"][:8]

    list_resp = await client.get("/businesses/me/api-keys", headers=headers)
    assert list_resp.status_code == 200
    items = list_resp.json()
    assert len(items) == 1
    assert "secret" not in items[0]


async def test_create_api_key_rejects_unknown_scope(client):
    body = await register(client)
    resp = await client.post(
        "/businesses/me/api-keys",
        headers=auth_headers(body["access_token"]),
        json={"name": "x", "scopes": ["admin"]},
    )
    assert resp.status_code == 422


async def test_revoke_api_key_hides_it_from_list(client):
    body = await register(client)
    headers = auth_headers(body["access_token"])

    create_resp = await client.post(
        "/businesses/me/api-keys", headers=headers, json={"name": "temp key", "scopes": ["read", "write"]}
    )
    key_id = create_resp.json()["id"]

    revoke_resp = await client.delete(f"/businesses/me/api-keys/{key_id}", headers=headers)
    assert revoke_resp.status_code == 204

    list_resp = await client.get("/businesses/me/api-keys", headers=headers)
    assert list_resp.json() == []

    second_revoke = await client.delete(f"/businesses/me/api-keys/{key_id}", headers=headers)
    assert second_revoke.status_code == 404


async def test_staff_cannot_create_api_key(client):
    body = await register(client)
    staff_token = mint_token(user_id=body["user"]["id"], business_id=body["user"]["business_id"], role="staff")

    resp = await client.post(
        "/businesses/me/api-keys", headers=auth_headers(staff_token), json={"name": "x", "scopes": ["read"]}
    )
    assert resp.status_code == 403
