"""Shared settings loaded from the environment. Every service imports this rather than reading
os.environ directly, so there is exactly one place that defines what configuration exists and what
its defaults/types are.
"""

from functools import lru_cache

from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    environment: str = Field(default="development", description="development | staging | production")

    # Application runtime database connection (asyncpg) — used by request-serving services.
    database_url: PostgresDsn = Field(
        default="postgresql+asyncpg://pluto_app:pluto_app_dev_password@localhost:5432/pluto_ai_dev"
    )

    # Migration/admin database connection (psycopg, sync) — used only by Alembic and bootstrap
    # scripts, never by application request handlers. Deliberately a separate role from
    # `database_url` per docs/architecture/04-security-and-compliance.md's least-privilege
    # principle: the app role must never have DDL privileges.
    migration_database_url: PostgresDsn = Field(
        default="postgresql+psycopg://postgres@localhost:5432/pluto_ai_dev"
    )

    redis_url: RedisDsn = Field(default="redis://localhost:6379/0")

    # JWT signing — RS256 keypair so any service can verify tokens with only the public key,
    # while only api-core (the issuer) holds the private key. See
    # docs/architecture/04-security-and-compliance.md §1.
    jwt_private_key_path: str = Field(default="secrets/jwt_private_key.pem")
    jwt_public_key_path: str = Field(default="secrets/jwt_public_key.pem")
    jwt_issuer: str = Field(default="pluto-ai")
    access_token_ttl_seconds: int = Field(default=900, description="15 minutes")
    refresh_token_ttl_seconds: int = Field(default=60 * 60 * 24 * 30, description="30 days")


@lru_cache
def get_settings() -> Settings:
    return Settings()
