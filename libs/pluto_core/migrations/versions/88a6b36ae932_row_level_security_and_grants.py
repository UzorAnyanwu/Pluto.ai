"""row level security and grants

Revision ID: 88a6b36ae932
Revises: 77eda2266198
Create Date: 2026-07-25 07:35:27.816117

Enables Postgres Row-Level Security on every tenant-owned table, creates the one narrow,
audited RLS bypass the login flow needs (see rls_helpers.py's module docstring for the full
reasoning), and grants the least-privilege `pluto_app` runtime role exactly the access it needs —
nothing more. `pluto_app` must already exist (via scripts/bootstrap_local_db.sh locally, or the
equivalent RDS bootstrap in staging/production) before this migration runs; it fails fast with a
clear error otherwise rather than a cryptic GRANT failure.

See docs/architecture/04-security-and-compliance.md §3.
"""
from collections.abc import Sequence

from alembic import op
from rls_helpers import TENANT_TABLES, disable_tenant_rls, enable_tenant_rls

# revision identifiers, used by Alembic.
revision: str = '88a6b36ae932'
down_revision: str | None = '71b28bb643db'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

APP_ROLE = "pluto_app"


def upgrade() -> None:
    op.execute(
        f"""
        DO $$
        BEGIN
          IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '{APP_ROLE}') THEN
            RAISE EXCEPTION
              'Role "{APP_ROLE}" does not exist. Run scripts/bootstrap_local_db.sh (dev) or the '
              'equivalent RDS bootstrap (staging/production) before applying this migration.';
          END IF;
        END
        $$;
        """
    )

    for table_name, tenant_column in TENANT_TABLES:
        enable_tenant_rls(table_name, tenant_column)

    # The one narrow, audited RLS bypass: login needs to resolve `business_id` from an email
    # address before any tenant context exists to set. Owned by the migration role (not
    # `pluto_app`), so it bypasses RLS by ordinary Postgres owner semantics without needing
    # `FORCE ROW LEVEL SECURITY` anywhere — see rls_helpers.py for the full reasoning on why that
    # matters. `pluto_app` itself still cannot read `users` unscoped; this function is its only
    # narrow, reviewed escape hatch.
    op.execute(
        """
        CREATE FUNCTION auth_resolve_business_by_email(p_email text)
        RETURNS TABLE(business_id uuid, user_id uuid, hashed_password text, role text)
        LANGUAGE sql
        SECURITY DEFINER
        STABLE
        SET search_path = public
        AS $$
          SELECT business_id, id, hashed_password, role::text
          FROM users
          WHERE email = p_email AND deleted_at IS NULL;
        $$;
        """
    )
    op.execute("REVOKE ALL ON FUNCTION auth_resolve_business_by_email(text) FROM PUBLIC;")
    op.execute(f"GRANT EXECUTE ON FUNCTION auth_resolve_business_by_email(text) TO {APP_ROLE};")

    # Baseline DML privileges on every existing table except alembic's own bookkeeping table
    # (the app must never be able to alter migration state) and refresh_tokens/agencies/
    # agency_users/platform_users/subscriptions/invoices/usage_records/feature_flags/audit_logs
    # get the same grant here too — RLS is opt-in per table above, but ordinary GRANT-based access
    # control still applies to all of them; see rls_helpers.py for why each non-RLS table is safe
    # to access this way at the application layer.
    op.execute(
        f"GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO {APP_ROLE};"
    )
    op.execute(f"REVOKE ALL ON alembic_version FROM {APP_ROLE};")

    # Applies to tables created by *future* migrations run by this same (migration) role, so we
    # don't need a fresh GRANT-everything migration every time the schema grows.
    op.execute(
        f"ALTER DEFAULT PRIVILEGES IN SCHEMA public "
        f"GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO {APP_ROLE};"
    )


def downgrade() -> None:
    op.execute(f"ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON TABLES FROM {APP_ROLE};")
    op.execute(f"REVOKE ALL ON ALL TABLES IN SCHEMA public FROM {APP_ROLE};")
    op.execute(f"REVOKE ALL ON FUNCTION auth_resolve_business_by_email(text) FROM {APP_ROLE};")
    op.execute("DROP FUNCTION IF EXISTS auth_resolve_business_by_email(text);")

    for table_name, _ in reversed(TENANT_TABLES):
        disable_tenant_rls(table_name)
