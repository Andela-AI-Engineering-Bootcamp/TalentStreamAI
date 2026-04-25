output "stack_name" {
  value       = local.name
  description = "Composite name (project + environment) for tagging and future resource naming."
}

output "aws_region" {
  value       = var.aws_region
  description = "Region the AWS provider is configured to use."
}

output "cloudfront_url" {
  description = "Primary app URL."
  value       = "https://${aws_cloudfront_distribution.cdn.domain_name}"
}

output "cloudfront_distribution_id" {
  description = "Used for cache invalidations during deploy."
  value       = aws_cloudfront_distribution.cdn.id
}

output "frontend_bucket_name" {
  description = "S3 bucket that stores the static frontend."
  value       = aws_s3_bucket.frontend.id
}

output "uploads_bucket_name" {
  description = "Private S3 bucket used for user uploads when the API is configured for S3 storage."
  value       = aws_s3_bucket.uploads.id
}

output "app_secrets_secret_arn" {
  description = "AWS Secrets Manager secret that stores sensitive API keys (loaded by Lambda on cold start)."
  value       = aws_secretsmanager_secret.app.arn
  sensitive   = true
}

output "api_cors_origins" {
  description = "The computed `CORS_ORIGINS` value passed to the API Lambda (includes the CloudFront URL)."
  value       = local.cors_joined
}

output "next_public_env" {
  description = "Expected `NEXT_PUBLIC_*` values for the static frontend build (not applied to AWS by Terraform)."
  value       = var.next_public
}

output "api_gateway_url" {
  description = "Direct API Gateway URL (CloudFront also routes /api/*)."
  value       = aws_apigatewayv2_api.http.api_endpoint
}

output "github_actions_role_arn" {
  description = "IAM role assumed by GitHub Actions via OIDC (if enabled)."
  value       = var.enable_github_oidc ? aws_iam_role.github_actions[0].arn : null
}

output "terraform_state_bucket_name" {
  description = "S3 bucket for Terraform state (if manage_terraform_state_backend = true). Use in backend.hcl after first apply + state migration."
  value       = var.manage_terraform_state_backend ? aws_s3_bucket.terraform_state[0].id : null
}

output "terraform_state_lock_table_name" {
  description = "DynamoDB table for state locking (if manage_terraform_state_backend = true)."
  value       = var.manage_terraform_state_backend ? aws_dynamodb_table.terraform_state_lock[0].name : null
}
