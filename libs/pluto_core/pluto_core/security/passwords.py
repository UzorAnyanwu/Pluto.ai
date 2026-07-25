"""Password hashing via Argon2id — the modern recommended default (OWASP), stronger against
GPU/ASIC cracking than bcrypt at equivalent tuning cost. Used for business `User`, `PlatformUser`,
and `AgencyUser` passwords, and for API key secrets (see api_keys.py).
"""

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

_hasher = PasswordHasher()


def hash_password(raw_password: str) -> str:
    return _hasher.hash(raw_password)


def verify_password(raw_password: str, hashed_password: str) -> bool:
    try:
        return _hasher.verify(hashed_password, raw_password)
    except VerifyMismatchError:
        return False


def needs_rehash(hashed_password: str) -> bool:
    """True if the hash was created with outdated parameters and should be regenerated on next
    successful login — lets us raise Argon2 cost parameters over time without a forced mass
    password reset.
    """
    return _hasher.check_needs_rehash(hashed_password)
