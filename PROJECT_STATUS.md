# Pluto AI — Project Status

This file is the single source of truth for where the project is. Update it at the start/end of
every work session — every future session should be able to read this file alone and know exactly
where things stand.

## Current Phase
**Phase 1 — Project Planning & System Architecture** (architecture approved; finishing remaining
Phase 1 deliverables before Phase 2 application code starts)

## Current Sprint
Sprint 1 — Requirements, specifications, and foundational infra/DB/auth setup

## Current Milestone
Stand up CI/CD, Terraform (dev environment), the initial database migrations, and the auth module —
the last Phase 1 items before Phase 2 (Core Backend/Frontend) begins.

## Completed Modules
- Repository scaffolding (monorepo folder structure, git initialized, scoped correctly to
  `/Users/macbookpro/Pluto_Ai`)
- System architecture decision doc (`docs/architecture/01-system-architecture.md`) — **reviewed and
  approved**
- Data model overview (`docs/architecture/02-data-model.md`)
- AI engine & voice pipeline architecture (`docs/architecture/03-ai-and-voice-architecture.md`)
- Security & compliance architecture (`docs/architecture/04-security-and-compliance.md`)
- Infra, deployment & observability architecture (`docs/architecture/05-infra-and-observability.md`)
- Business requirements (`docs/product/01-business-requirements.md`) — personas, functional/non-
  functional requirements, and the **voice-first MVP scope decision** (WhatsApp/SMS/email/chat
  deferred to Phase 3+)
- User flows (`docs/product/02-user-flows.md`) — onboarding, inbound call, booking, escalation,
  agency provisioning, billing lifecycle, platform support access
- Technical specifications (`docs/product/03-technical-specifications.md`) — API versioning, error
  format, pagination, idempotency, webhook delivery, migration strategy, testing contract
- OpenAPI contract for the MVP `api-core` surface (`docs/api/openapi.yaml`) — validated against the
  OpenAPI 3.0.3 spec (28 paths, 28 schemas): auth, businesses, team, AI agent config, knowledge base,
  calendar, bookings, customers, conversations, webhooks, API keys, billing

## Outstanding Tasks (Phase 1, remaining)
- [ ] CI/CD pipeline implementation (`.github/workflows/`) per `05-infra-and-observability.md` §3
- [ ] Terraform module scaffolding per `05-infra-and-observability.md` §2 (dev environment first)
- [ ] Database Design: concrete SQLAlchemy models + initial Alembic migrations derived from
      `02-data-model.md`, with RLS policies per table (per `03-technical-specifications.md` §8)
- [ ] Authentication module implementation (JWT + refresh rotation + RBAC per
      `04-security-and-compliance.md`, contract in `openapi.yaml`'s `Auth` paths)
- [ ] Local dev environment (`infra/docker/docker-compose.yml`): Postgres+pgvector, Redis, localstack

## Not Started (Phase 2+)
Core Backend · Core Frontend · Multi-tenancy implementation · Business Management · Knowledge Base ·
AI Engine · Voice Engine · Calendar · CRM · Bookings · Workflow Engine · Analytics · Payments ·
Agency Features · White-label · Admin Panel · Enterprise Features · Performance/Security hardening ·
Production Deployment

## Technical Debt
- `apps/admin` and `apps/agency` are placeholder directories pending a final decision on the
  single-Next.js-app-with-route-groups recommendation (`01-system-architecture.md` §8); they should
  be deleted (not built out) once Phase 2 frontend work confirms that direction.

## Key Decisions Log
See `docs/architecture/01-system-architecture.md` §3–10 for the full reasoning. Quick index:
1. Modular monolith (`api-core`) + day-1 extraction of `voice-gateway` and `workers` — not full
   microservices, not a single undifferentiated monolith.
2. Multi-tenancy: shared schema + `business_id` + Postgres RLS — not database-per-tenant.
3. Event backbone: SNS/SQS for cross-service domain events — Kafka deferred until volume justifies it.
4. All tenant-owned primary keys: UUIDv7.
5. Compute: ECS Fargate — EKS deferred until a concrete need (portability or Fargate limits) appears.
6. Frontend: one Next.js app, role-based route groups — not three separate apps.
7. Voice: dedicated stateful `voice-gateway` service, call-affinity scaling, streaming everywhere
   to hit the 2s p95 latency budget.
8. RAG storage: pgvector, partitioned per-tenant — not a dedicated vector DB.
9. MVP scope is **voice-first**: WhatsApp/SMS/email/web-chat channels are sequenced into Phase 3,
   not built simultaneously with voice (`docs/product/01-business-requirements.md` §4).
10. API versioning is URL path-based (`/v1`); pagination is offset-based for MVP; every mutating
    create endpoint with real-world side effects supports `Idempotency-Key`
    (`docs/product/03-technical-specifications.md`).
