# modules/voice-gateway (not yet implemented)

Specialized deployment module for `services/voice-gateway` — see
`docs/architecture/01-system-architecture.md` §9 and `docs/architecture/03-ai-and-voice-architecture.md`
§5. Differs from the generic `ecs-service` module in ways that matter enough to need its own
module rather than a variant of it:

- **Call-affinity, not request-affinity** target group behavior (new calls route to the
  least-loaded task; all audio frames for an existing call stay pinned to the same task for its
  duration) — the generic module's round-robin ALB target group doesn't support this.
- **No Fargate Spot** in its capacity provider strategy, ever — an interrupted Spot task mid-call
  is a dropped customer call, unlike `workers`, which tolerates interruption fine.
- A concurrent-call capacity ceiling per task that is currently an **open unknown**, flagged in
  `docs/architecture/05-infra-and-observability.md` §7 — sizing this module (cpu/memory per task,
  target-tracking metric) needs a load test that hasn't been run yet, so writing the module now
  would mean guessing at numbers instead of measuring them.

Build this once `services/voice-gateway` has real code to deploy (Phase 2, Voice Engine module
per `PROJECT_STATUS.md`) and the load test has produced real capacity numbers — not before.
