#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is required for this script. Install Docker Desktop or the Docker engine, then retry."
  exit 1
fi

echo "Building and starting TalentStreamAI (frontend :3000, backend :8000)..."
docker compose up --build
