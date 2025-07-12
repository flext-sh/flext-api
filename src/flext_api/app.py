"""Main FastAPI application with clean architecture and unified patterns.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

This module implements the FastAPI application using flext-core patterns
with proper dependency injection and configuration management.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from flext_api.config import get_api_settings
from flext_api.infrastructure.di_container import configure_api_dependencies
from flext_api.routes import auth_router
from flext_api.routes import pipelines_router
from flext_api.routes import plugins_router
from flext_api.routes import system_router

# Import LogLevel and LoggingConfig at the top
from flext_core import LogLevel
from flext_observability.logging import LoggingConfig
from flext_observability.logging import get_logger
from flext_observability.logging import setup_logging

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

# Configure dependencies
configure_api_dependencies()

# Initialize settings with DI container
settings = get_api_settings()

# Convert string to LogLevel enum
log_level_str = settings.log_level.lower()
log_level = getattr(LogLevel, log_level_str.upper(), LogLevel.INFO)

logging_config = LoggingConfig(
    service_name=settings.project_name,
    log_level=log_level,
    json_logs=(settings.log_format == "json"),
    environment=settings.environment,
    version=settings.docs.version,
)
setup_logging(logging_config)

# Get logger
logger = get_logger(__name__)

# Create rate limiter if enabled
limiter = None
if settings.rate_limit_enabled:
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=[f"{settings.rate_limit_per_minute}/minute"],
    )


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    """Application lifespan management."""
    logger.info("Starting FLEXT API version %s", settings.project_version)
    yield
    logger.info("Shutting down FLEXT API")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title=settings.docs.title,
        description=settings.docs.description,
        version=settings.docs.version,
        docs_url=settings.docs.docs_url,
        redoc_url=settings.docs.redoc_url,
        openapi_url=settings.docs.openapi_url,
        lifespan=lifespan,
    )

    # Add rate limiting if enabled
    if limiter:
        app.state.limiter = limiter
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Add CORS middleware if enabled
    if settings.cors.enabled:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors.allow_origins,
            allow_credentials=settings.cors.allow_credentials,
            allow_methods=settings.cors.allow_methods,
            allow_headers=settings.cors.allow_headers,
        )

    # Add trusted host middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.security.trusted_hosts,
    )

    # Include all routers
    app.include_router(auth_router)
    app.include_router(pipelines_router)
    app.include_router(plugins_router)
    app.include_router(system_router)

    @app.get("/")
    async def root() -> dict[str, str]:
        """Root endpoint with API information."""
        return {
            "message": "FLEXT API is running",
            "version": settings.project_version,
            "project": settings.project_name,
            "environment": settings.environment,
            "docs": settings.docs.docs_url or "disabled",
            "health": "/system/health",
        }

    return app


# Create the app instance
app = create_app()


def main() -> None:
    """Run the main application entry point."""
    logger.info(
        "Starting FLEXT API server - %s v%s (%s)",
        settings.project_name,
        settings.project_version,
        settings.environment,
    )

    uvicorn.run(
        "flext_api.app:app",
        host=settings.server.host,
        port=settings.server.port,
        workers=settings.server.workers,
        reload=settings.server.reload,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
