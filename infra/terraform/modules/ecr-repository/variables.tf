variable "name" {
  type = string
}

variable "image_tag_mutability" {
  type        = string
  default     = "IMMUTABLE"
  description = "IMMUTABLE — matches the SHA-tagged, never-overwritten image policy in docs/product/03-technical-specifications.md."
}

variable "max_untagged_image_count" {
  type    = number
  default = 10
}

variable "tags" {
  type    = map(string)
  default = {}
}
