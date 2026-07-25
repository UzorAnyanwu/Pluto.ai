# .github/workflows

CI/CD per [`docs/architecture/05-infra-and-observability.md`](../../docs/architecture/05-infra-and-observability.md) §3.

- **`ci.yml`** — runs on every PR and push to main: lint (ruff) + type-check (mypy), tests (pytest
  against real Postgres+pgvector and Redis service containers, including a migration
  up/down/up cycle), dependency vulnerability scan (pip-audit), and — only when
  `infra/terraform/**` changed — `terraform plan` posted as a PR comment (never applied).
- **`deploy.yml`** — triggered via `workflow_run` after `CI` succeeds on main: builds and pushes
  a SHA-tagged image, scans it (Trivy), runs Alembic migrations, deploys to staging, smoke-tests
  it, then waits behind the `production` GitHub Environment's required-reviewers gate before
  deploying to production. Rollback relies on the ECS deployment circuit breaker configured in
  `infra/terraform/modules/ecs-service`, not workflow-scripted rollback logic.

**Not exercised yet**: both workflows need repo secrets (`AWS_CI_DEPLOY_ROLE_ARN`,
`AWS_TERRAFORM_PLAN_ROLE_ARN`, staging/production migration DB URLs) and the AWS infrastructure
those roles/URLs point at — none of which exist until `infra/terraform/global` and an applied
`environments/dev` exist. YAML syntax and job structure are validated (parsed and reviewed against
the GitHub Actions schema); the workflows themselves have not run in GitHub Actions.
