variable "aws_region" {
  type        = string
  description = "Primary AWS region for future resources."
  default     = "us-east-1"
}

variable "project_name" {
  type        = string
  description = "Short name used in tagging and future resource names."
  default     = "talentstreamai"
}

variable "environment" {
  type        = string
  description = "Deployment stage label (not read by application code; use for tags and state keys)."

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment must be one of: dev, staging, prod."
  }
}
