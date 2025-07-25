"""Main FastAPI application with clean architecture and unified patterns.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

This module implements the FastAPI application using flext-core patterns
with proper dependency injection and configuration management.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime
from typing import TYPE_CHECKING

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from flext_core import FlextLogLevel as LogLevel
from flext_observability.structured_logging import (
    LoggingConfig,
    setup_logging,
)

# Rate limiting - conditional import
# Rate limiting is REQUIRED for production
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

# Import LogLevel and LoggingConfig at the top
from flext_api import get_logger
from flext_api.infrastructure.config import APIConfig
from flext_api.infrastructure.di_container import configure_api_dependencies

# Exception handlers to be implemented when needed
from flext_api.routes import (
    auth_router,
    system_router,
)

# Create logger using FLEXT patterns - NO MANUAL LOGGING
# Create logger using flext-core get_logger function
logger = get_logger(__name__)

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from fastapi import Request

# Configure dependencies
configure_api_dependencies()

# Initialize settings with DI container
settings = APIConfig()

# Convert string to LogLevel enum
log_level_str = (
    settings.log_level.lower()
    if isinstance(settings.log_level, str)
    else settings.log_level.value.lower()
)  # log_level can be string or enum
log_level = getattr(LogLevel, log_level_str.upper(), LogLevel.INFO)

logging_config = LoggingConfig(
    service_name=settings.title,
    log_level=log_level,
    json_logs=(
        settings.log_format == "json"
    ),  # log_format is inherited from LoggingConfigMixin
    environment="development" if settings.is_development() else "production",
    version=settings.project_version,  # inherited from BaseConfigMixin
)
setup_logging(logging_config)

# Create logger factory instance and logger

# Create rate limiter if enabled and available
limiter = None
if settings.rate_limit_enabled:
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=[f"{settings.rate_limit_per_minute}/minute"],
    )


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    """Application lifespan management."""
    logger.info(f"Starting FLEXT API version {settings.version}")
    yield
    logger.info("Shutting down FLEXT API")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title=settings.title,
        description=settings.description,
        version=settings.version,
        docs_url=settings.docs_url,
        redoc_url=settings.redoc_url,
        openapi_url=settings.openapi_url,
        lifespan=lifespan,
    )

    # Configure basic exception handlers - NO OVER-ENGINEERING

    @app.exception_handler(Exception)
    async def global_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Global exception handler for all unhandled exceptions."""
        logger.error("Unhandled exception occurred")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Internal server error",
                "detail": str(exc) if app.debug else "An unexpected error occurred",
            },
        )

    # Add rate limiting if enabled
    if limiter:
        app.state.limiter = limiter

        async def rate_limit_handler(request: Request, exc: Exception) -> JSONResponse:
            """Handle rate limit exceeded exception."""
            detail = getattr(exc, "detail", "Rate limit exceeded")
            return JSONResponse(
                status_code=429, content={"detail": f"Rate limit exceeded: {detail}"}
            )

        app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

    # Add CORS middleware - always enabled
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,  # Using cors_origins property
        allow_credentials=settings.cors_credentials,
        allow_methods=settings.cors_methods,
        allow_headers=settings.cors_headers,
    )

    # Add trusted host middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.trusted_hosts,
    )

    # Include all routers
    app.include_router(auth_router)
    # Temporarily disabled due to missing models
    # app.include_router(pipelines_router)
    # app.include_router(plugins_router)
    app.include_router(system_router)

    @app.get("/")
    async def root() -> dict[str, str]:
        """Root endpoint with API information."""
        return {
            "message": "FLEXT API is running",
            "version": settings.version,
            "project": settings.title,
            "environment": "development" if settings.is_development() else "production",
            "docs": settings.docs_url or "disabled",
            "health": "/health",
        }

    @app.get("/health")
    async def health_check() -> dict[str, str]:
        """Basic health check endpoint."""
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
        }

    @app.get("/health/ready")
    async def readiness_check() -> dict[str, str]:
        """Readiness probe endpoint."""
        return {
            "status": "ready",
            "timestamp": datetime.now().isoformat(),
        }

    return app


# Create the app instance
app = create_app()


def main() -> None:
    """Run the main application entry point."""
    logger.info(
        f"Starting FLEXT API server - {settings.title} v{settings.version} ({'development' if settings.is_development() else 'production'})"
    )

    uvicorn.run(
        "flext_api.app:app",
        host=settings.host,
        port=settings.port,
        workers=settings.workers,
        reload=settings.reload,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
