# Pluto AI — Project Status

This file is the single source of truth for where the project is. Update it at the start/end of
every work session — every future session should be able to read this file alone and know exactly
where things stand.

## Current Phase
**Phase 1 — Project Planning & System Architecture**

## Current Sprint
Sprint 0 — Architecture finalization

## Current Milestone
Get the Phase 1 architecture docs (`docs/architecture/`) reviewed and approved before any service
code is written.

## Completed Modules
- Repository scaffolding (monorepo folder structure, git initialized, scoped correctly to
  `/Users/macbookpro/Pluto_Ai`)
- System architecture decision doc (`docs/architecture/01-system-architecture.md`)
- Data model overview (`docs/architecture/02-data-model.md`)
- AI engine & voice pipeline architecture (`docs/architecture/03-ai-and-voice-architecture.md`)
- Security & compliance architecture (`docs/architecture/04-security-and-compliance.md`)
- Infra, deployment & observability architecture (`docs/architecture/05-infra-and-observability.md`)

## Outstanding Tasks (Phase 1, remaining)
- [ ] Architecture review — walk through all 5 docs, confirm or override each numbered decision
      (especially: modular monolith vs. earlier microservice split, ECS Fargate vs. EKS, single
      Next.js app vs. three apps)
- [ ] Business requirements doc (detailed user flows per persona: business owner, front-desk staff,
      agency reseller, platform admin)
- [ ] Technical specifications: OpenAPI contract skeleton for `api-core`, initial Alembic migration
      plan derived from `02-data-model.md`
- [ ] CI/CD pipeline implementation (`.github/workflows/`) per `05-infra-and-observability.md` §3
- [ ] Terraform module scaffolding per `05-infra-and-observability.md` §2 (dev environment first)
- [ ] Authentication module implementation (JWT + refresh rotation + RBAC per
      `04-security-and-compliance.md`)

## Not Started (Phase 2+)
Core Backend · Core Frontend · Multi-tenancy implementation · Business Management · Knowledge Base ·
AI Engine · Voice Engine · Calendar · CRM · Bookings · Workflow Engine · Analytics · Payments ·
Agency Features · White-label · Admin Panel · Enterprise Features · Performance/Security hardening ·
Production Deployment

## Technical Debt
None yet — nothing has been built. (This section should never be empty once Phase 2 starts; if it
looks empty later, that's a sign debt isn't being tracked, not that there isn't any.)

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
