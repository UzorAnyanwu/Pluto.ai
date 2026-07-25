import os
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))  # makes rls_helpers importable from versions/

from pluto_core.db.base import Base  # noqa: E402
from pluto_core.db.models import *  # noqa: E402,F401,F403  (registers every model on Base.metadata)

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_url() -> str:
    """Migrations always run against `MIGRATION_DATABASE_URL` (a privileged, DDL-capable role),
    never `DATABASE_URL` (the least-privilege application runtime role) — see
    docs/product/03-technical-specifications.md §8 and pluto_core/config.py.
    """
    url = os.environ.get("MIGRATION_DATABASE_URL")
    if url:
        return url
    from pluto_core.config import get_settings

    return str(get_settings().migration_database_url)


def run_migrations_offline() -> None:
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(configuration, prefix="sqlalchemy.", poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
