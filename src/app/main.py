"""Main FastAPI application."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from .config import get_settings
from .exception_handlers import register_exception_handlers
from .logging_config import get_logger, setup_logging
from .middleware import (
    ErrorTrackingMiddleware,
    RequestLoggingMiddleware,
    RequestValidationMiddleware,
    SecurityHeadersMiddleware,
)
from .routers import widgets_router

# Set up logging first
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan context manager."""
    from .database import create_tables

    # Import models to register them with SQLAlchemy metadata
    from .models import Widget  # noqa: F401

    # Startup
    logger.info("Starting up Widget CRUD API...")
    await create_tables()
    logger.info("Database tables created/verified")
    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down Widget CRUD API...")
    logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    """Create FastAPI application instance."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="A production-ready CRUD REST API for Widget resources",
        docs_url=settings.docs_url,
        redoc_url=settings.redoc_url,
        openapi_url=settings.openapi_url,
        lifespan=lifespan,
    )

    # Add middleware in order (first added = outermost layer)
    # Security headers should be outermost
    app.add_middleware(SecurityHeadersMiddleware)

    # Error tracking middleware
    app.add_middleware(ErrorTrackingMiddleware)

    # Request logging middleware
    app.add_middleware(RequestLoggingMiddleware)

    # Request validation middleware
    app.add_middleware(RequestValidationMiddleware)

    # Add CORS middleware (this should be after our custom middleware)
    from fastapi.middleware.cors import CORSMiddleware

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )

    # Register exception handlers
    register_exception_handlers(app)

    # Health check endpoint
    @app.get("/health", tags=["Health"])
    async def health_check() -> dict[str, str]:
        """Health check endpoint."""
        logger.info("Health check requested")
        return {"status": "healthy", "service": settings.app_name}

    # Root endpoint
    @app.get("/", tags=["Root"])
    async def root() -> dict[str, str]:
        """Root endpoint."""
        return {
            "message": f"Welcome to {settings.app_name}",
            "version": settings.app_version,
            "docs": "/docs",
        }

    # Include routers
    app.include_router(widgets_router)

    logger.info("FastAPI application created successfully")
    return app


# Create the application instance
app = create_app()
