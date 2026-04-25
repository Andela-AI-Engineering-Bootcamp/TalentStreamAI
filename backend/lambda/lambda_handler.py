import json
import os
from typing import Any

import boto3


def _load_secrets_from_env() -> None:
  """Merge JSON secrets from AWS Secrets Manager into `os.environ` (before importing the app)."""
  secret_id = (os.environ.get("TALENTSTREAM_SECRETS_ID") or "").strip()
  if not secret_id:
    return

  client = boto3.client("secretsmanager", region_name=os.environ.get("AWS_REGION"))
  resp = client.get_secret_value(SecretId=secret_id)
  raw = (resp.get("SecretString") or "").strip()
  if not raw:
    return

  data = json.loads(raw)
  if not isinstance(data, dict):
    raise RuntimeError("App secret JSON must be an object at the top level.")

  for k, v in data.items():
    if v is None:
      continue
    if isinstance(v, (dict, list)):
      os.environ[str(k)] = json.dumps(v)
    else:
      os.environ[str(k)] = str(v)


def _apply_lambda_runtime_defaults() -> None:
  # Lambda has a read-only filesystem except /tmp. Local dev continues to use repo `.data/`.
  if (os.environ.get("TALENTSTREAM_AWS_LAMBDA") or "").strip() == "1":
    os.environ.setdefault("SQLITE_PATH", "/tmp/talentstreamai.sqlite3")
    os.environ.setdefault("UPLOAD_DIR", "/tmp/uploads")


_load_secrets_from_env()
_apply_lambda_runtime_defaults()

from mangum import Mangum  # noqa: E402  (import after env is prepared)

from app.main import app  # noqa: E402


handler: Any = Mangum(app, lifespan="off")

