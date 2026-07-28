import pytest
from tests.helpers import auth_headers, mint_token, register

pytestmark = pytest.mark.asyncio


async def test_get_business_profile(client):
    body = await register(client)
    resp = await client.get("/businesses/me", headers=auth_headers(body["access_token"]))
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Test Biz"
    assert data["status"] == "trial"
    assert data["version"] == 1


async def test_update_business_profile(client):
    body = await register(client)
    headers = auth_headers(body["access_token"])

    resp = await client.patch("/businesses/me", headers=headers, json={"name": "New Name", "version": 1})
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "New Name"
    assert data["version"] == 2

    # Persisted, not just returned
    get_resp = await client.get("/businesses/me", headers=headers)
    assert get_resp.json()["name"] == "New Name"


async def test_update_business_profile_conflict_on_stale_version(client):
    body = await register(client)
    headers = auth_headers(body["access_token"])

    resp = await client.patch("/businesses/me", headers=headers, json={"name": "X", "version": 99})
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "CONFLICT"


async def test_staff_cannot_update_business_profile(client):
    body = await register(client)
    staff_token = mint_token(user_id=body["user"]["id"], business_id=body["user"]["business_id"], role="staff")

    resp = await client.patch(
        "/businesses/me", headers=auth_headers(staff_token), json={"name": "X", "version": 1}
    )
    assert resp.status_code == 403


async def test_team_invite_list_role_update_and_remove(client):
    body = await register(client)
    owner_headers = auth_headers(body["access_token"])

    invite_resp = await client.post(
        "/businesses/me/team", headers=owner_headers, json={"email": "staff@example.com", "role": "staff"}
    )
    assert invite_resp.status_code == 201
    invited = invite_resp.json()
    assert invited["role"] == "staff"
    assert invited["status"] == "invited"

    list_resp = await client.get("/businesses/me/team", headers=owner_headers)
    assert list_resp.status_code == 200
    emails = {m["email"] for m in list_resp.json()}
    assert emails == {"owner@example.com", "staff@example.com"}

    role_resp = await client.patch(
        f"/businesses/me/team/{invited['user_id']}", headers=owner_headers, json={"role": "admin"}
    )
    assert role_resp.status_code == 200
    assert role_resp.json()["role"] == "admin"

    remove_resp = await client.delete(f"/businesses/me/team/{invited['user_id']}", headers=owner_headers)
    assert remove_resp.status_code == 204

    list_resp_2 = await client.get("/businesses/me/team", headers=owner_headers)
    assert len(list_resp_2.json()) == 1


async def test_cannot_demote_or_remove_the_owner(client):
    body = await register(client)
    owner_headers = auth_headers(body["access_token"])
    owner_user_id = body["user"]["id"]

    role_resp = await client.patch(
        f"/businesses/me/team/{owner_user_id}", headers=owner_headers, json={"role": "staff"}
    )
    assert role_resp.status_code == 403

    delete_resp = await client.delete(f"/businesses/me/team/{owner_user_id}", headers=owner_headers)
    assert delete_resp.status_code == 403


async def test_invite_duplicate_email_conflicts(client):
    body = await register(client)
    owner_headers = auth_headers(body["access_token"])

    first = await client.post(
        "/businesses/me/team", headers=owner_headers, json={"email": "dup@example.com", "role": "staff"}
    )
    assert first.status_code == 201

    second = await client.post(
        "/businesses/me/team", headers=owner_headers, json={"email": "dup@example.com", "role": "staff"}
    )
    assert second.status_code == 409


async def test_staff_cannot_invite_team_members(client):
    body = await register(client)
    staff_token = mint_token(user_id=body["user"]["id"], business_id=body["user"]["business_id"], role="staff")

    resp = await client.post(
        "/businesses/me/team",
        headers=auth_headers(staff_token),
        json={"email": "someone@example.com", "role": "staff"},
    )
    assert resp.status_code == 403
