from datetime import UTC, datetime

from fastapi import APIRouter

from app.core.config import settings

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    payload: dict[str, str] = {"status": "ok", "time": datetime.now(UTC).isoformat()}
    if settings.deployment_environment:
        payload["deployment_environment"] = settings.deployment_environment
    return payload
