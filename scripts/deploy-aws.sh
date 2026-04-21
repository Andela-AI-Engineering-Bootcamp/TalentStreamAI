#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TF_DIR="$ROOT/terraform"
ENVIRONMENT="${TF_ENVIRONMENT:-${1:-dev}}"

if ! command -v terraform >/dev/null 2>&1; then
  echo "Terraform is not installed or not on PATH."
  exit 1
fi

if ! command -v aws >/dev/null 2>&1; then
  echo "AWS CLI is not installed. Install it and configure credentials before using remote state."
  exit 1
fi

case "$ENVIRONMENT" in
  dev | staging | prod) ;;
  *)
    echo "Invalid environment: $ENVIRONMENT (expected dev, staging, or prod)"
    exit 1
    ;;
esac

cd "$TF_DIR"

if [ -f backend.hcl ]; then
  terraform init -input=false -backend-config=backend.hcl
elif [ "${TALENTSTREAM_USE_LOCAL_TF_STATE:-}" = "1" ]; then
  echo "Using local Terraform state (TALENTSTREAM_USE_LOCAL_TF_STATE=1)."
  terraform init -input=false -backend=false
else
  echo "Missing $TF_DIR/backend.hcl"
  echo "Copy backend.hcl.example to backend.hcl and fill in your S3 remote state settings,"
  echo "or export TALENTSTREAM_USE_LOCAL_TF_STATE=1 for a disposable local state file."
  exit 1
fi

if [ ! -f terraform.tfvars ]; then
  echo "Missing terraform.tfvars in $TF_DIR"
  echo "Copy terraform.tfvars.example to terraform.tfvars, adjust values, then rerun."
  exit 1
fi

terraform plan -var="environment=${ENVIRONMENT}" -out=tfplan
echo
echo "Scaffold: there are no resources in main.tf yet. When you add them, review the plan and run:"
echo "  terraform apply tfplan"
