####################################################################################################
# One SNS topic (domain events) fanning out to one SQS queue per consumer, each with its own
# dead-letter queue. This is the event backbone from docs/architecture/01-system-architecture.md
# §5: publishers (api-core) don't know or care who's listening; new consumers subscribe without
# touching the code that publishes the event.
####################################################################################################

resource "aws_sns_topic" "this" {
  name = var.topic_name
  tags = merge(var.tags, { Name = var.topic_name })
}

resource "aws_sqs_queue" "dlq" {
  for_each = var.subscriber_queues

  name                      = "${var.topic_name}-${each.key}-dlq"
  message_retention_seconds = var.message_retention_seconds

  tags = merge(var.tags, { Name = "${var.topic_name}-${each.key}-dlq" })
}

resource "aws_sqs_queue" "this" {
  for_each = var.subscriber_queues

  name                       = "${var.topic_name}-${each.key}"
  visibility_timeout_seconds = var.visibility_timeout_seconds
  message_retention_seconds  = var.message_retention_seconds

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dlq[each.key].arn
    maxReceiveCount     = var.max_receive_count
  })

  tags = merge(var.tags, { Name = "${var.topic_name}-${each.key}" })
}

# Lets SNS deliver to the queue — without this, SNS publishes succeed but nothing ever arrives,
# a classic silent-failure misconfiguration this policy exists specifically to prevent.
resource "aws_sqs_queue_policy" "allow_sns" {
  for_each  = var.subscriber_queues
  queue_url = aws_sqs_queue.this[each.key].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow"
        Principal = { Service = "sns.amazonaws.com" }
        Action    = "sqs:SendMessage"
        Resource  = aws_sqs_queue.this[each.key].arn
        Condition = {
          ArnEquals = { "aws:SourceArn" = aws_sns_topic.this.arn }
        }
      }
    ]
  })
}

resource "aws_sns_topic_subscription" "this" {
  for_each  = var.subscriber_queues
  topic_arn = aws_sns_topic.this.arn
  protocol  = "sqs"
  endpoint  = aws_sqs_queue.this[each.key].arn

  filter_policy = each.value.filter_policy
}
