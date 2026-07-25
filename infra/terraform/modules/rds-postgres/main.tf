####################################################################################################
# RDS for PostgreSQL. pgvector needs no special parameter-group entry (it doesn't require
# shared_preload_libraries — it's loaded per-database via `CREATE EXTENSION vector`, done by the
# first Alembic migration, not here).
#
# The master credential is AWS-managed (`manage_master_user_password = true`): RDS generates it
# and stores it in Secrets Manager itself, so a plaintext password never touches Terraform state,
# a .tfvars file, or CI logs. The master user is used ONLY by the migration bootstrap step
# (creating the `pluto_app` least-privilege role and running Alembic) — see
# libs/pluto_core/migrations/rls_helpers.py and scripts/bootstrap_local_db.sh for why the
# application itself must never connect as this user.
####################################################################################################

resource "aws_db_subnet_group" "this" {
  name       = "${var.name}-postgres"
  subnet_ids = var.private_subnet_ids
  tags       = merge(var.tags, { Name = "${var.name}-postgres" })
}

resource "aws_security_group" "this" {
  name_prefix = "${var.name}-postgres-"
  description = "Allows Postgres (5432) only from explicitly listed security groups."
  vpc_id      = var.vpc_id

  tags = merge(var.tags, { Name = "${var.name}-postgres" })

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_security_group_rule" "ingress" {
  for_each                 = toset(var.allowed_security_group_ids)
  type                     = "ingress"
  from_port                = 5432
  to_port                  = 5432
  protocol                 = "tcp"
  security_group_id        = aws_security_group.this.id
  source_security_group_id = each.value
}

resource "aws_security_group_rule" "egress_all" {
  type              = "egress"
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  security_group_id = aws_security_group.this.id
  cidr_blocks       = ["0.0.0.0/0"]
}

resource "aws_db_parameter_group" "this" {
  name_prefix = "${var.name}-postgres-"
  family      = "postgres16"
  description = "Custom tuning hook for ${var.name} — empty today, deliberately present so tuning changes are a Terraform diff, not a manual console edit."

  lifecycle {
    create_before_destroy = true
  }

  tags = var.tags
}

resource "aws_db_instance" "this" {
  identifier     = "${var.name}-postgres"
  engine         = "postgres"
  engine_version = var.engine_version
  instance_class = var.instance_class

  allocated_storage     = var.allocated_storage_gb
  max_allocated_storage = var.max_allocated_storage_gb
  storage_type          = "gp3"
  storage_encrypted     = true

  db_name  = var.database_name
  username = "pluto_migrator"

  manage_master_user_password = true

  db_subnet_group_name   = aws_db_subnet_group.this.name
  vpc_security_group_ids = [aws_security_group.this.id]
  parameter_group_name   = aws_db_parameter_group.this.name

  multi_az                = var.multi_az
  backup_retention_period = var.backup_retention_days
  # Continuous point-in-time recovery, backed by the same backup_retention_period window — see
  # the RPO target (<=5 min) in docs/architecture/05-infra-and-observability.md §5.
  copy_tags_to_snapshot = true

  deletion_protection       = var.deletion_protection
  skip_final_snapshot       = var.skip_final_snapshot
  final_snapshot_identifier = var.skip_final_snapshot ? null : "${var.name}-postgres-final"

  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]

  tags = merge(var.tags, { Name = "${var.name}-postgres" })
}
