variable "name" {
  type        = string
  description = "e.g. \"pluto-api-core-dev\"."
}

variable "cluster_id" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "private_subnet_ids" {
  type = list(string)
}

variable "image" {
  type        = string
  description = "Initial image. CI (deploy.yml) updates the running task definition's image on every deploy — this value only matters for the very first `terraform apply`."
}

variable "container_port" {
  type    = number
  default = 8000
}

variable "cpu" {
  type    = number
  default = 512
}

variable "memory" {
  type    = number
  default = 1024
}

variable "desired_count" {
  type    = number
  default = 2
}

variable "min_capacity" {
  type    = number
  default = 2
}

variable "max_capacity" {
  type    = number
  default = 10
}

variable "cpu_target_utilization" {
  type        = number
  default     = 60
  description = "Target-tracking autoscaling policy: add tasks to keep average CPU near this percentage."
}

variable "environment_variables" {
  type    = map(string)
  default = {}
}

variable "secrets" {
  type        = map(string)
  default     = {}
  description = "Map of container env var name -> Secrets Manager ARN."
}

variable "attach_to_alb" {
  type        = bool
  default     = true
  description = "false for services with no inbound HTTP traffic (e.g. the Celery `workers` service) — see docs/architecture/01-system-architecture.md §3."
}

variable "alb_listener_arn" {
  type    = string
  default = null
}

variable "alb_security_group_id" {
  type    = string
  default = null
}

variable "health_check_path" {
  type    = string
  default = "/docs"
}

variable "path_pattern" {
  type        = list(string)
  default     = ["/*"]
  description = "ALB listener rule path pattern routed to this service."
}

variable "listener_rule_priority" {
  type = number
}

variable "task_role_policy_arns" {
  type        = list(string)
  default     = []
  description = "Additional IAM policy ARNs attached to the task role — e.g. S3 access for a service that reads/writes recordings. Kept as an input (not hardcoded here) because task-level permissions are inherently service-specific; this module only owns the execution role (ECR pull, log group, Secrets Manager read for the `secrets` map above)."
}

variable "enable_execute_command" {
  type        = bool
  default     = false
  description = "true enables `aws ecs execute-command` (a shell into a running task) — useful in dev for debugging, should stay false in production (it's a standing remote-access surface)."
}

variable "tags" {
  type    = map(string)
  default = {}
}
