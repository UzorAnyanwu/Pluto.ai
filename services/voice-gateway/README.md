# services/voice-gateway

Stateful, low-latency telephony service: terminates Twilio Media Streams, runs streaming
speech-to-text (Deepgram) and streaming text-to-speech (ElevenLabs), and handles barge-in and
warm-transfer escalation. Deployed with call-affinity (not request-affinity) scaling — a dedicated
service, never merged into `api-core`, because its latency and concurrency profile (long-lived
WebSocket per active call, hard 2s p95 response budget) is categorically different from a REST API.
See [`docs/architecture/03-ai-and-voice-architecture.md`](../../docs/architecture/03-ai-and-voice-architecture.md) §5.

Not yet implemented — scaffolding lands in Phase 2 (Voice Engine).
