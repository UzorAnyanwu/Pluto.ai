"""Shared test helpers — not a conftest fixture module, just plain importable functions."""

import uuid

from app.config import get_jwt_keys, get_settings
from pluto_core.security.jwt import create_access_token

DEFAULT_PASSWORD = "correct-horse-battery-staple"


async def register(client, *, email="owner@example.com", business_name="Test Biz", password=DEFAULT_PASSWORD):
    resp = await client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
            "business_name": business_name,
            "timezone": "America/New_York",
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def mint_token(*, user_id: str, business_id: str, role: str) -> str:
    """Mints an access token directly (bypassing login) so tests can exercise RBAC for roles
    that have no way to log in yet — invited team members get an unusable placeholder password
    until a real accept-invite flow exists (see app/api/v1/businesses.py).
    """
    private_key, _ = get_jwt_keys()
    settings = get_settings()
    return create_access_token(
        user_id=uuid.UUID(str(user_id)),
        business_id=uuid.UUID(str(business_id)),
        role=role,
        private_key=private_key,
        issuer=settings.jwt_issuer,
        ttl_seconds=settings.access_token_ttl_seconds,
    )
