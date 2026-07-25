####################################################################################################
# Shared Application Load Balancer — one per environment, sitting behind Cloudflare (per
# docs/architecture/01-system-architecture.md §7: Cloudflare terminates and rate-limits at the
# edge, then proxies to this ALB). Each ecs-service module instance attaches its own target group
# and listener rule to the HTTPS listener created here, rather than provisioning its own ALB —
# one ALB per environment is both cheaper and simpler to point Cloudflare/DNS at than one per
# service.
#
# Ingress is open to 0.0.0.0/0 rather than allowlisted to Cloudflare's published IP ranges: with
# Cloudflare in front, that allowlist is the correct hardening step, but it's an operational
# detail (Cloudflare's IP list changes periodically and needs a refresh mechanism) deliberately
# deferred past this initial scaffolding — tracked in PROJECT_STATUS.md technical debt.
####################################################################################################

resource "aws_security_group" "this" {
  name_prefix = "${var.name}-alb-"
  description = "Public ALB — HTTP redirects to HTTPS, HTTPS terminates here."
  vpc_id      = var.vpc_id

  tags = merge(var.tags, { Name = "${var.name}-alb" })

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_security_group_rule" "http_ingress" {
  type              = "ingress"
  from_port         = 80
  to_port           = 80
  protocol          = "tcp"
  security_group_id = aws_security_group.this.id
  cidr_blocks       = ["0.0.0.0/0"]
}

resource "aws_security_group_rule" "https_ingress" {
  type              = "ingress"
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  security_group_id = aws_security_group.this.id
  cidr_blocks       = ["0.0.0.0/0"]
}

resource "aws_security_group_rule" "egress_all" {
  type              = "egress"
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  security_group_id = aws_security_group.this.id
  cidr_blocks       = ["0.0.0.0/0"]
}

resource "aws_lb" "this" {
  name               = var.name
  internal           = false
  load_balancer_type = "application"
  subnets            = var.public_subnet_ids
  security_groups    = [aws_security_group.this.id]

  # Deletion protection is deliberately off even for the ALB used by the production environment
  # composition's variables — production-specific hardening is applied at the environment level
  # (environments/production/main.tf), not hardcoded into this shared module.
  enable_deletion_protection = false

  tags = merge(var.tags, { Name = var.name })
}

resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.this.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  certificate_arn   = var.acm_certificate_arn

  default_action {
    type = "fixed-response"
    fixed_response {
      status_code  = "404"
      content_type = "text/plain"
      message_body = "Not found"
    }
  }
}

resource "aws_lb_listener" "http_redirect" {
  load_balancer_arn = aws_lb.this.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type = "redirect"
    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}
