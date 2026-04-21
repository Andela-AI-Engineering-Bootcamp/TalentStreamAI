output "stack_name" {
  value       = local.name
  description = "Composite name (project + environment) for tagging and future resource naming."
}

output "aws_region" {
  value       = var.aws_region
  description = "Region the AWS provider is configured to use."
}

output "next_steps" {
  value       = <<-EOT
    Terraform is intentionally empty: add resources under this root module (or introduce child modules) following the checklist in main.tf.
    Wire remote state (backend.hcl), then iterate with `terraform plan` before any apply in a shared account.
  EOT
  description = "Human-oriented reminder for implementers."
}
