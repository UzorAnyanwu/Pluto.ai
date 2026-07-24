# infra/terraform

IaC for all AWS infrastructure (VPC, ECS, RDS, ElastiCache, S3, SNS/SQS, IAM), organized as
reusable modules composed per environment (`dev`, `staging`, `production`). See
[`docs/architecture/05-infra-and-observability.md`](../../docs/architecture/05-infra-and-observability.md) §2
for the planned module layout. Not yet implemented — lands alongside the first CI/CD pipeline work
in Phase 1's remaining Repository Setup/Infrastructure milestone.
