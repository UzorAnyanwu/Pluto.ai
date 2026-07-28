import pytest
from tests.helpers import auth_headers, mint_token, register

pytestmark = pytest.mark.asyncio


async def test_create_and_list_webhook(client):
    body = await register(client)
    headers = auth_headers(body["access_token"])

    create_resp = await client.post(
        "/businesses/me/webhooks",
        headers=headers,
        json={"target_url": "https://example.com/hooks/pluto", "subscribed_events": ["call.completed"]},
    )
    assert create_resp.status_code == 201
    created = create_resp.json()
    assert created["secret"].startswith("whsec_")
    assert created["subscribed_events"] == ["call.completed"]

    list_resp = await client.get("/businesses/me/webhooks", headers=headers)
    assert list_resp.status_code == 200
    items = list_resp.json()
    assert len(items) == 1
    assert "secret" not in items[0]  # never returned again after creation


async def test_create_webhook_rejects_unknown_event(client):
    body = await register(client)
    resp = await client.post(
        "/businesses/me/webhooks",
        headers=auth_headers(body["access_token"]),
        json={"target_url": "https://example.com/hooks", "subscribed_events": ["not.a.real.event"]},
    )
    assert resp.status_code == 422


async def test_delete_webhook(client):
    body = await register(client)
    headers = auth_headers(body["access_token"])

    create_resp = await client.post(
        "/businesses/me/webhooks",
        headers=headers,
        json={"target_url": "https://example.com/hooks", "subscribed_events": ["booking.created"]},
    )
    webhook_id = create_resp.json()["id"]

    delete_resp = await client.delete(f"/businesses/me/webhooks/{webhook_id}", headers=headers)
    assert delete_resp.status_code == 204

    list_resp = await client.get("/businesses/me/webhooks", headers=headers)
    assert list_resp.json() == []


async def test_staff_cannot_create_webhook(client):
    body = await register(client)
    staff_token = mint_token(user_id=body["user"]["id"], business_id=body["user"]["business_id"], role="staff")

    resp = await client.post(
        "/businesses/me/webhooks",
        headers=auth_headers(staff_token),
        json={"target_url": "https://example.com/hooks", "subscribed_events": ["call.completed"]},
    )
    assert resp.status_code == 403
