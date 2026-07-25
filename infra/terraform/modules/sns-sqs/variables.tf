variable "topic_name" {
  type        = string
  description = "e.g. \"pluto-ai-dev-domain-events\" — one topic per environment carries every domain event (call.completed, booking.created, etc.); consumers filter via subscription filter policies, not separate topics. See docs/architecture/01-system-architecture.md §5."
}

variable "subscriber_queues" {
  description = <<-EOT
    One entry per consumer (e.g. "crm-sync-worker", "webhook-dispatcher", "analytics-pipeline").
    `filter_policy`, if set, is a JSON string per AWS's SNS filter policy syntax so a consumer
    only receives the event types it cares about — e.g. '{"event_type": ["call.completed"]}'.
  EOT
  type = map(object({
    filter_policy = optional(string)
  }))
  default = {}
}

variable "max_receive_count" {
  type        = number
  default     = 5
  description = "Messages are moved to the per-queue dead-letter queue after this many failed processing attempts, rather than being retried forever or silently dropped."
}

variable "visibility_timeout_seconds" {
  type    = number
  default = 30
}

variable "message_retention_seconds" {
  type    = number
  default = 1209600 # 14 days — SQS's maximum, giving the widest possible window to notice and fix a broken consumer before its backlog is lost.
}

variable "tags" {
  type    = map(string)
  default = {}
}
