# Pluto AI — Business Requirements (v1)

Status: **Draft for review — Phase 1**
Last updated: 2026-07-24

This translates the architecture into what the product must actually do, for whom, and what "done"
means for the MVP. Requirements are tagged `MVP` (Phase 2 target) or `Later` (Phase 3+) so scope
creep into Phase 2 is a visible, deliberate decision, not a drift.

## 1. Personas

| Persona | Who they are | Primary goal |
|---|---|---|
| **Business Owner/Admin** | SME owner or manager (salon, clinic, law firm, contractor, etc.) | Never miss a call, never miss a lead, without hiring a receptionist |
| **Staff** | Front-desk / employee at the business | See what the AI handled, jump in when needed, manage their own bookings |
| **Customer** | The end caller/texter — the business's customer | Get a fast, correct answer or booking without knowing (or caring) they're talking to AI |
| **Agency Admin** | Reseller/white-label partner (e.g., a marketing agency selling Pluto AI under their own brand to their SME clients) | Provision and manage many businesses under their own brand, earn margin |
| **Agency Staff** | Support/onboarding staff at an agency | Onboard and support the agency's businesses without needing Pluto AI platform access |
| **Platform Admin** | Us — Pluto AI internal team | Operate the platform, support customers, control abuse, without unrestricted silent access to tenant data |
| **Platform Support** | Us — support/success team | Debug a specific customer issue with time-boxed, audited access |

## 2. Functional requirements by persona

### Business Owner/Admin — `MVP` unless noted
- Sign up, create a business workspace, invite team members with roles (owner/admin/staff/read-only).
- Connect a phone number (provision a new Twilio number, or port/forward an existing one).
- Configure the AI agent: system prompt, voice, language, operating hours, escalation rules,
  services/pricing/employees, locations.
- Upload knowledge base content: PDF/DOCX/CSV upload, website URL crawl, manual FAQ entry — and see
  indexing status (pending/ready/failed with reason).
- Connect a calendar (Google Calendar `MVP`, Outlook `MVP`, Calendly `Later`) and see bookings the
  AI makes sync bidirectionally (conflict detection against the real calendar, not just our DB).
- View conversation history: transcript, recording, AI-generated summary, sentiment, and any
  extracted lead/CRM fields, per conversation, searchable and filterable.
- View a CRM: customers, tagged/stateful leads, opportunity status — auto-populated from
  conversations, manually editable.
- Configure basic workflow automation (`MVP`: a fixed set of trigger→action templates, e.g. "on
  booking created, send SMS confirmation"; `Later`: a full visual workflow builder with arbitrary
  DAGs).
- See an analytics dashboard: call volume, answer rate, average handle time, booking conversion,
  sentiment trend.
- Manage billing: view/change plan, see usage against plan limits, view invoices.
- `Later`: WhatsApp, SMS, and web-chat channels (MVP is voice-first — see §4 scope decision below).
- `Later`: outbound AI calling (reminders, follow-ups, re-engagement campaigns).

### Staff — `MVP`
- View (not necessarily edit, depending on role) conversations and bookings relevant to them.
- Manually take over an escalated call/conversation.
- Manage their own booking calendar/availability if they're a bookable employee.

### Customer (end caller) — `MVP`
- Call the business's number and reach the AI receptionist with no perceptible IVR-maze delay.
- Be understood in natural language, get correct answers grounded in the business's actual
  knowledge base (not hallucinated pricing/policy).
- Book, reschedule, or cancel an appointment entirely through the call.
- Be transferred to a human when the AI can't help or the customer asks — with context carried over,
  not a cold transfer.
- `Later`: reach the same AI consistently across voice, WhatsApp, and web chat with shared memory
  of prior interactions.

### Agency Admin — `Later` (Phase 4 per architecture doc; requirements captured now so the data
model already accommodates it — see `02-data-model.md` §1)
- White-label branding (logo, colors, custom domain) applied across the dashboard their businesses
  use.
- Provision new businesses under their agency, with default AI config templates.
- View aggregated (not raw-content) analytics across their portfolio.
- Manage billing for their portfolio (revenue share or markup model — commercial terms TBD with
  finance, not an engineering decision).

### Platform Admin / Support — `MVP` (a minimal admin panel is required at MVP for us to operate the
platform at all — full admin feature set per Phase 4)
- View platform health: active businesses, call volume, error rates, per-tenant usage against plan.
- Time-boxed, audited access into a specific tenant's data for support purposes (never ambient).
- Suspend/reinstate a business (abuse, non-payment).
- `Later`: feature flag management UI, full billing override tools, impersonation-for-support mode
  (with strict audit + customer notification requirements — a security-sensitive feature that needs
  its own design pass before building, not assumed here).

## 3. Non-functional requirements

| Requirement | Target | Source |
|---|---|---|
| Voice response latency | p95 < 2s (customer speech end → AI audio start) | Mission statement; see AI/voice architecture doc §5 |
| Platform availability | 99.9% for `api-core`/dashboard; 99.95% for the voice path specifically (a dropped call is worse than a slow dashboard load) | Product requirement — receptionist that doesn't answer defeats the purpose |
| Tenant data isolation | No cross-tenant data access under any application-layer bug — enforced at the DB (RLS), not just app code | Security architecture doc §3 |
| Scale | Architecture must not require a redesign to support 100,000 active businesses | Project mandate |
| Multi-language | Voice/chat must support the top languages of target markets at launch (`MVP`: English + Spanish; additional languages `Later`, gated by Deepgram/ElevenLabs/LLM language support quality, not just a config flag) | Market requirement — many SME customer bases are multilingual |
| Data residency | Architecture must not block a future EU-region deployment | GDPR-aware mandate, security doc §6 |
| Accessibility (dashboard) | WCAG 2.1 AA for the web dashboard | Standard SaaS baseline |

## 4. MVP scope decision — voice-first, not all-channels-at-once

**The mission statement lists voice, WhatsApp, SMS, email, and web chat as core features.
Building all five simultaneously for MVP is explicitly rejected here — reasoning below, since this
is exactly the kind of scope tradeoff this project's standards require to be explained, not silently
decided.**

**Options**

| | All channels simultaneously for MVP | Voice-first MVP, other channels sequenced in Phase 3 |
|---|---|---|
| Time to a sellable product | Slow — five channel integrations, five sets of edge cases, before any business can go live | Fast — one channel done well |
| Product quality risk | High — effort split five ways means voice (the hardest, most differentiating, most technically demanding piece — 2s latency budget, barge-in, telephony) gets under-resourced | Low — voice gets full focus, which is also where the architecture (§5 of the voice doc) has already invested the most design effort |
| Market differentiation | Diluted | Voice is the hardest thing for competitors to do well — it's the moat |
| Reuse across channels | The `ai-engine` orchestration, RAG, and CRM layers are channel-agnostic by design (per `03-ai-and-voice-architecture.md` — `AgentContext` and the LangGraph orchestration don't know or care what channel they're serving), so adding WhatsApp/SMS/chat later is materially cheaper than building voice later would be | Same — the architecture was deliberately built so this reuse holds regardless of sequencing |

**Recommendation: MVP (Phase 2) ships voice only.** WhatsApp and web chat follow in Phase 3 (they
reuse the channel-agnostic AI/CRM core and mainly add a new "transport" adapter, not new AI logic).
SMS and email follow after that, since they're needed more for workflow/notification purposes
(booking confirmations, reminders) than as full conversational AI channels initially. This is
reflected in `PROJECT_STATUS.md`'s scope notes going forward.

## 5. Success metrics (product KPIs, not engineering SLOs)

- **Call answer rate**: % of inbound calls the AI successfully handles without an unrecoverable
  failure (dropped call, unresponsive, or repeated "I don't understand").
- **Booking conversion**: % of qualifying calls that result in a completed booking.
- **Escalation rate**: % of calls escalated to a human — tracked, not because escalation is bad
  (it's a required safety valve, per the architecture's escalation design), but because a rate
  that's too high indicates the AI isn't handling what it should, and a rate near zero on a business
  with genuinely complex requests may indicate escalation isn't triggering when it should.
- **Time-to-live**: from signup to "AI is answering real calls" — this is the core activation metric
  for a self-serve SME product; every onboarding flow decision in the next doc is evaluated against
  minimizing this.
- **Net Promoter Score / churn** — standard SaaS health metrics, tracked from launch.

---

Next: [`02-user-flows.md`](./02-user-flows.md)
