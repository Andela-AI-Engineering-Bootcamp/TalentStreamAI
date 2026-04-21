terraform {
  required_version = ">= 1.6.0"

  backend "s3" {}

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.75"
    }
  }
}

locals {
  name = "${var.project_name}-${var.environment}"
}

# ---------------------------------------------------------------------------
# Scaffold only — no AWS resources are declared here on purpose.
#
# Implement the reference architecture in this order (split into modules or
# keep flat until the shape stabilizes):
#
# 1) Networking — VPC, public/private subnets, routing, NAT (or reuse an account landing zone).
# 2) Data — Aurora Serverless v2, RDS-managed master secret in Secrets Manager, Data API enabled.
# 3) App secrets — Secrets Manager entries the ECS/Lambda task will read (OpenRouter, etc.).
# 4) Compute — ECS Fargate (LangGraph + OpenRouter client) or Lambda behind API Gateway; ECR for images.
# 5) Edge — API Gateway HTTP API (Clerk JWT authorizer on protected routes), CloudFront + S3 for the static Next export.
# 6) CI/CD — GitHub Actions OIDC role with least privilege for plan/apply and for publishing artifacts.
# ---------------------------------------------------------------------------
