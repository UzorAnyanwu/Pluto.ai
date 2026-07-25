variable "name" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "public_subnet_ids" {
  type = list(string)
}

variable "acm_certificate_arn" {
  type        = string
  description = "ACM certificate for the HTTPS listener. Provisioned separately (infra/terraform/global — DNS validation is account-wide, not per-environment)."
}

variable "tags" {
  type    = map(string)
  default = {}
}
