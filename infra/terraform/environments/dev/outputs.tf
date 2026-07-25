output "alb_dns_name" {
  value = module.alb.dns_name
}

output "rds_endpoint" {
  value = module.rds.endpoint
}

output "redis_endpoint" {
  value = module.redis.primary_endpoint_address
}

output "ecr_repository_url" {
  value = module.ecr_api_core.repository_url
}

output "domain_events_topic_arn" {
  value = module.domain_events.topic_arn
}
