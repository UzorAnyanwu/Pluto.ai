# services/api-core

The core FastAPI monolith: auth & RBAC, tenants/businesses, CRM, bookings/calendar, workflow
engine, billing, and the platform admin API. Internally organized into bounded-context modules with
no cross-module internal imports — only through module-level service interfaces — so any module can
be extracted into its own service later without a rewrite. See
[`docs/architecture/01-system-architecture.md`](../../docs/architecture/01-system-architecture.md) §3.

Not yet implemented — scaffolding lands in Phase 2 (Core Backend).
