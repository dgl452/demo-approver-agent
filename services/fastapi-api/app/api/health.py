from fastapi import APIRouter, Depends

from app.auth import require_api_key

router = APIRouter(dependencies=[Depends(require_api_key)])


@router.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
