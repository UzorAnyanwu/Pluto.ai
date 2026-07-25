from functools import lru_cache

from pluto_core.config import Settings as CoreSettings
from pluto_core.config import get_settings as get_core_settings
from pluto_core.security.jwt import load_private_key, load_public_key


class ApiCoreSettings(CoreSettings):
    """Extends the shared settings with anything specific to this service. Kept as a thin
    subclass rather than a parallel settings object so every service reads the same env vars the
    same way — see pluto_core/config.py.
    """


@lru_cache
def get_settings() -> ApiCoreSettings:
    return ApiCoreSettings()


@lru_cache
def get_jwt_keys() -> tuple[str, str]:
    """Returns (private_key_pem, public_key_pem). Cached — these are read from disk once."""
    settings = get_settings()
    return (
        load_private_key(settings.jwt_private_key_path),
        load_public_key(settings.jwt_public_key_path),
    )


__all__ = ["ApiCoreSettings", "get_settings", "get_jwt_keys", "get_core_settings"]
