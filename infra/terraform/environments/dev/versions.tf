terraform {
  required_version = ">= 1.9.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.70"
    }
  }

  # Partial backend configuration — the bucket/key/region/dynamodb_table are supplied via
  # `terraform init -backend-config=backend.hcl` (kept out of version control since the bucket
  # name is account-specific) so this same block works unmodified across dev/staging/production,
  # per docs/architecture/05-infra-and-observability.md §2.
  backend "s3" {}
}
