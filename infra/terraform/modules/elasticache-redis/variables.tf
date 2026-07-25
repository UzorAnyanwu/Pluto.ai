variable "name" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "private_subnet_ids" {
  type = list(string)
}

variable "allowed_security_group_ids" {
  type = list(string)
}

variable "node_type" {
  type    = string
  default = "cache.t4g.micro"
}

variable "engine_version" {
  type    = string
  default = "7.1"
}

variable "multi_az_enabled" {
  type        = bool
  default     = false
  description = "true in production: automatic failover to a replica if the primary node fails."
}

variable "tags" {
  type    = map(string)
  default = {}
}
