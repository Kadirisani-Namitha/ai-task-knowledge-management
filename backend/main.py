import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.api.router import api_router, root_router
from app.core.config import get_settings
from app.core.logging import configure_logging

# Configure logging and application settings
configure_logging()
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="AI-Powered Task & Knowledge Management",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # ── Middleware ─────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.get_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Error handlers ─────────────────────────────────────────────────────
    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        # Return structured validation errors without stack traces
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.errors()},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        # Log the full exception server-side but never expose it to the caller
        logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An unexpected error occurred"},
        )

    # ── Routers ────────────────────────────────────────────────────────────
    app.include_router(api_router)
    app.include_router(root_router)

    # ── Startup / Shutdown ─────────────────────────────────────────────────
    @app.on_event("startup")
    async def on_startup() -> None:
        logger.info("Application starting up")
        _verify_db_connection()

    @app.on_event("shutdown")
    async def on_shutdown() -> None:
        logger.info("Application shutting down")

    return app


def _verify_db_connection() -> None:
    from sqlalchemy import text
    from app.db.session import engine

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection verified")
    except Exception:
        logger.exception("Failed to connect to the database at startup")
        raise


app = create_app()
