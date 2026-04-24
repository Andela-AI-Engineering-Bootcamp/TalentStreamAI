# One-time Terraform remote state bootstrap

Creates the **S3 bucket** and **DynamoDB lock table** used by the main root (`terraform/`) backend. This module keeps **local** Terraform state (not stored in the bucket it creates).

## Prerequisites

- AWS credentials with permission to create S3 buckets and DynamoDB tables in the target account.

## Steps

1. Choose a **globally unique** `state_bucket_name` (S3 bucket names are global).

2. Copy variables and apply:

   ```bash
   cd terraform/bootstrap
   cp terraform.tfvars.example terraform.tfvars
   # edit terraform.tfvars
   terraform init
   terraform apply
   ```

3. Wire the main stack:

   - Copy `terraform output -raw backend_hcl_snippet` into `terraform/backend.hcl` (or merge with `backend.hcl.example`), and adjust `key` if needed.
   - Set `state_bucket_arn`, `state_bucket_objects_arn`, and `state_lock_table_arn` in `terraform/terraform.tfvars` from `terraform output` in this directory.

4. From **`terraform/`** (main root):

   ```bash
   terraform init -backend-config=backend.hcl
   ```

`aws_region` here must match `region` in `backend.hcl` and the DynamoDB table ARN region in the main `terraform.tfvars`.
