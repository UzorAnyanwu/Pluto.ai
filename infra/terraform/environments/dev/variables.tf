variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "availability_zones" {
  type    = list(string)
  default = ["us-east-1a", "us-east-1b"]
}

variable "acm_certificate_arn" {
  type        = string
  description = "ACM certificate ARN for api.dev.pluto-ai.com, provisioned in infra/terraform/global (account-wide DNS validation, not per-environment)."
}

variable "api_core_image" {
  type        = string
  description = "Initial api-core image URI (e.g. the ECR repo with an early tag). CI takes over subsequent deploys — see infra/ecs/README.md."
}
