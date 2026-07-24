# Pluto AI

AI Business Operating System for SMEs — starting as an AI receptionist platform (voice, WhatsApp,
SMS, web chat) with booking, CRM, and workflow automation, built as a multi-tenant SaaS with
white-label/agency support from day one.

**Status:** Phase 1 — Architecture. No application code has been written yet by design; see
[`PROJECT_STATUS.md`](./PROJECT_STATUS.md) for exactly where things stand and
[`docs/architecture/`](./docs/architecture/) for the full system design and the reasoning behind
every major decision.

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
