"""Health & readiness endpoints."""

from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import text

from app.core.database import async_session_factory

router = APIRouter()


@router.get("/health")
async def health() -> dict:
    """Liveness probe — always returns 200 if the process is running."""
    return {"status": "ok", "service": "lumina-v3"}


@router.get("/ready")
async def ready() -> dict:
    """Readiness probe — checks DB connectivity."""
    try:
        async with async_session_factory() as session:
            await session.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    status = "ready" if db_ok else "not_ready"
    return {"status": status, "database": db_ok}
