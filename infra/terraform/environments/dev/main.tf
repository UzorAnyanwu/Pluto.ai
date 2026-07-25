####################################################################################################
# Dev environment composition. Mirrors staging/production (once those exist) by construction —
# every environment instantiates the same modules with different sizing/variables, never a
# different shape, per docs/architecture/05-infra-and-observability.md §2.
####################################################################################################

locals {
  name = "pluto-ai-dev"
  tags = { Environment = "dev" }
}

module "vpc" {
  source = "../../modules/vpc"

  name               = local.name
  availability_zones = var.availability_zones
  single_nat_gateway = true # dev: cost over cross-AZ NAT redundancy
  tags               = local.tags
}

module "ecs_cluster" {
  source = "../../modules/ecs-cluster"

  name = local.name
  tags = local.tags
}

module "alb" {
  source = "../../modules/alb"

  name                = "${local.name}-alb"
  vpc_id              = module.vpc.vpc_id
  public_subnet_ids   = module.vpc.public_subnet_ids
  acm_certificate_arn = var.acm_certificate_arn
  tags                = local.tags
}

module "api_core_service" {
  source = "../../modules/ecs-service"

  name               = "${local.name}-api-core"
  cluster_id         = module.ecs_cluster.cluster_id
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  image              = var.api_core_image

  cpu           = 512
  memory        = 1024
  desired_count = 1 # dev: single task is enough; staging/production set this higher
  min_capacity  = 1
  max_capacity  = 4

  attach_to_alb          = true
  alb_listener_arn       = module.alb.https_listener_arn
  alb_security_group_id  = module.alb.security_group_id
  listener_rule_priority = 100
  path_pattern           = ["/*"]
  health_check_path      = "/docs"

  environment_variables = {
    ENVIRONMENT = "dev"
    JWT_ISSUER  = "pluto-ai"
  }

  secrets = {
    DATABASE_URL = module.rds.master_user_secret_arn # dev only — staging/production use the
    # pluto_app credential, stored as its own Secrets Manager secret by the migration bootstrap
    # job, never the RDS-managed master credential. See infra/ecs/README.md's "known gap" note
    # for the JWT keypair, which has the same "dev takes a shortcut" characteristic.
  }

  tags = local.tags
}

module "rds" {
  source = "../../modules/rds-postgres"

  name                       = local.name
  vpc_id                     = module.vpc.vpc_id
  private_subnet_ids         = module.vpc.private_subnet_ids
  allowed_security_group_ids = [module.api_core_service.security_group_id]

  instance_class      = "db.t4g.medium"
  multi_az            = false
  deletion_protection = false
  skip_final_snapshot = true

  tags = local.tags
}

module "redis" {
  source = "../../modules/elasticache-redis"

  name                       = local.name
  vpc_id                     = module.vpc.vpc_id
  private_subnet_ids         = module.vpc.private_subnet_ids
  allowed_security_group_ids = [module.api_core_service.security_group_id]
  multi_az_enabled           = false

  tags = local.tags
}

module "ecr_api_core" {
  source = "../../modules/ecr-repository"

  name = "pluto-api-core"
  tags = local.tags
}

module "call_recordings_bucket" {
  source = "../../modules/s3-bucket"

  bucket_name               = "${local.name}-call-recordings"
  lifecycle_transition_days = 90 # Glacier after 90 days — see retention policy, docs/architecture/05-infra-and-observability.md §5
  tags                      = local.tags
}

module "knowledge_base_bucket" {
  source = "../../modules/s3-bucket"

  bucket_name          = "${local.name}-knowledge-base"
  cors_allowed_origins = ["https://dev.pluto-ai.com"] # dashboard uploads via presigned URLs
  tags                 = local.tags
}

module "domain_events" {
  source = "../../modules/sns-sqs"

  topic_name = "${local.name}-domain-events"

  # No consumers yet — services/workers (the Celery worker pool that will consume these) hasn't
  # been built (see PROJECT_STATUS.md: Phase 2, not yet started). The topic exists now so
  # api-core can start publishing events without waiting on that build-out; consumers are added
  # here as subscriber_queues entries when they exist, with zero change to the publishing side.
  subscriber_queues = {}

  tags = local.tags
}
