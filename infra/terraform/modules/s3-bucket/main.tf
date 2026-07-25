####################################################################################################
# Generic private S3 bucket module — instantiated once per use case (call recordings, knowledge
# base source documents) rather than sharing a single bucket, so retention/lifecycle policies and
# access patterns can differ per data type without conditionals scattered through one bucket's
# config. Public access is blocked unconditionally; anything client-facing goes through presigned
# URLs, never a public bucket policy.
####################################################################################################

resource "aws_s3_bucket" "this" {
  bucket = var.bucket_name
  tags   = merge(var.tags, { Name = var.bucket_name })
}

resource "aws_s3_bucket_public_access_block" "this" {
  bucket                  = aws_s3_bucket.this.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "this" {
  bucket = aws_s3_bucket.this.id
  versioning_configuration {
    status = var.versioning_enabled ? "Enabled" : "Disabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "this" {
  bucket = aws_s3_bucket.this.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "aws:kms"
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "this" {
  count  = var.lifecycle_transition_days != null || var.lifecycle_expiration_days != null ? 1 : 0
  bucket = aws_s3_bucket.this.id

  rule {
    id     = "retention-policy"
    status = "Enabled"

    # Explicit empty filter = applies to every object in the bucket. Newer AWS provider versions
    # warn (soon: error) without this — a rule with no filter/prefix is ambiguous about scope.
    filter {}

    dynamic "transition" {
      for_each = var.lifecycle_transition_days != null ? [1] : []
      content {
        days          = var.lifecycle_transition_days
        storage_class = "GLACIER"
      }
    }

    dynamic "expiration" {
      for_each = var.lifecycle_expiration_days != null ? [1] : []
      content {
        days = var.lifecycle_expiration_days
      }
    }
  }
}

resource "aws_s3_bucket_cors_configuration" "this" {
  count  = length(var.cors_allowed_origins) > 0 ? 1 : 0
  bucket = aws_s3_bucket.this.id

  cors_rule {
    allowed_methods = ["GET", "PUT", "POST"]
    allowed_origins = var.cors_allowed_origins
    allowed_headers = ["*"]
    max_age_seconds = 3000
  }
}
