# apps/web

## What's actually here right now

An AI-Studio-generated marketing landing page with an interactive AI sandbox demo (Vite + React
19 + Express + Tailwind, calling Gemini). It was built and pushed to this repo's GitHub remote
independently of the architecture/backend work documented in `docs/` and `PROJECT_STATUS.md`,
then merged into this path (`git subtree add --prefix=apps/web`) so both histories are preserved.
The Gemini API key is used server-side only (`server.ts`'s `/api/triage` and `/api/chat` routes),
not exposed to the browser — that part follows the right pattern.

**This is not the planned Next.js dashboard.** `docs/architecture/01-system-architecture.md` §6/§8
decided on a single Next.js (App Router) app with role-based route groups
(`(tenant)`/`(agency)`/`(platform-admin)`) for the actual product — the tenant dashboard, team
management, AI agent config, everything `services/api-core` exposes. This landing page is a
different thing: a **marketing/demo site**, built with a different framework (Vite, not Next.js),
with its own small demo backend that calls Gemini directly for an interactive sales sandbox — it
does not talk to `services/api-core` at all.

## Open decision (not made yet — flagging, not deciding unilaterally)

Two reasonable paths once real Core Frontend work starts:
1. **Keep this as a separate marketing site.** It doesn't need to be Next.js — it's not part of
   the tenant/agency/admin dashboard route groups, so there's no architectural reason to force it
   into that app. Build the actual product dashboard as its own Next.js app alongside it.
2. **Fold it into the Next.js app** as a public marketing route group, rewriting these components
   in Next.js for a single deploy target.

Whoever picks this up should decide based on how this project wants to handle marketing-site
deploys (its own Vercel/Render static/Node deploy vs. bundled with the product app) — not
something to guess at while just merging code.

## Run locally

**Prerequisites:** Node.js

1. `npm install`
2. Set `GEMINI_API_KEY` in `.env.local` (see `.env.example`)
3. `npm run dev` — runs the Express+Vite dev server on `http://localhost:3000`

`npm run build` / `npm start` for a production build (bundles `server.ts`, serves the built SPA).
