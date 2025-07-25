"""FlextAPIBuilder - Powerful API construction with massive code reduction.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

This builder reduces FastAPI application setup from 100+ lines to 10-20 lines.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from flext_core import FlextResult, get_logger
from pydantic import BaseModel

from flext_api.helpers.middleware import (
    FlextLoggingMiddleware,
    FlextRateLimitMiddleware,
    FlextSecurityMiddleware,
)

if TYPE_CHECKING:
    from collections.abc import Callable

logger = get_logger(__name__)


class FlextAPIConfig(BaseModel):
    """Configuration for FlextAPIBuilder."""

    title: str = "FLEXT API"
    description: str = "Enterprise API built with FLEXT"
    version: str = "1.0.0"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    openapi_url: str = "/openapi.json"

    # CORS settings
    cors_origins: list[str] = ["*"]
    cors_credentials: bool = True
    cors_methods: list[str] = ["*"]
    cors_headers: list[str] = ["*"]

    # Security settings
    trusted_hosts: list[str] = ["*"]
    rate_limit_enabled: bool = True
    rate_limit_per_minute: int = 100

    # Logging settings
    enable_request_logging: bool = True
    enable_response_logging: bool = True
    log_level: str = "INFO"


class FlextAPIBuilder:
    """Powerful FastAPI builder for massive code reduction.

    Example usage:
        app = (FlextAPIBuilder()
               .with_cors()
               .with_auth()
               .with_rate_limiting()
               .with_logging()
               .add_health_checks()
               .build())

    This replaces 100+ lines of boilerplate FastAPI setup.
    """

    def __init__(self, config: FlextAPIConfig | None = None) -> None:
        """Initialize builder with optional configuration."""
        self.config = config or FlextAPIConfig()
        self.app = FastAPI(
            title=self.config.title,
            description=self.config.description,
            version=self.config.version,
            docs_url=self.config.docs_url,
            redoc_url=self.config.redoc_url,
            openapi_url=self.config.openapi_url,
            lifespan=self._create_lifespan(),
        )
        self._middlewares: list[tuple[type, dict[str, Any]]] = []
        self._exception_handlers: list[tuple[type, Callable]] = []
        self._startup_tasks: list[Callable] = []
        self._shutdown_tasks: list[Callable] = []

    def with_cors(
        self,
        origins: list[str] | None = None,
        credentials: bool | None = None,
        methods: list[str] | None = None,
        headers: list[str] | None = None,
    ) -> FlextAPIBuilder:
        """Add CORS middleware with sensible defaults."""
        cors_config = {
            "allow_origins": origins or self.config.cors_origins,
            "allow_credentials": credentials or self.config.cors_credentials,
            "allow_methods": methods or self.config.cors_methods,
            "allow_headers": headers or self.config.cors_headers,
        }
        self._middlewares.append((CORSMiddleware, cors_config))
        return self

    def with_trusted_hosts(self, hosts: list[str] | None = None) -> FlextAPIBuilder:
        """Add trusted host middleware."""
        config = {"allowed_hosts": hosts or self.config.trusted_hosts}
        self._middlewares.append((TrustedHostMiddleware, config))
        return self

    def with_rate_limiting(
        self,
        enabled: bool | None = None,
        per_minute: int | None = None,
    ) -> FlextAPIBuilder:
        """Add rate limiting middleware."""
        if enabled is False or (enabled is None and not self.config.rate_limit_enabled):
            return self

        limit = per_minute or self.config.rate_limit_per_minute
        self._middlewares.append((FlextRateLimitMiddleware, {"limit": limit}))
        return self

    def with_security(self) -> FlextAPIBuilder:
        """Add security headers middleware."""
        self._middlewares.append((FlextSecurityMiddleware, {}))
        return self

    def with_logging(
        self,
        enable_requests: bool | None = None,
        enable_responses: bool | None = None,
    ) -> FlextAPIBuilder:
        """Add request/response logging middleware."""
        config = {
            "log_requests": enable_requests or self.config.enable_request_logging,
            "log_responses": enable_responses or self.config.enable_response_logging,
        }
        self._middlewares.append((FlextLoggingMiddleware, config))
        return self

    def with_exception_handler(
        self,
        exception_type: type[Exception],
        handler: Callable[[Request, Exception], JSONResponse],
    ) -> FlextAPIBuilder:
        """Add custom exception handler."""
        self._exception_handlers.append((exception_type, handler))
        return self

    def with_global_exception_handler(self) -> FlextAPIBuilder:
        """Add global exception handler for all unhandled exceptions."""
        async def global_handler(request: Request, exc: Exception) -> JSONResponse:
            logger.error("Unhandled exception occurred")
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": "Internal server error",
                    "detail": str(exc) if self.app.debug else "An unexpected error occurred",
                },
            )

        self._exception_handlers.append((Exception, global_handler))
        return self

    def add_startup_task(self, task: Callable) -> FlextAPIBuilder:
        """Add startup task."""
        self._startup_tasks.append(task)
        return self

    def add_shutdown_task(self, task: Callable) -> FlextAPIBuilder:
        """Add shutdown task."""
        self._shutdown_tasks.append(task)
        return self

    def add_health_checks(self) -> FlextAPIBuilder:
        """Add standard health check endpoints."""
        from datetime import datetime

        @self.app.get("/health")
        async def health_check() -> dict[str, str]:
            """Basic health check endpoint."""
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "service": self.config.title,
                "version": self.config.version,
            }

        @self.app.get("/health/ready")
        async def readiness_check() -> dict[str, str]:
            """Readiness probe endpoint."""
            return {
                "status": "ready",
                "timestamp": datetime.now().isoformat(),
            }

        @self.app.get("/health/live")
        async def liveness_check() -> dict[str, str]:
            """Liveness probe endpoint."""
            return {
                "status": "alive",
                "timestamp": datetime.now().isoformat(),
            }

        return self

    def add_info_endpoint(self) -> FlextAPIBuilder:
        """Add API information endpoint."""
        @self.app.get("/")
        async def api_info() -> dict[str, str]:
            """Root endpoint with API information."""
            return {
                "message": f"{self.config.title} is running",
                "version": self.config.version,
                "docs": self.config.docs_url,
                "redoc": self.config.redoc_url,
                "health": "/health",
            }

        return self

    def build(self) -> FastAPI:
        """Build and return the configured FastAPI application."""
        # Add all middlewares
        for middleware_class, config in reversed(self._middlewares):
            self.app.add_middleware(middleware_class, **config)

        # Add all exception handlers
        for exception_type, handler in self._exception_handlers:
            self.app.add_exception_handler(exception_type, handler)

        logger.info(f"Built {self.config.title} with {len(self._middlewares)} middlewares")
        return self.app

    def _create_lifespan(self) -> any:
        """Create lifespan context manager for startup/shutdown tasks."""
        @asynccontextmanager
        async def lifespan(app: FastAPI) -> None:
            # Startup
            logger.info(f"Starting {self.config.title} v{self.config.version}")
            for task in self._startup_tasks:
                try:
                    if callable(task):
                        await task() if hasattr(task, "__await__") else task()
                except Exception as e:
                    logger.exception(f"Startup task failed: {e}")

            yield

            # Shutdown
            logger.info(f"Shutting down {self.config.title}")
            for task in self._shutdown_tasks:
                try:
                    if callable(task):
                        await task() if hasattr(task, "__await__") else task()
                except Exception as e:
                    logger.exception(f"Shutdown task failed: {e}")

        return lifespan


# Convenience function for even more code reduction
def create_flext_api(
    title: str = "FLEXT API",
    version: str = "1.0.0",
    description: str = "Enterprise API built with FLEXT",
    enable_cors: bool = True,
    enable_auth: bool = False,
    enable_rate_limiting: bool = True,
    enable_logging: bool = True,
    enable_security: bool = True,
    add_health_checks: bool = True,
    add_info_endpoint: bool = True,
) -> FastAPI:
    """Create a fully configured FastAPI app with one function call.

    This single function replaces 100+ lines of FastAPI boilerplate.

    Args:
        title: API title
        version: API version
        description: API description
        enable_cors: Enable CORS middleware
        enable_auth: Enable authentication (future)
        enable_rate_limiting: Enable rate limiting
        enable_logging: Enable request logging
        enable_security: Enable security headers
        add_health_checks: Add health check endpoints
        add_info_endpoint: Add info endpoint

    Returns:
        Fully configured FastAPI application

    Example:
        # This replaces 100+ lines of FastAPI setup:
        app = create_flext_api(
            title="My API",
            version="2.0.0",
            enable_cors=True,
            enable_rate_limiting=True
        )

    """
    config = FlextAPIConfig(title=title, version=version, description=description)
    builder = FlextAPIBuilder(config)

    if enable_cors:
        builder.with_cors()

    if enable_rate_limiting:
        builder.with_rate_limiting()

    if enable_logging:
        builder.with_logging()

    if enable_security:
        builder.with_security().with_trusted_hosts()

    if add_health_checks:
        builder.add_health_checks()

    if add_info_endpoint:
        builder.add_info_endpoint()

    # Always add global exception handler
    builder.with_global_exception_handler()

    return builder.build()
