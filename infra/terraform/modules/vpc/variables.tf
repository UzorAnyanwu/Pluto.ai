variable "name" {
  description = "Name prefix for all resources created by this module (e.g. \"pluto-ai-dev\")."
  type        = string
}

variable "cidr_block" {
  description = "CIDR block for the VPC."
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "Availability zones to spread subnets across. At least 2 required for RDS Multi-AZ / ALB."
  type        = list(string)
}

variable "single_nat_gateway" {
  description = <<-EOT
    If true, provisions one NAT gateway shared by all private subnets (cheaper — appropriate for
    dev/staging). If false, provisions one NAT gateway per AZ (higher availability — a NAT
    gateway outage only affects one AZ's private subnet, not the whole VPC's outbound traffic —
    the correct choice for production per docs/architecture/05-infra-and-observability.md's
    per-environment isolation stance).
  EOT
  type        = bool
  default     = true
}

variable "tags" {
  description = "Tags applied to every resource this module creates."
  type        = map(string)
  default     = {}
}
