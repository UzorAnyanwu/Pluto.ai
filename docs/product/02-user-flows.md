# Pluto AI — User Flows (v1)

Status: **Draft for review — Phase 1**
Last updated: 2026-07-24

Flows are written at the level of detail needed to derive API endpoints and screens from them in
the next doc (`03-technical-specifications.md`) — concrete steps and decision points, not vague
narrative.

## 1. Onboarding — signup to first live call (MVP, voice-first per business requirements §4)

This is the single most important flow in the product: it's the activation path, and every extra
step here is a drop-off risk.

```mermaid
flowchart TD
    A[Sign up: email + password or Google OAuth] --> B[Create business workspace:<br/>name, industry, timezone]
    B --> C{Get a phone number}
    C -->|Provision new number| D[Pick area code → Twilio number purchased & attached]
    C -->|Use existing number| E[Call forwarding instructions shown<br/>+ verification call to confirm forwarding works]
    D --> F[Configure AI agent basics:<br/>business hours, services, one-line description]
    E --> F
    F --> G[Add knowledge:<br/>upload docs OR paste website URL OR skip for now]
    G --> H{Knowledge indexing}
    H -->|ready| I[Connect calendar: Google/Outlook, or skip for now]
    H -->|failed| G
    I --> J[Test call: place a call to your own number,<br/>talk to your AI, see the transcript live]
    J --> K{Satisfied?}
    K -->|No, tweak config| F
    K -->|Yes| L[Go live: AI now answers real inbound calls]
    L --> M[Dashboard home: call log, empty state guidance]
```

**Key product decisions this flow implies:**
- Knowledge base and calendar connection are both **skippable** — the AI must be able to go live in
  a degraded-but-useful mode (answer questions from the system prompt/business basics alone, take a
  message instead of booking) rather than blocking activation on every integration being complete.
  This directly serves the time-to-live metric from the requirements doc.
- The test call step is not optional — letting an owner hear their AI before it takes a real call is
  the trust-building moment of the whole flow, and it surfaces obviously-wrong config (bad voice,
  wrong hours) before a real customer does.

## 2. Inbound call — customer-facing and business-facing views of the same event

Technical sequence is in `docs/architecture/03-ai-and-voice-architecture.md` §5. This is the product
view: what the business owner sees afterward.

```mermaid
sequenceDiagram
    participant Cust as Customer
    participant AI as AI Receptionist
    participant Sys as Pluto AI (async, post-call)
    participant Owner as Business Owner (dashboard)

    Cust->>AI: Calls the business number
    AI->>Cust: Answers, converses, (books / answers / escalates)
    Note over AI: Call ends
    AI->>Sys: conversation_events (full transcript, tool calls)
    Sys->>Sys: Generate summary, sentiment, extract lead fields (async, seconds after call ends)
    Sys->>Sys: Update CRM: create/update customer, lead, booking if applicable
    Sys->>Sys: Fire workflow triggers (e.g. "send booking confirmation SMS")
    Owner->>Sys: Opens dashboard, sees new conversation card:<br/>summary, sentiment badge, transcript, recording, CRM link
```

The dashboard conversation view is the single highest-traffic screen for an active business owner —
it's the "did the AI do its job" trust check they'll come back to repeatedly, especially in the
first weeks after going live.

## 3. Booking flow (via voice, MVP)

```mermaid
flowchart TD
    A[Customer asks to book / AI determines intent = booking] --> B[AI asks for service + preferred time]
    B --> C[AI queries availability:<br/>internal bookings + live external calendar]
    C --> D{Slot available?}
    D -->|Yes| E[AI confirms slot verbally, customer confirms]
    D -->|No| F[AI offers nearest alternative slots]
    F --> B
    E --> G[Booking written to DB + pushed to external calendar]
    G --> H{External calendar push succeeds?}
    H -->|Yes| I[AI confirms booking to customer, ends call]
    H -->|No — conflict detected at write time,<br/>e.g. race with a manual booking| J[AI apologizes, offers new slot immediately<br/>rather than confirming a booking that isn't real]
    I --> K[Async: confirmation SMS/email sent<br/>per configured workflow]
```

The race-condition branch (H → J) matters at scale: two customers (or a customer and a staff member
booking manually in Google Calendar directly) can contend for the same slot. The write path treats
the external calendar as the final source of truth at commit time, not just at read time — the AI
never confirms a booking to a customer before that write has actually succeeded.

## 4. Escalation / human handoff (MVP)

```mermaid
flowchart TD
    A[Escalation trigger fires:<br/>explicit request / negative sentiment / repeated failure / configured always-escalate intent] --> B{Staff configured as available<br/>for live transfer right now?}
    B -->|Yes| C[Warm transfer: AI briefs the human with a spoken summary,<br/>then connects the call]
    B -->|No / no answer| D[AI takes a structured message:<br/>reason, callback number, urgency]
    D --> E[Message + full transcript pushed to dashboard<br/>as a flagged, unread item]
    E --> F[Notification to staff: SMS/email/dashboard per their preferences]
    C --> G[Conversation marked escalated in CRM,<br/>full context available to the human]
```

## 5. Agency provisioning (Later — Phase 4, flow captured now for data-model completeness)

```mermaid
flowchart TD
    A[Agency signs up / is onboarded by Pluto AI sales] --> B[Configure white-label branding:<br/>logo, colors, custom domain]
    B --> C[Provision a new business under the agency]
    C --> D[Business inherits an agency-defined AI config template<br/>owner can still customize]
    D --> E[Business appears in agency's portfolio dashboard]
    E --> F[Agency billing: business's subscription rolls up<br/>to agency invoice per commercial terms]
```

## 6. Billing lifecycle (MVP: trial → paid; usage overage Later)

```mermaid
flowchart LR
    A[Signup starts a 14-day trial<br/>no card required] --> B{Trial ends}
    B -->|Card added, plan selected| C[Active subscription via Stripe]
    B -->|No card added| D[Business suspended:<br/>AI stops answering, dashboard read-only,<br/>data retained per retention policy]
    C --> E{Usage within plan limits?}
    E -->|Yes| C
    E -->|Exceeded — Later: usage-based overage| F[Overage billed via Stripe usage records<br/>at period end]
    D -->|Card added later| C
```

## 7. Platform support access (MVP — the audited-access flow from the security doc, as a UX flow)

```mermaid
flowchart TD
    A[Support agent needs to debug a customer's reported issue] --> B[Opens the ticket in the internal admin panel,<br/>links the business]
    B --> C[Requests time-boxed access to that business's data<br/>— reason required, free text]
    C --> D[Access granted for a limited window, e.g. 2 hours]
    D --> E[Every read of tenant data during that window<br/>writes to audit_logs with the ticket reference]
    E --> F[Access auto-expires; re-request needed for further work]
```

This flow exists specifically so "platform staff can see customer data" is never an ambient
capability — it's a deliberate, logged, time-boxed action, matching the RBAC design in
`04-security-and-compliance.md` §2.

---

Next: [`03-technical-specifications.md`](./03-technical-specifications.md), which derives the
`api-core` API contract from these flows.
