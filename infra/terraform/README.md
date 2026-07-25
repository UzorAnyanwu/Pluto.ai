# infra/terraform

IaC for all AWS infrastructure, organized as reusable modules composed per environment. See
[`docs/architecture/05-infra-and-observability.md`](../../docs/architecture/05-infra-and-observability.md) §2.

```
modules/
  vpc/                 Public/private subnets across N AZs, NAT gateway(s), route tables
  ecs-cluster/          Fargate + Fargate Spot capacity providers, Container Insights
  ecs-service/           Generic per-service module: task def, service, autoscaling, target group
  alb/                    Shared HTTPS ALB (Cloudflare sits in front of this — see architecture doc §7)
  rds-postgres/            AWS-managed master credential, encrypted, storage autoscaling
  elasticache-redis/        Celery broker + rate-limit counters, TLS + at-rest encryption
  s3-bucket/                Generic private bucket (call recordings, KB documents each get their own)
  sns-sqs/                   Domain event topic + per-consumer queue+DLQ (docs/architecture §5)
  ecr-repository/              Immutable-tag image repo, scan-on-push
  voice-gateway/, cloudfront-cf/   Not yet implemented — see their READMEs for why (no code/frontend to deploy yet)
environments/
  dev/                  Composes all of the above. Validated with `terraform validate` (real
                         AWS credentials weren't available in this environment, so `plan`/`apply`
                         have not been run — see below).
global/                 Account-wide resources (Route53 zone, ACM, GitHub OIDC role) — not yet
                         implemented, needs a real domain/account decision first (see its README)
```

## Validating changes

```bash
cd infra/terraform/environments/dev
terraform init -backend=false   # skip backend/AWS creds — validates config only
terraform validate
terraform fmt -recursive -check
```

`terraform plan`/`apply` need real AWS credentials and the S3 backend configured (copy
`backend.hcl.example` → `backend.hcl`, fill in your bucket, `terraform init -backend-config=backend.hcl`)
— not exercised yet since this repo has no AWS account wired up. `dev/variables.tf`'s
`acm_certificate_arn` has no default specifically to force that decision to happen in
`infra/terraform/global` first, not be guessed at here.
