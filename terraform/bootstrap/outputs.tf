output "state_bucket_name" {
  value       = aws_s3_bucket.terraform_state.bucket
  description = "backend \"bucket\" in terraform/backend.hcl."
}

output "dynamodb_table_name" {
  value       = aws_dynamodb_table.terraform_locks.name
  description = "backend \"dynamodb_table\" in terraform/backend.hcl."
}

output "state_bucket_arn" {
  value       = aws_s3_bucket.terraform_state.arn
  description = "state_bucket_arn in the main terraform/terraform.tfvars (GitHub deploy role)."
}

output "state_bucket_objects_arn" {
  value       = "${aws_s3_bucket.terraform_state.arn}/*"
  description = "state_bucket_objects_arn in the main terraform/terraform.tfvars."
}

output "state_lock_table_arn" {
  value       = aws_dynamodb_table.terraform_locks.arn
  description = "state_lock_table_arn in the main terraform/terraform.tfvars."
}

output "backend_hcl_snippet" {
  value       = <<-EOT
    bucket         = "${aws_s3_bucket.terraform_state.bucket}"
    key            = "talentstreamai/dev/terraform.tfstate"
    region         = "${var.aws_region}"
    dynamodb_table = "${aws_dynamodb_table.terraform_locks.name}"
    encrypt        = true
  EOT
  description = "Values for terraform/backend.hcl (adjust key per environment)."
}
