"""Helpers shared by migrations that enable/disable Postgres Row-Level Security.

Design notes (see docs/architecture/04-security-and-compliance.md §3 for the full rationale):

- Tables are owned by the migration role (whoever runs `alembic upgrade`, e.g. the local
  superuser in dev, a dedicated `pluto_migrator` role in production). The application connects as
  `pluto_app`, a separate, unprivileged, non-owner role. RLS applies to any role that is not the
  table owner and not a superuser, so `pluto_app` is always subject to these policies — even a
  forgotten `WHERE business_id = ...` in application code cannot leak cross-tenant rows.
- We deliberately do NOT use `FORCE ROW LEVEL SECURITY`. Forcing would also apply RLS to the
  table owner, which would break the one narrow, intentional bypass this schema relies on: the
  `auth_resolve_business_by_email` SECURITY DEFINER function (see
  0002_row_level_security_and_grants.py), which needs to read `users` across all tenants during
  login — before a tenant context exists to set. That function is owned by the same (owner) role
  as the tables, a small, reviewed, single-purpose piece of SQL — an intentional, narrow, audited
  exception, not a general bypass, since `pluto_app` itself still can't read `users` unscoped.
"""

from alembic import op

_POLICY_NAME = "tenant_isolation"


def enable_tenant_rls(table_name: str, tenant_column: str = "business_id") -> None:
    op.execute(f"ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY;")
    op.execute(
        f"""
        CREATE POLICY {_POLICY_NAME} ON {table_name}
        USING ({tenant_column} = NULLIF(current_setting('app.current_tenant', true), '')::uuid)
        WITH CHECK ({tenant_column} = NULLIF(current_setting('app.current_tenant', true), '')::uuid);
        """
    )


def disable_tenant_rls(table_name: str) -> None:
    op.execute(f"DROP POLICY IF EXISTS {_POLICY_NAME} ON {table_name};")
    op.execute(f"ALTER TABLE {table_name} DISABLE ROW LEVEL SECURITY;")


# Every table protected by the standard business_id-scoped tenant_isolation policy. `businesses`
# itself uses `id` as its own tenant column (a business IS a tenant, it doesn't have a separate
# business_id pointing at itself). `users` is here too (see the module docstring for how login
# still works despite RLS being enabled on it).
TENANT_TABLES: list[tuple[str, str]] = [
    ("businesses", "id"),
    ("users", "business_id"),
    ("ai_agent_configs", "business_id"),
    ("knowledge_sources", "business_id"),
    ("knowledge_chunks", "business_id"),
    ("customers", "business_id"),
    ("conversations", "business_id"),
    ("messages", "business_id"),
    ("calls", "business_id"),
    ("call_recordings", "business_id"),
    ("call_transcripts", "business_id"),
    ("leads", "business_id"),
    ("conversation_events", "business_id"),
    ("locations", "business_id"),
    ("services", "business_id"),
    ("employees", "business_id"),
    ("calendar_connections", "business_id"),
    ("bookings", "business_id"),
    ("workflows", "business_id"),
    ("workflow_runs", "business_id"),
    ("webhooks", "business_id"),
    ("api_keys", "business_id"),
    ("feature_flag_overrides", "business_id"),
]

# Deliberately excluded from RLS, each for a documented reason:
#   - refresh_tokens: looked up by token_hash before any tenant context exists (that's the whole
#     point of a refresh token); scoped at the application layer instead.
#   - agencies, agency_users: Phase 4 (white-label) feature, not exposed by any MVP endpoint yet;
#     will get their own agency-scoped RLS policy (tenant column = agency's own id, mirroring how
#     `businesses` uses `id`) when that phase starts.
#   - platform_users: platform staff are not tenant data; access to *tenant* data by platform
#     staff goes through the explicit audited support-access flow
#     (docs/product/02-user-flows.md §7), not through this table's own RLS.
#   - subscriptions, invoices, usage_records: can belong to a business OR an agency (see
#     models/billing.py's check constraint) — a single-column tenant policy doesn't fit; scoped at
#     the application layer for MVP. Revisit alongside the agency RLS policy work above.
#   - feature_flags: platform-wide defaults, not tenant data.
#   - audit_logs: needs a dual policy (tenant users see their own business's rows; platform_admin/
#     platform_support see everything, audited) — deferred to the admin-panel milestone
#     (Phase 4) rather than half-built now. Tracked in PROJECT_STATUS.md technical debt.
