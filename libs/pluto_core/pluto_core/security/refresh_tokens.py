"""Opaque refresh token generation/hashing.

Deliberately *not* a JWT: a refresh token must be revocable and reuse-detectable server-side (see
docs/architecture/04-security-and-compliance.md §1), which means the server needs a record it can
look up and invalidate — a self-contained JWT can't be un-issued without a blocklist, which just
reinvents this table with extra steps. A high-entropy random token hashed with SHA-256 is the
standard approach here (unlike passwords, this is already 256 bits of entropy, so a slow KDF like
Argon2 buys nothing and only adds latency).
"""

import hashlib
import secrets


def generate_refresh_token() -> str:
    return secrets.token_urlsafe(48)


def hash_refresh_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
