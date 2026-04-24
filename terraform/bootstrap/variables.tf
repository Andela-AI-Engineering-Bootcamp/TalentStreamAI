variable "aws_region" {
  type        = string
  description = "Region for the state bucket and lock table (must match the main root backend.hcl region)."
  default     = "eu-central-1"
}

variable "state_bucket_name" {
  type        = string
  description = "Globally unique S3 bucket name for Terraform remote state."
}

variable "dynamodb_table_name" {
  type        = string
  description = "DynamoDB table name for S3 backend state locking (backend dynamodb_table)."
  default     = "terraform-locks"
}

variable "force_destroy_state_bucket" {
  type        = bool
  description = "If true, the state bucket can be emptied and destroyed by Terraform. Use false in production."
  default     = false
}
