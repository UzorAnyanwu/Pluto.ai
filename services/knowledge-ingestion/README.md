# services/knowledge-ingestion

Document (PDF/DOCX/CSV) and website-crawl ingestion pipeline for the knowledge base: extraction,
chunking, embedding, and indexing into `knowledge_chunks`. Runs as Celery tasks (via
`services/workers`) rather than inline on the upload request. See
[`docs/architecture/03-ai-and-voice-architecture.md`](../../docs/architecture/03-ai-and-voice-architecture.md) §4.

Not yet implemented — scaffolding lands in Phase 2 (Knowledge Base).
