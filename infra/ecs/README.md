# infra/ecs

ECS task definition templates used by `.github/workflows/deploy.yml` via
`aws-actions/amazon-ecs-render-task-definition` (which replaces the `image` field with the
freshly-built, SHA-tagged image before deploying). `ACCOUNT_ID` and resource ARNs are placeholders
— filled in for real once the corresponding Terraform (`infra/terraform/`) is applied and IAM
roles/secrets actually exist.

## Known gap: JWT private key provisioning in containers

`JWT_PRIVATE_KEY_PATH` / `JWT_PUBLIC_KEY_PATH` currently point at `/run/secrets/*.pem`, but
nothing in these task definitions actually populates that path yet — ECS Fargate's native
`secrets` field injects Secrets Manager values as **environment variables**, not files, so
`DATABASE_URL`/`REDIS_URL` work as-is but the JWT keypair does not. Two ways to close this,
neither implemented yet (tracked in `PROJECT_STATUS.md`):

1. Store the PEM contents as env vars (`JWT_PRIVATE_KEY_PEM`/`JWT_PUBLIC_KEY_PEM`) and extend
   `pluto_core.security.jwt`/`app.config` to accept key material directly, not just a file path —
   smallest change, no extra infrastructure.
2. Add a startup init container that fetches the keypair from Secrets Manager and writes it to a
   shared `ephemeralStorage`/volume mount before the app container starts — more infrastructure,
   but keeps key material out of process environment listings.

Option 1 is the recommended default (simpler, and env-var secret injection already has the same
trust boundary as the file-based approach) — deferred here because it's an application code
change, not purely an infra one, and this batch of work was scoped to auth/DB/CI/Terraform
scaffolding, not a second pass on the auth module.
