#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is not installed. Install it from https://docs.astral.sh/uv/getting-started/installation/"
  exit 1
fi

echo "Installing frontend dependencies..."
(cd frontend && npm install)

echo "Syncing backend dependencies with uv..."
(cd backend && uv sync)

if [ ! -f "$ROOT/.env" ]; then
  if [ -f "$ROOT/.env.example" ]; then
    echo
    echo "No root .env file found. Copy .env.example to .env and adjust values as needed."
  fi
fi

echo
echo "Done."
echo "Backend: cd backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo "Frontend: cd frontend && npm run dev"
