"""JWT issuance and verification — RS256 (asymmetric), not HS256.

Why asymmetric: per docs/architecture/04-security-and-compliance.md §1, multiple services need to
*verify* access tokens (api-core, and eventually voice-gateway/ai-engine for authenticated
internal calls), but only api-core (the issuer) should ever hold the ability to *mint* one. With
HS256 every verifier needs the same shared secret, so any service that can check a token can also
forge one. With RS256, verifiers only need the public key.
"""

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

import jwt as pyjwt

ALGORITHM = "RS256"


class TokenError(Exception):
    """Raised for any invalid, expired, or malformed token — callers should treat this uniformly
    as 401 Unauthorized without distinguishing the reason to the client (avoids leaking whether a
    token is expired vs. tampered vs. wrong-issuer, which is unnecessary information to hand an
    attacker).
    """


@dataclass(frozen=True)
class AccessTokenClaims:
    user_id: uuid.UUID
    business_id: uuid.UUID
    role: str
    issued_at: datetime
    expires_at: datetime
    jti: str


def load_private_key(path: str | Path) -> str:
    return Path(path).read_text()


def load_public_key(path: str | Path) -> str:
    return Path(path).read_text()


def create_access_token(
    *,
    user_id: uuid.UUID,
    business_id: uuid.UUID,
    role: str,
    private_key: str,
    issuer: str,
    ttl_seconds: int,
) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": str(user_id),
        "biz": str(business_id),
        "role": role,
        "iss": issuer,
        "iat": now,
        "exp": now + timedelta(seconds=ttl_seconds),
        "jti": str(uuid.uuid4()),
    }
    return pyjwt.encode(payload, private_key, algorithm=ALGORITHM)


def decode_access_token(token: str, *, public_key: str, issuer: str) -> AccessTokenClaims:
    try:
        payload = pyjwt.decode(token, public_key, algorithms=[ALGORITHM], issuer=issuer)
    except pyjwt.PyJWTError as exc:
        raise TokenError(str(exc)) from exc

    try:
        return AccessTokenClaims(
            user_id=uuid.UUID(payload["sub"]),
            business_id=uuid.UUID(payload["biz"]),
            role=payload["role"],
            issued_at=datetime.fromtimestamp(payload["iat"], tz=UTC),
            expires_at=datetime.fromtimestamp(payload["exp"], tz=UTC),
            jti=payload["jti"],
        )
    except (KeyError, ValueError, TypeError) as exc:
        raise TokenError("Malformed token claims") from exc
