output "topic_arn" {
  value = aws_sns_topic.this.arn
}

output "queue_arns" {
  value = { for k, v in aws_sqs_queue.this : k => v.arn }
}

output "queue_urls" {
  value = { for k, v in aws_sqs_queue.this : k => v.id }
}

output "dlq_arns" {
  value = { for k, v in aws_sqs_queue.dlq : k => v.arn }
}
