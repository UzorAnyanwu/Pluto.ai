"""Importing this module registers every ORM model on `Base.metadata`, which is what Alembic
autogenerate (and the RLS-policy migration, which iterates tenant-scoped tables) relies on. Any
new model module must be imported here or it will silently be invisible to migrations.
"""

from pluto_core.db.models import (  # noqa: F401
    ai_agent,
    billing,
    crm,
    knowledge,
    platform,
    scheduling,
    tenancy,
    workflow,
)

__all__ = [
    "tenancy",
    "ai_agent",
    "knowledge",
    "crm",
    "scheduling",
    "workflow",
    "billing",
    "platform",
]
