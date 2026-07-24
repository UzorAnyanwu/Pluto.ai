# Pluto AI — Infrastructure, Deployment & Observability (v1)

Status: **Draft for review — Phase 1**
Last updated: 2026-07-24

## 1. Environments

`dev` (shared, ephemeral-friendly, seeded with synthetic data) → `staging` (production-topology
mirror, real integrations in sandbox/test mode — Twilio test credentials, Stripe test mode) →
`production`. Every environment is a fully separate AWS account (not just a separate VPC in one
account) — the strongest blast-radius boundary available, and it removes an entire class of
"staging IAM role accidentally had prod access" incidents. Cross-account access is via assumed
roles from a central CI/CD identity, never long-lived per-environment credentials sitting in GitHub
Actions secrets.

## 2. Infrastructure as Code

**Terraform**, organized as reusable modules, not one monolithic root:

```
infra/terraform/
├── modules/
│   ├── vpc/
│   ├── ecs-service/          # generic: any of our services (api-core, ai-engine, workers) instantiate this
│   ├── voice-gateway/        # specialized module: call-affinity target group config differs from generic ecs-service
│   ├── rds-postgres/
│   ├── elasticache-redis/
│   ├── s3-bucket/
│   ├── sns-sqs/
│   └── cloudfront-cf/
├── environments/
│   ├── dev/
│   ├── staging/
│   └── production/
└── global/                   # IAM, Route53, Cloudflare account-level config
```

Each `environments/<env>` composes modules with env-specific variables; state is stored remotely
(S3 backend + DynamoDB lock table) per environment, never local state files. Module reuse is what
makes standing up a fourth environment (e.g., a dedicated single-tenant deployment for an enterprise
customer, per the isolation-tier escape hatch in the system architecture doc) a variables file, not
a rewrite.

## 3. CI/CD pipeline (GitHub Actions)

```
On PR:
  lint (ruff/eslint) → type-check (mypy/tsc) → unit tests (pytest/vitest) →
  dependency + container scan → Terraform plan (posted as PR comment, not applied)

On merge to main:
  full test suite → build + push container images (tagged by commit SHA, immutable) →
  deploy to staging (automatic) → smoke tests against staging →
  deploy to production (manual approval gate) → post-deploy health check → auto-rollback on failure
```

**Why a manual gate to production and not full continuous deployment:** at this stage, the cost of
a bad production deploy (a live phone call getting dropped mid-conversation) is asymmetric with the
cost of a few minutes of human approval latency. Revisit full auto-deploy to prod once deploy
health-checks and automatic rollback have a proven track record — this is a maturity gate, not a
permanent policy.

Database migrations run as a distinct, gated pipeline step (Alembic), applied before the new
application version is allowed to receive traffic, using expand/contract migration patterns (add
new columns nullable → deploy code that writes both → backfill → deploy code that reads new column
→ drop old column in a later release) so a rollback of the application version never requires a
matching database rollback.

## 4. Observability stack

| Concern | Tool | Notes |
|---|---|---|
| Distributed tracing | OpenTelemetry SDK in every service → OTel Collector → backend | Every request/call gets a trace ID propagated from `voice-gateway`/`api-core` through `ai-engine` and background jobs — essential for debugging "why did this specific call take 3.2 seconds" |
| Metrics | Prometheus (scraped via OTel Collector) + Grafana dashboards | Per-service RED metrics (rate/errors/duration) plus product metrics (active calls, p95 voice latency, RAG retrieval latency) as first-class dashboards, not just infra metrics |
| Error tracking | Sentry | Every service reports exceptions with tenant/request context attached (scrubbed of PII per the security doc's data classification) |
| Logs | Structured JSON logs → CloudWatch Logs (launch) | Every log line carries `trace_id`, `business_id`, `request_id`. Revisit a dedicated log aggregation stack (e.g., self-hosted Loki/ELK) once CloudWatch's per-query cost or search ergonomics becomes a real constraint — not needed at launch volume |
| Alerting | Grafana alerting → PagerDuty/Slack | Alert on symptom (p95 voice latency > 2s sustained, error rate spike, queue depth growing unbounded), not on every individual infra metric — alert fatigue is a real failure mode for a small on-call rotation |

**The one dashboard that matters most for this product specifically:** voice pipeline stage-by-stage
latency (STT time, LLM time-to-first-token, TTS time-to-first-byte, total), broken out by percentile,
because the 2-second budget (`03-ai-and-voice-architecture.md` §5) is the product's core quality
promise — a regression here is a product incident even if every infra metric looks green.

## 5. Backup & disaster recovery

- **RDS:** automated daily snapshots + continuous point-in-time recovery (35-day window), cross-region
  snapshot replication for the production account.
- **S3** (recordings, KB source documents): versioning enabled, lifecycle policy transitions
  older call recordings to Glacier after a configurable retention window (business-configurable,
  respecting jurisdiction-specific retention rules from the compliance doc).
- **RTO/RPO targets (production):** RPO ≤ 5 minutes (continuous WAL-based PITR), RTO ≤ 1 hour for a
  full regional failure (documented runbook, not yet a fully automated failover — automated
  multi-region active/active is a Phase 5+ concern once traffic volume justifies the added
  complexity and cost).

## 6. Local development

`infra/docker/docker-compose.yml` (added when Phase 2 backend work starts) brings up Postgres
(with pgvector extension), Redis, and localstack (for S3/SNS/SQS emulation) so engineers don't need
live AWS credentials to develop day-to-day — only staging/prod deploys touch real AWS.

## 7. Known scaling bottlenecks to watch (tracked honestly, not hidden)

- **Postgres as the single primary datastore for both OLTP and vector search**: the first real
  scaling pressure point past a few thousand active tenants is likely write load on `messages` /
  `conversation_events` (every turn of every call writes rows). Mitigation path: read replicas for
  analytics/dashboard queries (never route transactional writes to a replica), then table
  partitioning by `business_id` or time range, before considering a second datastore — in that
  order, because each step is cheaper than the next.
- **`voice-gateway` concurrent-call ceiling per task**: needs a load test early (Phase 2) to
  establish real numbers rather than assumed capacity — this determines the call-affinity router's
  scaling curve and is a concrete unknown, flagged here rather than guessed at.
- **SNS/SQS fan-out cost and latency at very high event volume**: acceptable at launch; the
  Kafka/MSK migration trigger from Decision 3 (system architecture doc) is the mitigation, not a
  redesign.
