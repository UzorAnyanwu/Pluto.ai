# infra/terraform/global

Account-wide resources that don't belong to any single environment: the Route53 hosted zone,
ACM certificates (DNS validation is account-wide), and IAM resources shared across
dev/staging/production (e.g. the GitHub OIDC provider + the `AWS_CI_DEPLOY_ROLE_ARN` /
`AWS_TERRAFORM_PLAN_ROLE_ARN` roles referenced in `.github/workflows/`).

**Not implemented yet** — this requires a real registered domain and AWS account decisions
(which account hosts the zone, certificate rotation ownership) that are a product/business call,
not something to scaffold speculatively. Populate this directory as the first step of the
Infrastructure milestone in `PROJECT_STATUS.md`, before `environments/dev` can actually be
applied (its `acm_certificate_arn` variable has no default for exactly this reason).
