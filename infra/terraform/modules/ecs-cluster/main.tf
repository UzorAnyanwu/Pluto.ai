resource "aws_ecs_cluster" "this" {
  name = var.name

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = merge(var.tags, { Name = var.name })
}

# Fargate + Fargate Spot as available capacity providers. Spot is not used by default (services
# opt in per-task via a capacity_provider_strategy at the service level) — appropriate for
# `workers` (interruption-tolerant background jobs) but never for `voice-gateway` (an interrupted
# Spot task mid-call is a dropped customer call).
resource "aws_ecs_cluster_capacity_providers" "this" {
  cluster_name       = aws_ecs_cluster.this.name
  capacity_providers = ["FARGATE", "FARGATE_SPOT"]

  default_capacity_provider_strategy {
    capacity_provider = "FARGATE"
    weight            = 100
  }
}
