# Pluto AI — Security & Compliance Architecture (v1)

Status: **Draft for review — Phase 1**
Last updated: 2026-07-24

## 1. AuthN — humans and machines are different problems

**Human users (dashboard):** JWT access tokens (short-lived, 15 min) + rotating refresh tokens
(httpOnly, secure, SameSite=strict cookie — never in localStorage, which is readable by any injected
script and turns an XSS bug into full account takeover). Refresh token rotation invalidates the
previous token on use, so a stolen refresh token that gets replayed after the legitimate client
already rotated it is detectable (reuse-detection → force logout + alert).

**Third-party integrations (Google Calendar, Outlook, CRMs):** standard OAuth2 authorization code
flow, tokens encrypted at rest (§5 of the data model doc), refreshed server-side, never exposed to
the frontend.

**Service-to-service (internal, e.g. `voice-gateway` → `ai-engine`):** short-lived signed service
tokens (not shared static API keys), scoped to the calling service's identity, issued by `api-core`'s
auth module. This means a compromised `voice-gateway` instance can't be used to call arbitrary
internal admin endpoints on `api-core` — its service token only carries the permissions that service
actually needs.

**External API access (customers integrating with our public API):** API keys, hashed at rest
(never store the raw key — same principle as password storage), scoped (read-only / read-write /
specific resource types), with `last_used_at` tracked so a business can audit and rotate stale keys.

## 2. AuthZ — RBAC matrix

| Role | Scope | Can manage AI config | Can manage users | Can view CRM/calls | Can manage billing | Can manage other businesses |
|---|---|---|---|---|---|---|
| `platform_admin` | Platform | — (not applicable) | Any business | Any business (with audit-logged access) | Platform-wide | Yes |
| `platform_support` | Platform | No | No | Read-only, audit-logged, time-boxed access grant | No | No |
| `agency_admin` | Agency | No (unless delegated per-business) | Agency staff + businesses under agency | Aggregated/anonymized analytics only, not raw conversation content, unless the business explicitly grants it | Agency's own billing | Businesses under their agency only |
| `owner` | Business | Yes | Yes (within business) | Yes | Yes | No |
| `admin` | Business | Yes | Yes, except cannot remove/demote the owner | Yes | View only | No |
| `staff` | Business | No | No | Yes, scoped to assigned locations if location-restricted | No | No |
| `read_only` | Business | No | No | Yes | No | No |

Platform-level access to a specific business's tenant data (`platform_admin`/`platform_support`
reading into a tenant's conversations for a support ticket) is never silent: every such cross-tenant
read is written to `audit_logs` with `actor_type = platform_staff`, and — for anything beyond
aggregate metrics — is a deliberate, logged support action, not an ambient capability. This is the
control that matters most for customer trust in a platform handling phone call recordings and
transcripts.

## 3. Tenant isolation enforcement (implementation of Decision 2)

Layered, not single-point-of-failure:

1. **Database — Postgres RLS** (primary control, per `02-data-model.md` §4): every tenant table has
   a policy tying rows to `current_setting('app.current_tenant')`. This holds even if application
   code has a bug.
2. **Application layer** — a request-scoped `TenantContext` is required to construct any repository
   call; there is no code path that queries a tenant table without one (enforced by code review +
   a lint rule that flags direct ORM session usage outside the repository layer).
3. **API layer** — every authenticated request's JWT `business_id` claim is cross-checked against
   the `business_id` in the URL/payload for every resource-scoped endpoint; a mismatch is a 403, not
   a silently-scoped query.

## 4. Rate limiting

Two layers:
- **Edge (Cloudflare):** coarse, IP/ASN-based, protects against volumetric abuse before it reaches
  our infrastructure (relevant given inbound telephony/webhook endpoints are public by necessity).
- **Application (Redis token bucket, per `business_id` + per `api_key`):** protects against a single
  tenant's misbehaving integration or a compromised API key from degrading service for other
  tenants — critical in a shared-infrastructure multi-tenant system where the whole point of
  Decision 2 (§4 of the system architecture doc) is that tenants share compute and DB capacity.
  Limits are tiered by subscription plan, not one-size-fits-all.

## 5. Encryption

- **In transit:** TLS 1.2+ everywhere, including internal service-to-service traffic within the VPC
  (not "it's a private network so plaintext is fine" — defense in depth against a compromised
  workload in the same VPC).
- **At rest:** RDS encryption (AES-256, AWS-managed keys) as the baseline; field-level envelope
  encryption via AWS KMS for OAuth tokens, integration secrets, and any field classified as a
  credential (per `02-data-model.md` §5).
- **Secrets management:** AWS Secrets Manager for service credentials and API keys (Twilio,
  Deepgram, ElevenLabs, OpenAI/Anthropic/Gemini, Stripe); nothing sensitive in environment files
  committed to the repo, ever — `.env.example` files document required variables with placeholder
  values only.

## 6. Compliance posture

**SOC2-readiness (architectural prerequisites, not a certification itself — that requires audit
plus operational maturity beyond architecture):**
- Complete audit trail (§4 of data model doc) for all data access and mutation.
- Documented access control model (this doc) with least-privilege service tokens.
- Encryption at rest and in transit (§5 above).
- Change management via CI/CD with required review (see infra doc) — no direct production
  database or infra changes outside the pipeline.

**GDPR-aware architecture:**
- **Right to erasure:** because we use soft deletes + an audit log by default (§4 of data model
  doc), a genuine erasure request is a distinct, explicit hard-delete job — not the default delete
  path — that cascades through `customers`, their `conversations`/`calls`/`recordings`/`transcripts`,
  and scrubs (not deletes — replaces with a tombstone reference) the `audit_logs` rows that
  reference them, preserving audit integrity for unrelated events while honoring erasure for the
  data subject.
- **Data residency:** the schema and infra are designed so a future EU-region deployment (separate
  RDS instance + S3 bucket in `eu-west-1`, tenant routed by `business.data_region`) doesn't require a
  schema change — this is exactly why tenant/business primary keys are UUIDs, not
  instance-sequential integers (Decision 4, system architecture doc).
- **Consent & call recording disclosure:** call recording consent requirements are jurisdiction-
  dependent (one-party vs. two-party consent). `ai_agent_configs` includes a
  `recording_disclosure_policy` field, and `voice-gateway` plays the appropriate disclosure prompt
  based on the business's configured jurisdiction before recording begins — this is a legal
  requirement in two-party-consent jurisdictions, not optional polish.

## 7. API security baseline

- Input validation at the boundary via Pydantic models (FastAPI) / Zod schemas (Next.js) — reject
  malformed input before it reaches business logic, never rely on the database to catch bad data.
- Parameterized queries only (SQLAlchemy ORM/Core, never raw string-interpolated SQL) — no SQL
  injection surface by construction.
- Webhook payloads we send out are HMAC-signed (per-business secret, per `webhooks` table) so
  receivers can verify authenticity; webhook payloads we receive (Twilio, Stripe, calendar
  providers) are signature-verified before processing, not trusted by URL obscurity.
- CORS restricted to known frontend origins; no wildcard `*` in production.
- Dependency scanning (`pip-audit` / `npm audit`) and container image scanning in CI (see infra
  doc) — supply-chain hygiene as a pipeline gate, not a manual periodic task.

---

Next: [`05-infra-and-observability.md`](./05-infra-and-observability.md)
