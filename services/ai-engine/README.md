# services/ai-engine

LangGraph orchestration, the multi-provider model router (OpenAI/Anthropic/Gemini), and RAG
retrieval. Ships initially as a library consumed by `api-core` and `voice-gateway`; extracted into
its own networked service once inference-cost/GPU isolation needs justify it. See
[`docs/architecture/03-ai-and-voice-architecture.md`](../../docs/architecture/03-ai-and-voice-architecture.md).

Not yet implemented — scaffolding lands in Phase 2 (AI Engine).
