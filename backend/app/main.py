"""Lumina V3 — FastAPI application factory."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.errors import register_error_handlers
from app.core.middleware import register_middleware, setup_structlog


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Startup and shutdown lifecycle."""
    import structlog

    logger = structlog.get_logger()
    await logger.ainfo("startup", message="Lumina V3 starting up")
    yield
    await logger.ainfo("shutdown", message="Lumina V3 shutting down")


def create_app() -> FastAPI:
    """Application factory — returns a fully configured FastAPI instance."""
    settings = get_settings()

    app = FastAPI(
        title="Lumina V3 — Telegram School OS",
        version="3.0.0",
        description="Electronic journal, diary, schedule, analytics & gamification",
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        lifespan=lifespan,
    )

    # -- Structured logging --
    setup_structlog()

    # -- CORS --
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.app_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )

    # -- Custom middleware --
    register_middleware(app)

    # -- Error handlers --
    register_error_handlers(app)

    # -- Routers --
    _register_routers(app)

    return app


def _register_routers(app: FastAPI) -> None:
    """Register all API routers."""
    from app.api.admin import router as admin_router
    from app.api.auth import router as auth_router
    from app.api.health import router as health_router
    from app.api.parent import router as parent_router
    from app.api.student import router as student_router
    from app.api.teacher import router as teacher_router

    app.include_router(health_router, tags=["Health"])
    app.include_router(health_router, prefix="/api/health", tags=["Health"])
    app.include_router(health_router, prefix="/api/v1/health", tags=["Health"])

    for prefix in ["/api/v1", "/api"]:
        app.include_router(auth_router, prefix=f"{prefix}/auth", tags=["Auth"])
        app.include_router(admin_router, prefix=f"{prefix}/admin", tags=["Admin"])
        app.include_router(teacher_router, prefix=f"{prefix}/teacher", tags=["Teacher"])
        app.include_router(student_router, prefix=f"{prefix}/student", tags=["Student"])
        app.include_router(parent_router, prefix=f"{prefix}/parent", tags=["Parent"])


# Default application instance for ASGI servers and test clients
app = create_app()

