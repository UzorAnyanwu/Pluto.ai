"""Generic high-entropy secret generation/hashing — the same pattern as
`refresh_tokens.py` (opaque token, SHA-256 hash for storage, never store the raw value), used
wherever a caller needs a bearer secret shown once: webhook signing secrets, API keys. Kept
separate from `refresh_tokens.py` because callers there want refresh-token-specific naming; this
module is the generic primitive both build on conceptually.
"""

import hashlib
import secrets


def generate_secret(*, prefix: str = "", nbytes: int = 32) -> str:
    return f"{prefix}{secrets.token_urlsafe(nbytes)}"


def hash_secret(raw_secret: str) -> str:
    return hashlib.sha256(raw_secret.encode("utf-8")).hexdigest()
