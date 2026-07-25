provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "pluto-ai"
      Environment = "dev"
      ManagedBy   = "terraform"
    }
  }
}
