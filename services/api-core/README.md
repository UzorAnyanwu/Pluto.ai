# services/api-core

The core FastAPI monolith: auth & RBAC, tenants/businesses, CRM, bookings/calendar, workflow
engine, billing, and the platform admin API. Internally organized into bounded-context modules with
no cross-module internal imports — only through module-level service interfaces — so any module can
be extracted into its own service later without a rewrite. See
[`docs/architecture/01-system-architecture.md`](../../docs/architecture/01-system-architecture.md) §3.

## Implemented

- **Auth module** (`app/api/v1/auth.py`): register, login, refresh (rotation + reuse detection),
  logout — matching the `Auth` tag in [`docs/api/openapi.yaml`](../../docs/api/openapi.yaml).
  RS256 JWT access tokens, Argon2id password hashing, Redis-backed rate limiting on
  register/login. See [`docs/architecture/04-security-and-compliance.md`](../../docs/architecture/04-security-and-compliance.md) §1.
- Tenant resolution + RBAC dependencies (`app/dependencies.py`): every protected route resolves a
  `TenantContext` from the JWT before touching the database — see `libs/pluto_core`'s README for
  how that ties into Row-Level Security.
- Structured error responses (`app/errors.py`) matching `docs/api/openapi.yaml`'s `Error` schema.

## Not yet implemented

Everything else in `openapi.yaml` (businesses, team, AI agent config, knowledge base, calendar,
bookings, customers, conversations, webhooks, API keys, billing) — Phase 2, Core Backend.

## Local development

```bash
# From the repo root, with Postgres+Redis running and migrations applied (see libs/pluto_core's
# README) and a JWT keypair generated (see scripts/bootstrap_local_db.sh's output for how the
# dev keypair was generated into secrets/ — gitignored, regenerate locally):
python3 -m venv .venv && source .venv/bin/activate
pip install -e libs/pluto_core -e services/api-core

cd services/api-core
uvicorn app.main:app --reload
# → http://localhost:8000/docs
```

### Tests

```bash
cd services/api-core
pytest tests/ -v
```

Runs against a **real** Postgres with RLS enabled and a real Redis — never mocks the database, per
[`docs/product/03-technical-specifications.md`](../../docs/product/03-technical-specifications.md) §9.
`tests/test_rls_isolation.py` is the most important file in this test suite: it proves tenant
isolation actually holds through the application's own code path, not just in the raw-SQL check
done while writing the RLS migration.
