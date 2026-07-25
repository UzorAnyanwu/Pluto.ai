# Pluto AI

AI Business Operating System for SMEs — starting as an AI receptionist platform (voice, WhatsApp,
SMS, web chat) with booking, CRM, and workflow automation, built as a multi-tenant SaaS with
white-label/agency support from day one.

**Status:** Phase 1 complete, Phase 2 (Core Backend) underway. Database schema + Row-Level
Security and the authentication module are built and passing tests against a real Postgres +
Redis. See [`PROJECT_STATUS.md`](./PROJECT_STATUS.md) for exactly where things stand and
[`docs/architecture/`](./docs/architecture/) for the full system design and the reasoning behind
every major decision.

## Backend quickstart

```bash
# 1. Postgres 16 + pgvector, and Redis — via infra/docker/docker-compose.yml if you have Docker,
#    or natively (see scripts/bootstrap_local_db.sh, which is what this repo's own dev setup used)
./scripts/bootstrap_local_db.sh

# 2. Python workspace
python3 -m venv .venv && source .venv/bin/activate
pip install -e libs/pluto_core -e services/api-core

# 3. Migrations (schema + Row-Level Security)
export MIGRATION_DATABASE_URL="postgresql+psycopg://<migration-role>@localhost:5432/pluto_ai_dev"
cd libs/pluto_core && alembic upgrade head && cd ../..

# 4. Run it
cd services/api-core && uvicorn app.main:app --reload   # → http://localhost:8000/docs
```

See [`libs/pluto_core/README.md`](./libs/pluto_core/README.md) and
[`services/api-core/README.md`](./services/api-core/README.md) for details, and
`services/api-core/tests/` for the test suite (`pytest tests/ -v`).

## Start here

1. [`PROJECT_STATUS.md`](./PROJECT_STATUS.md) — current phase, sprint, and outstanding tasks.
2. [`docs/architecture/01-system-architecture.md`](./docs/architecture/01-system-architecture.md) —
   overall system design and the tradeoffs behind it.
3. [`docs/architecture/02-data-model.md`](./docs/architecture/02-data-model.md) — entities and
   tenancy model.
4. [`docs/architecture/03-ai-and-voice-architecture.md`](./docs/architecture/03-ai-and-voice-architecture.md) —
   AI orchestration and the voice pipeline's latency budget.
5. [`docs/architecture/04-security-and-compliance.md`](./docs/architecture/04-security-and-compliance.md)
6. [`docs/architecture/05-infra-and-observability.md`](./docs/architecture/05-infra-and-observability.md)
7. [`docs/product/01-business-requirements.md`](./docs/product/01-business-requirements.md) —
   personas, requirements, and the voice-first MVP scope decision.
8. [`docs/product/02-user-flows.md`](./docs/product/02-user-flows.md) — onboarding, call, booking,
   escalation, billing, and support-access flows.
9. [`docs/product/03-technical-specifications.md`](./docs/product/03-technical-specifications.md) —
   API conventions the implementation must follow.
10. [`docs/api/openapi.yaml`](./docs/api/openapi.yaml) — the validated MVP API contract.

## Repository layout

```
apps/            Frontend applications (Next.js)
services/        Backend services (Python/FastAPI)
packages/        Shared code (types, UI components, config) used across apps/services
infra/           Terraform (IaC) and Docker/local-dev configuration
docs/            Architecture, API, and operational runbook documentation
```

See the README in each top-level directory for what belongs there.

## Tech stack

Frontend: Next.js (App Router), React, TypeScript, TailwindCSS, shadcn/ui, TanStack Query, React
Hook Form, Zod.

Backend: Python, FastAPI, SQLAlchemy, Celery, Redis, PostgreSQL + pgvector, S3-compatible object
storage.

AI: OpenAI, Anthropic, Google Gemini (routed per task — see AI architecture doc), LangGraph,
Deepgram (STT), ElevenLabs (TTS), Twilio, WhatsApp Business API.

Infra: AWS, Docker, Terraform, GitHub Actions, NGINX/ALB, Cloudflare.

Observability: Prometheus, Grafana, OpenTelemetry, Sentry.

Testing: Pytest, Playwright, Vitest.
