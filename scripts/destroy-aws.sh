#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TF_DIR="$ROOT/terraform"
ENVIRONMENT="${TF_ENVIRONMENT:-${1:-dev}}"

if ! command -v terraform >/dev/null 2>&1; then
  echo "Terraform is not installed or not on PATH."
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

if [ ! -d .terraform ]; then
  echo "Terraform has not been initialized in $TF_DIR. Run ./scripts/deploy-aws.sh first."
  exit 1
fi

echo "Scaffold: destroy is a no-op until resources exist. When they do, this will remove environment=${ENVIRONMENT} from state."
read -r -p "Type 'destroy' to continue: " confirm
if [ "$confirm" != "destroy" ]; then
  echo "Aborted."
  exit 1
fi

terraform destroy -auto-approve -var="environment=${ENVIRONMENT}"
