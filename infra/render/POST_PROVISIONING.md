# Render staging deployment — one-time setup checklist

`render.yaml` (repo root) defines the Blueprint. These steps can't be encoded in that file — they
either require dashboard/OAuth actions or handling real secret material that must never be
committed. Do them in order the first time; only the domain step is optional.

## 1. Sync the Blueprint
Render dashboard → **New** → **Blueprint** → select the `UzorAnyanwu/Pluto.ai` repo → branch
`main`. Render detects `render.yaml` and shows a plan (1 web service, 1 Postgres, 1 Redis) before
creating anything — review it, then apply.

## 2. Fill in the JWT secret files
The Blueprint declares two secret files (`jwt_private_key.pem`, `jwt_public_key.pem`) as
placeholders — Render won't let the service start until they have content, and that content must
never go in the repo. On this machine, the production keypair already exists (generated
alongside this deployment work, separate from the local dev keypair):

```
secrets/production/jwt_private_key.pem
secrets/production/jwt_public_key.pem
```

Open each file, copy its full contents (including the `-----BEGIN/END-----` lines), and paste
into the matching secret file's content field: service → **Environment** → **Secret Files**.

## 3. Wire the deploy gate
`render.yaml` sets `autoDeploy: false` deliberately (see its comments) — deploys are triggered by
`.github/workflows/deploy-render.yml` only after the `CI` workflow passes, not on every push.

1. In Render: service → **Settings** → **Deploy Hook** → copy the URL.
2. In GitHub: repo → **Settings** → **Secrets and variables** → **Actions** → **New repository
   secret** → name it `RENDER_DEPLOY_HOOK_URL`, paste the URL.

Until this is set, deploys only happen when manually triggered from the Render dashboard.

## 4. Custom domain (optional — needs the domain name)
Service → **Settings** → **Custom Domains** → add the domain. Render shows a CNAME (or A record
for an apex domain) to add at your DNS registrar. TLS certificate provisioning is automatic once
that record verifies — no ACM-style manual cert request needed, unlike the AWS path.

## 5. Known gap: single DB role, not the two-role security model
`render.yaml` points `DATABASE_URL` and `MIGRATION_DATABASE_URL` at the same Render-managed
Postgres admin connection — Render provisions one admin user per database, not the least-privilege
`pluto_app` role our RLS design assumes (see `libs/pluto_core/migrations/rls_helpers.py`). This is
a deliberate, documented simplification for a validation deployment, not silently accepted debt.

To close it (only if this deployment needs to be more than a validation step):
1. Get the external connection string: service → the Postgres resource → **Connect** → **External
   Connection String**.
2. `psql "<that connection string>"` and run the same role-creation SQL as
   `scripts/bootstrap_local_db.sh` (adjust the password), i.e. create `pluto_app`
   `NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS`, then `GRANT CONNECT`/`GRANT USAGE ON SCHEMA
   public` — the Alembic migration's `row_level_security_and_grants` revision handles the rest
   (table-level grants, RLS policies) automatically once that role exists, exactly as it does
   locally.
3. Manually override `DATABASE_URL` in the Render dashboard (service → Environment) to a
   connection string built from that new role's credentials — `fromDatabase` in render.yaml can't
   express "the same database, but as a different role," so this one env var stops being
   Blueprint-managed after this point (Render will warn about the drift on future Blueprint syncs
   — that's expected and fine).

## 6. Verify it's actually live
```
curl -sf https://<service>.onrender.com/docs -o /dev/null && echo "up"

# Full round-trip, same check as the AWS smoke test in deploy.yml:
curl -sf -X POST https://<service>.onrender.com/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"smoke-test@example.com","password":"smoke-test-password-123","business_name":"Smoke Test","timezone":"UTC"}'
```
A JSON body with an `access_token` confirms: the container built and started, migrations ran
against the real Render Postgres, RLS is enforced (the same code path
`test_rls_isolation.py` exercises locally), and Redis-backed rate limiting is reachable.
