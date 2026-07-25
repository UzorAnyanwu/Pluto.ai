variable "bucket_name" {
  type = string
}

variable "versioning_enabled" {
  type    = bool
  default = true
}

variable "lifecycle_transition_days" {
  type        = number
  default     = null
  description = "If set, objects transition to GLACIER after this many days — used for call recordings per the retention policy in docs/architecture/05-infra-and-observability.md §5. Null disables the rule."
}

variable "lifecycle_expiration_days" {
  type        = number
  default     = null
  description = "If set, objects are deleted after this many days. Null disables the rule."
}

variable "cors_allowed_origins" {
  type        = list(string)
  default     = []
  description = "Non-empty only for buckets the frontend uploads to directly (e.g. knowledge-base documents via presigned URLs)."
}

variable "tags" {
  type    = map(string)
  default = {}
}
