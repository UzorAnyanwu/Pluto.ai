# services/workers

Celery worker pool for background jobs: embedding generation, transcription post-processing, CRM
sync, outbound notification delivery (SMS/email/WhatsApp), and SNS/SQS domain-event consumers.
Runs as a separate process pool from `api-core` from day one so batch workload never competes with
request-serving capacity. See
[`docs/architecture/01-system-architecture.md`](../../docs/architecture/01-system-architecture.md) §3.

Not yet implemented — scaffolding lands in Phase 2 (Core Backend).
