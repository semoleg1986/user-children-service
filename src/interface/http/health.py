from __future__ import annotations

from fastapi import APIRouter, Response, status

router = APIRouter()


@router.get("/healthz", status_code=status.HTTP_200_OK)
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/readyz", status_code=status.HTTP_200_OK)
async def readyz(response: Response) -> dict[str, str]:
    # Minimal readiness: app is up. Extend with DB/JWKS checks later.
    return {"status": "ready"}
