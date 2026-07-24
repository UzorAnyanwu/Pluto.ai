# Pluto AI — Technical Specifications (v1)

Status: **Draft for review — Phase 1**
Last updated: 2026-07-24

This is the contract layer between the architecture (`docs/architecture/`) and actual
implementation. It defines conventions every endpoint and service must follow, so consistency is a
rule engineers check against, not a matter of individual taste per PR. The concrete API surface it
governs is [`docs/api/openapi.yaml`](../api/openapi.yaml) (validated against the OpenAPI 3.0.3 spec).

## 1. API versioning

URL path versioning: `/v1/...`. A breaking change (removed field, changed type, changed required-ness,
removed endpoint) requires a new version (`/v2/...`) served alongside `/v1/...` for a documented
deprecation window (minimum 6 months for anything with active external API-key usage) — never a
breaking change shipped silently into an existing version. Additive changes (new optional field, new
endpoint) do not require a version bump.

## 2. Error format

Every error response uses the shape defined in `openapi.yaml`'s `Error` schema:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "start_at must be in the future",
    "details": { "field": "start_at" },
    "request_id": "01998f3e-..."
  }
}
```

`code` is a stable, machine-readable enum (`VALIDATION_ERROR`, `NOT_FOUND`, `CONFLICT`,
`UNAUTHORIZED`, `FORBIDDEN`, `RATE_LIMITED`, `INTERNAL_ERROR`) — frontend code branches on `code`,
never on parsing `message` (which is for humans and can change wording without breaking clients).
`request_id` is the OpenTelemetry trace ID (`05-infra-and-observability.md` §4), so a customer-reported
error can be looked up directly in traces/logs without asking them to reproduce it.

## 3. Pagination

Offset-based (`page`, `page_size`, per the `Pagination` schema) for MVP list endpoints — simple,
matches the query patterns in the OpenAPI spec (dashboard tables with page controls). Cursor-based
pagination is adopted later specifically for any endpoint expected to page through very large,
frequently-mutating result sets (a realistic future case: platform-admin cross-tenant audit log
export) — not adopted platform-wide preemptively, since it adds client complexity that offset
pagination doesn't need for bounded, UI-driven lists.

## 4. Request validation

FastAPI + Pydantic models validate every request body/query/path parameter at the boundary; no
handler function receives unvalidated input. Every Pydantic model has an equivalent Zod schema on
the frontend (`packages/shared-types`, generated from `openapi.yaml`, not hand-duplicated) so
frontend form validation and backend validation can never silently drift apart.

## 5. Authentication & tenant resolution (implementation contract for `04-security-and-compliance.md`)

Every authenticated request:
1. Bearer JWT validated (signature, expiry, not-yet-revoked).
2. `business_id`, `user_id`, `role` claims extracted into a `TenantContext`.
3. `TenantContext` is injected via FastAPI dependency injection into every route handler — there is
   no handler that can construct a DB session without one (enforced by a repository-layer wrapper
   that requires `TenantContext` as a constructor argument, not an optional one).
4. `SET LOCAL app.current_tenant` issued at transaction start, per the RLS design.

Endpoints under `/businesses/me/...` resolve `me` to the caller's `business_id` from the
`TenantContext` — the API never accepts a client-supplied `business_id` for these routes, precisely
to remove the class of bug where a client could pass a different business's ID and rely on the
server "trusting" it.

## 6. Idempotency

All `POST` endpoints that create a resource with real-world side effects (bookings, phone number
provisioning, checkout sessions) accept an optional `Idempotency-Key` header. If a request with a
previously-seen key (same business, same endpoint, within a 24h window) arrives, the original
response is replayed rather than the action repeated. This matters concretely for this product: a
flaky mobile network causing a dashboard retry on "create booking" must never double-book a
customer, and a Twilio webhook retry (Twilio explicitly documents at-least-once delivery) must never
double-process a call-completed event.

## 7. Webhook delivery (outbound, to customers) and receipt (inbound, from providers)

**Outbound** (our webhooks to customer-configured `target_url`s): payload signed with HMAC-SHA256
using the per-webhook secret (`X-Pluto-Signature` header); delivery retried with exponential backoff
(5 attempts over ~1 hour) on non-2xx response; a webhook that fails all retries is marked `failing`
in the dashboard so the business notices, rather than silently dropped.

**Inbound** (Twilio, Stripe, calendar provider webhooks): signature verified before any processing
(Twilio request signature validation, Stripe signature header) — a request that fails signature
verification is rejected with 400 before touching any business logic, never processed "just to be
safe."

## 8. Database migration strategy (Alembic — bridges to the Database Design phase)

This doc defines the *process*; the actual initial migration set (concrete tables, columns,
indexes, RLS policies) is the Database Design phase deliverable that follows this doc, built
directly from `docs/architecture/02-data-model.md`.

- One Alembic migration per logical change, reversible (`downgrade()` implemented, not `pass`) —
  a migration that can't be rolled back is a deployment risk we don't accept.
- Expand/contract pattern for any change that isn't purely additive (see
  `05-infra-and-observability.md` §3): add nullable → backfill → enforce constraint/drop old →
  each as a separate migration/deploy, so an application rollback never requires an incompatible
  database rollback.
- RLS policies are defined in migrations alongside the tables they protect — a table is never
  created without its policy in the same migration, so there is no window where a tenant table
  exists without isolation enforced.
- CI runs every migration against a throwaway Postgres instance (up, then down, then up again) on
  every PR that touches `alembic/versions/` — a migration that doesn't reverse cleanly fails CI
  before merge.

## 9. Testing contract

- **Unit tests (pytest/vitest):** every module's business logic, mocking only true external
  boundaries (Twilio, Stripe, LLM providers) — never mocking the database for logic that depends on
  RLS behavior, since that's exactly the kind of test that would pass while the real tenant-isolation
  guarantee is broken.
- **Integration tests:** run against a real Postgres instance (via `infra/docker/docker-compose.yml`
  once it exists) with RLS enabled, specifically to catch tenant-isolation regressions — this is the
  test suite's single highest-priority responsibility given the architecture's security model rests
  on RLS actually being enforced.
- **E2E (Playwright):** the onboarding flow (`docs/product/02-user-flows.md` §1) end-to-end,
  including the test-call step, is a required E2E test before any release — it's the activation
  path and the one flow that must never silently break.
- **Voice pipeline load testing:** a dedicated load-testing plan for `voice-gateway` concurrent-call
  capacity is scheduled explicitly in Phase 2 (flagged as an open unknown in
  `05-infra-and-observability.md` §7) — not deferred indefinitely.

## 10. Definition of done (applies to every module going forward)

A module is not "done" until: endpoints match `openapi.yaml` exactly (spec is the contract, not
documentation-after-the-fact), RLS policy exists and has a passing isolation test, unit + integration
tests pass in CI, OpenTelemetry spans are emitted for its operations, and its README is updated to
remove the "Not yet implemented" line these scaffold READMEs currently carry.

---

This closes out the Phase 1 written-specification set. Per `PROJECT_STATUS.md`, next up: CI/CD
pipeline implementation, Terraform scaffolding for the `dev` environment, and the Database
Design + Authentication modules — the first actual application code in this repository.
