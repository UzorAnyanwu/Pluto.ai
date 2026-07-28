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
- **Business management** (`app/api/v1/businesses.py`): profile `GET`/`PATCH` (optimistic
  concurrency), team `GET`/`POST`/`PATCH`/`DELETE` — the owner can never be demoted or removed,
  enforced server-side. Phone number provisioning is **not** implemented (needs a real Twilio
  account — see `PROJECT_STATUS.md`).
- **AI agent config** (`app/api/v1/ai_agent_config.py`): `GET`/`PUT`, auto-creating working
  defaults on first read. `test-call` is **not** implemented (same Twilio blocker).
- **Customers (CRM)** (`app/api/v1/customers.py`): search/filter/paginated list, detail, tag and
  custom-field updates. No creation endpoint by design — see the module's docstring.
- **Webhooks** and **API Keys** (`app/api/v1/webhooks.py`, `app/api/v1/api_keys.py`): full CRUD,
  secrets shown once and SHA-256-hashed at rest.
- Tenant resolution + RBAC dependencies (`app/dependencies.py`): every protected route resolves a
  `TenantContext` from the JWT before touching the database — see `libs/pluto_core`'s README for
  how that ties into Row-Level Security.
- Structured error responses (`app/errors.py`) matching `docs/api/openapi.yaml`'s `Error` schema.

## Not yet implemented

Calendar, bookings (and their prerequisite Services/Employees/Locations, missing from
`openapi.yaml`), conversations, billing — Phase 2, Core Backend continues. Knowledge base is
blocked on an embeddings API key; phone number provisioning and AI test-call are blocked on a
Twilio account — see `PROJECT_STATUS.md`'s Technical Debt for why those were left undone rather
than stubbed.

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
