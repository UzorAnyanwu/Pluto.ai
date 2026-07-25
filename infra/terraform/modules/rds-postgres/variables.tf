variable "name" {
  type        = string
  description = "Identifier prefix, e.g. \"pluto-ai-dev\"."
}

variable "vpc_id" {
  type = string
}

variable "private_subnet_ids" {
  type        = list(string)
  description = "RDS is never placed in a public subnet — see docs/architecture/05-infra-and-observability.md."
}

variable "allowed_security_group_ids" {
  type        = list(string)
  description = "Security groups permitted to connect on 5432 (typically the ECS tasks' SG)."
}

variable "instance_class" {
  type    = string
  default = "db.t4g.medium"
}

variable "allocated_storage_gb" {
  type    = number
  default = 50
}

variable "max_allocated_storage_gb" {
  type        = number
  default     = 500
  description = "RDS storage autoscaling ceiling — grows automatically under write load instead of paging someone at 2am."
}

variable "engine_version" {
  type    = string
  default = "16.4"
}

variable "multi_az" {
  type        = bool
  default     = false
  description = "true in production (docs/architecture/05-infra-and-observability.md's RTO/RPO targets assume it); false in dev/staging to control cost."
}

variable "backup_retention_days" {
  type    = number
  default = 7
}

variable "deletion_protection" {
  type    = bool
  default = false
}

variable "skip_final_snapshot" {
  type        = bool
  default     = true
  description = "false in production — never skip the final snapshot on an environment that matters."
}

variable "database_name" {
  type    = string
  default = "pluto_ai"
}

variable "tags" {
  type    = map(string)
  default = {}
}
