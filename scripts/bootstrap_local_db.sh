#!/usr/bin/env bash
# Idempotent local dev database bootstrap: creates the dev database, the pgvector extension, and
# the least-privilege `pluto_app` role the application connects as (never the migration/owner
# role — see libs/pluto_core/migrations/rls_helpers.py for why this separation is what makes RLS
# actually enforce anything).
#
# Usage: PATH must include the postgresql@16 bin dir, e.g.:
#   PATH="/usr/local/opt/postgresql@16/bin:$PATH" ./scripts/bootstrap_local_db.sh

set -euo pipefail

DB_NAME="${PLUTO_DEV_DB:-pluto_ai_dev}"
APP_ROLE="${PLUTO_APP_ROLE:-pluto_app}"
APP_PASSWORD="${PLUTO_APP_PASSWORD:-pluto_app_dev_password}"

echo "==> Ensuring database '${DB_NAME}' exists"
if ! psql -lqt | cut -d '|' -f 1 | grep -qw "${DB_NAME}"; then
  createdb "${DB_NAME}"
  echo "    created."
else
  echo "    already exists."
fi

echo "==> Enabling pgvector extension"
psql -d "${DB_NAME}" -c "CREATE EXTENSION IF NOT EXISTS vector;"

echo "==> Ensuring role '${APP_ROLE}' exists (least-privilege, NOSUPERUSER, NOBYPASSRLS)"
psql -d "${DB_NAME}" -v ON_ERROR_STOP=1 <<SQL
DO \$\$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '${APP_ROLE}') THEN
    CREATE ROLE ${APP_ROLE} LOGIN PASSWORD '${APP_PASSWORD}'
      NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS;
  END IF;
END
\$\$;

GRANT CONNECT ON DATABASE ${DB_NAME} TO ${APP_ROLE};
GRANT USAGE ON SCHEMA public TO ${APP_ROLE};
SQL

echo "==> Done. Run 'alembic upgrade head' (from libs/pluto_core) next to create the schema,"
echo "    grant table privileges to ${APP_ROLE}, and enable Row-Level Security."
