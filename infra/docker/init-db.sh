#!/usr/bin/env bash
# Runs once, automatically, on first container start (docker-entrypoint-initdb.d convention).
# Mirrors scripts/bootstrap_local_db.sh's role setup for the Dockerized path — see
# libs/pluto_core/migrations/rls_helpers.py for why the app must run as a non-owner role.
set -euo pipefail

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-SQL
  CREATE EXTENSION IF NOT EXISTS vector;

  DO \$\$
  BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'pluto_app') THEN
      CREATE ROLE pluto_app LOGIN PASSWORD 'pluto_app_dev_password'
        NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS;
    END IF;
  END
  \$\$;

  GRANT CONNECT ON DATABASE "$POSTGRES_DB" TO pluto_app;
  GRANT USAGE ON SCHEMA public TO pluto_app;
SQL
