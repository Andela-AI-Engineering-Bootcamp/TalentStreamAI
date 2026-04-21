#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is required for this script. Install Docker Desktop or the Docker engine, then retry."
  exit 1
fi

echo "Building and starting TalentStreamAI (frontend :3000, backend :8000)..."
if [ -f "$ROOT/.env" ]; then
  # Compose reads environment variables for interpolation; exporting keeps config in one place.
  set -a
  # shellcheck disable=SC1091
  source "$ROOT/.env"
  set +a
fi

docker compose up --build
