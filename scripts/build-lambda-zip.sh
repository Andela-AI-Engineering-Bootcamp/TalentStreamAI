#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_ZIP="${ROOT}/terraform/build/api_lambda.zip"
PKG_DIR="${ROOT}/terraform/build/lambda_pkg"

echo "Building Lambda zip: ${OUT_ZIP}"

rm -f "${OUT_ZIP}"
rm -rf "${PKG_DIR}"
mkdir -p "${PKG_DIR}"

if command -v uv >/dev/null 2>&1; then
  echo "Using uv export (frozen) from backend lockfile"
  uv export --frozen --no-dev --project "${ROOT}/backend" -o "${PKG_DIR}/requirements.txt"
  python3 -m pip install -r "${PKG_DIR}/requirements.txt" -t "${PKG_DIR}" --no-cache-dir
else
  echo "uv not found; falling back to backend/lambda/requirements-lambda.txt"
  python3 -m pip install -r "${ROOT}/backend/lambda/requirements-lambda.txt" -t "${PKG_DIR}" --no-cache-dir
fi

cp -R "${ROOT}/backend/app" "${PKG_DIR}/app"
cp "${ROOT}/backend/lambda/lambda_handler.py" "${PKG_DIR}/lambda_handler.py"

python3 - <<PY
import os, zipfile

out = r"""${OUT_ZIP}"""
root = r"""${PKG_DIR}"""
os.makedirs(os.path.dirname(out), exist_ok=True)

def should_skip(path: str) -> bool:
  p = path.replace(os.sep, "/")
  if "/__pycache__/" in p:
    return True
  if p.endswith((".pyc", ".pyo")):
    return True
  return False

with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as z:
  for base, _, files in os.walk(root):
    for name in files:
      full = os.path.join(base, name)
      if should_skip(full):
        continue
      rel = os.path.relpath(full, root)
      z.write(full, arcname=rel)
print("Wrote", out, f"({os.path.getsize(out)} bytes)")
PY
