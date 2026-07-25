import pytest

pytestmark = pytest.mark.asyncio


async def _register(
    client, *, email="owner@example.com", password="correct-horse-battery-staple", business_name="Test Biz"
):
    return await client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
            "business_name": business_name,
            "timezone": "America/New_York",
        },
    )


async def test_register_creates_business_and_returns_tokens(client):
    resp = await _register(client)
    assert resp.status_code == 201
    body = resp.json()
    assert body["user"]["email"] == "owner@example.com"
    assert body["user"]["role"] == "owner"
    assert body["access_token"]
    assert resp.cookies.get("pluto_refresh_token")


async def test_register_rejects_duplicate_email(client):
    first = await _register(client)
    assert first.status_code == 201

    second = await _register(client)
    assert second.status_code == 409
    assert second.json()["error"]["code"] == "CONFLICT"


async def test_register_rejects_short_password(client):
    resp = await _register(client, password="short")
    assert resp.status_code == 422


async def test_login_succeeds_with_correct_credentials(client):
    await _register(client, email="login-test@example.com", password="correct-horse-battery-staple")

    resp = await client.post(
        "/auth/login", json={"email": "login-test@example.com", "password": "correct-horse-battery-staple"}
    )
    assert resp.status_code == 200
    assert resp.json()["user"]["email"] == "login-test@example.com"
    assert resp.cookies.get("pluto_refresh_token")


async def test_login_fails_with_wrong_password(client):
    await _register(client, email="wrongpw@example.com")

    resp = await client.post("/auth/login", json={"email": "wrongpw@example.com", "password": "not-the-password"})
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "UNAUTHORIZED"


async def test_login_fails_for_unknown_email_with_same_error_as_wrong_password(client):
    resp = await client.post("/auth/login", json={"email": "nobody@example.com", "password": "whatever12345"})
    assert resp.status_code == 401
    assert resp.json()["error"]["message"] == "Invalid email or password"


async def test_refresh_rotates_token_and_issues_new_access_token(client):
    register_resp = await _register(client, email="refresh-test@example.com")
    old_access_token = register_resp.json()["access_token"]

    refresh_resp = await client.post("/auth/refresh")
    assert refresh_resp.status_code == 200
    new_body = refresh_resp.json()
    assert new_body["access_token"] != old_access_token
    assert new_body["user"]["email"] == "refresh-test@example.com"

    # The client's cookie jar now holds the *new* refresh token (rotation) — the old cookie value
    # is gone from the jar, which is exactly what should happen.
    assert refresh_resp.cookies.get("pluto_refresh_token")


async def test_refresh_without_cookie_is_unauthorized(client):
    resp = await client.post("/auth/refresh")
    assert resp.status_code == 401


async def test_refresh_reuse_detection_revokes_all_sessions(client):
    await _register(client, email="reuse-test@example.com")

    old_refresh_cookie = client.cookies.get("pluto_refresh_token")

    first_refresh = await client.post("/auth/refresh")
    assert first_refresh.status_code == 200

    # Replay the *original* (now-rotated-away) refresh token — simulates a stolen token being
    # used after the legitimate client already rotated past it.
    client.cookies.set("pluto_refresh_token", old_refresh_cookie)
    replay_resp = await client.post("/auth/refresh")
    assert replay_resp.status_code == 401
    assert "already been used" in replay_resp.json()["error"]["message"]

    # The token issued by the *first* (legitimate) refresh must now be dead too — reuse detection
    # revokes the whole chain, not just the replayed token.
    latest_refresh_cookie = first_refresh.cookies.get("pluto_refresh_token")
    client.cookies.set("pluto_refresh_token", latest_refresh_cookie)
    second_attempt = await client.post("/auth/refresh")
    assert second_attempt.status_code == 401


async def test_logout_revokes_refresh_token(client):
    await _register(client, email="logout-test@example.com")

    logout_resp = await client.post("/auth/logout")
    assert logout_resp.status_code == 204

    refresh_resp = await client.post("/auth/refresh")
    assert refresh_resp.status_code == 401


async def test_register_rate_limit(client):
    for i in range(5):
        resp = await _register(client, email=f"rate-{i}@example.com")
        assert resp.status_code == 201

    limited = await _register(client, email="rate-6@example.com")
    assert limited.status_code == 429
    assert limited.json()["error"]["code"] == "RATE_LIMITED"
