import pytest
from tests.helpers import auth_headers, mint_token, register

pytestmark = pytest.mark.asyncio


async def test_get_ai_agent_config_returns_working_defaults(client):
    body = await register(client)
    resp = await client.get("/businesses/me/ai-agent-config", headers=auth_headers(body["access_token"]))
    assert resp.status_code == 200
    data = resp.json()
    assert data["version"] == 1
    assert data["voice_id"] == "default"
    assert data["language"] == "en-US"
    assert data["enabled_tools"] == []


async def test_update_ai_agent_config_persists(client):
    body = await register(client)
    headers = auth_headers(body["access_token"])

    resp = await client.put(
        "/businesses/me/ai-agent-config",
        headers=headers,
        json={
            "system_prompt": "You are Dana, a receptionist for Acme Dental.",
            "voice_id": "warm-female-1",
            "language": "en-US",
            "enabled_tools": ["book_appointment", "lookup_pricing"],
            "escalation_rules": {
                "always_escalate_intents": ["complaint"],
                "max_clarification_attempts": 2,
            },
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["version"] == 2
    assert data["voice_id"] == "warm-female-1"
    assert data["enabled_tools"] == ["book_appointment", "lookup_pricing"]
    assert data["escalation_rules"]["max_clarification_attempts"] == 2

    get_resp = await client.get("/businesses/me/ai-agent-config", headers=headers)
    assert get_resp.json()["system_prompt"].startswith("You are Dana")
    assert get_resp.json()["version"] == 2


async def test_staff_cannot_update_ai_agent_config(client):
    body = await register(client)
    staff_token = mint_token(user_id=body["user"]["id"], business_id=body["user"]["business_id"], role="staff")

    resp = await client.put(
        "/businesses/me/ai-agent-config",
        headers=auth_headers(staff_token),
        json={"system_prompt": "x", "voice_id": "v", "language": "en-US"},
    )
    assert resp.status_code == 403


async def test_staff_can_view_ai_agent_config(client):
    body = await register(client)
    staff_token = mint_token(user_id=body["user"]["id"], business_id=body["user"]["business_id"], role="staff")

    resp = await client.get("/businesses/me/ai-agent-config", headers=auth_headers(staff_token))
    assert resp.status_code == 200
