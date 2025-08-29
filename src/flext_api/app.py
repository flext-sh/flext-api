"""FLEXT API FastAPI application - CONSOLIDATED ARCHITECTURE.

Este módulo implementa o padrão CONSOLIDATED seguindo FLEXT_REFACTORING_PROMPT.md.
Toda a funcionalidade da aplicação FastAPI está centralizada na classe FlextApiApp,
eliminando a violação de "múltiplas classes por módulo" e garantindo
consistência arquitetural.

Padrões FLEXT aplicados:
- Classe CONSOLIDADA FlextApiApp contendo toda a funcionalidade da aplicação
- Herança de flext-core FlextDomainService
- FlextResult para operações que podem falhar
- Imports diretos sem TYPE_CHECKING

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import argparse

# Datetime operations now use FlextUtilities.generate_iso_timestamp() - no direct datetime import needed
import inspect
import sys

# UUID generation now use FlextUtilities.generate_uuid() - no direct uuid import needed
from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager
from typing import TypedDict, cast, override

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from flext_core import (
    FlextConstants,
    FlextDomainService,
    FlextResult,
    FlextUtilities,
    get_logger,
)

from flext_api.config import FlextApiSettings, create_api_settings
from flext_api.exceptions import FlextApiError, create_error_response
from flext_api.storage import FlextApiStorage, create_memory_storage

# Type definitions will be provided by FlextApiApp consolidated class


logger = get_logger(__name__)


# Internal helper to intentionally fail initialization for tests
def _forced_init_failure() -> None:
    raise RuntimeError


# ==============================================================================
# CONSOLIDATED FLEXT API APP CLASS
# ==============================================================================


class FlextApiApp(FlextDomainService[dict[str, object]]):
    """Single consolidated class containing all FastAPI application functionality following FLEXT patterns.

    This class follows the CONSOLIDATED class pattern from FLEXT_REFACTORING_PROMPT.md,
    centralizing all application functionality into a single class structure to eliminate
    the "multiple classes per module" violation while maintaining clean
    architecture principles.

    All application classes and functionality are defined as nested classes and methods
    within this consolidated structure, providing namespace organization.
    """

    # ==============================================================================
    # NESTED CLASSES - CONFIGURATION AND UTILITIES
    # ==============================================================================

    class ResponseLike(TypedDict, total=False):
        """Type definition for response-like objects."""

        headers: dict[str, str]
        status_code: int

    class ErrorResponse(TypedDict):
        """Type definition for error response objects."""

        success: bool
        error: dict[str, object] | str
        data: None
        message: str | None
        timestamp: str | None

    class FlextApiAppConfig:
        """Configuration for FastAPI application."""

        def __init__(self, settings: FlextApiSettings | None = None) -> None:
            """Initialize application configuration."""
            if settings is None:
                # Use unwrap_or pattern for cleaner error handling without exceptions
                # Modern FlextResult pattern: unwrap_or_raise
                settings = FlextResult.unwrap_or_raise(
                    create_api_settings(), RuntimeError
                )

            self.settings = settings
            self.storage: FlextApiStorage | None = None

        def get_cors_origins(self) -> list[str]:
            """Get CORS origins from configuration."""
            if self.settings and self.settings.cors_origins:
                return self.settings.cors_origins

            # Default CORS origins for development - derive from core Platform constants
            try:
                platform_urls = getattr(FlextConstants.Platform, "ALLOWED_HOSTS", None)
                if isinstance(platform_urls, list):
                    # Cast to expected type and filter string items
                    urls_list = cast("list[object]", platform_urls)
                    typed_urls = [item for item in urls_list if isinstance(item, str)]
                    return typed_urls or ["http://localhost:3000"]
                return ["http://localhost:3000"]
            except (AttributeError, TypeError):
                return ["http://localhost:3000"]

        def get_version(self) -> str:
            """Get application version."""
            return (
                getattr(self.settings, "version", "0.9.0") if self.settings else "0.9.0"
            )

    class FlextApiHealthChecker:
        """Health check service implementing Strategy Pattern to reduce complexity."""

        def __init__(self, config: FlextApiApp.FlextApiAppConfig) -> None:
            """Initialize health checker with configuration."""
            self.config = config

        def _get_current_timestamp(self) -> str:
            """Get current UTC timestamp in ISO format (DRY pattern)."""
            return FlextUtilities.generate_iso_timestamp()

        def _build_base_health_data(self) -> dict[str, object]:
            """Build base health data structure."""
            return {
                "status": "healthy",
                "timestamp": self._get_current_timestamp(),
                "version": self.config.get_version(),
                "environment": self.config.settings.environment
                if self.config.settings
                else "unknown",
                "services": {
                    "api": {
                        "status": "healthy",
                        "port": self.config.settings.api_port
                        if self.config.settings
                        else 8000,
                        "host": self.config.settings.api_host
                        if self.config.settings
                        else "127.0.0.1",
                    },
                },
                "system": {
                    "python_version": sys.version.split()[0],
                    "platform": sys.platform,
                },
            }

        async def _check_storage_health(
            self,
            app: FastAPI,
            health_data: dict[str, object],
        ) -> None:
            """Check storage health and update health data."""
            if hasattr(app.state, "storage") and app.state.storage:
                try:
                    # Simple storage health check
                    storage_result = await app.state.storage.get("__health_check__")
                    services = cast(
                        "dict[str, object]", health_data.get("services", {})
                    )
                    services["storage"] = {
                        "status": "healthy" if storage_result.success else "degraded",
                        "backend": getattr(
                            app.state.storage._config, "backend", "unknown"
                        ),
                    }
                except Exception as e:
                    services = cast(
                        "dict[str, object]", health_data.get("services", {})
                    )
                    services["storage"] = {
                        "status": "unhealthy",
                        "error": str(e),
                    }

        async def get_health_status(self, app: FastAPI) -> dict[str, object]:
            """Get comprehensive health status."""
            health_data = self._build_base_health_data()
            await self._check_storage_health(app, health_data)
            return health_data

    # ==============================================================================
    # MAIN CONSOLIDATED CLASS IMPLEMENTATION
    # ==============================================================================

    def __init__(
        self, config: FlextApiAppConfig | None = None, **kwargs: object
    ) -> None:
        """Initialize FlextApiApp with configuration."""
        super().__init__(**kwargs)
        self._config = config or self.FlextApiAppConfig()
        self._health_checker = self.FlextApiHealthChecker(self._config)
        self._app_instance: FastAPI | None = None

    @override
    def execute(self) -> FlextResult[dict[str, object]]:
        """Execute the application service operation (required by FlextDomainService)."""
        return FlextResult[dict[str, object]].ok({
            "service": "FlextApiApp",
            "status": "ready",
            "version": self._config.get_version(),
            "environment": self._config.settings.environment
            if self._config.settings
            else "unknown",
            "app_created": self._app_instance is not None,
        })

    async def lifespan(self, app: FastAPI) -> AsyncGenerator[None]:
        """Application lifespan manager."""
        # Startup
        logger.info("Starting FLEXT API application")

        try:
            # Initialize storage
            app.state.storage = create_memory_storage(namespace="flext_api")
            logger.info("Storage initialized successfully")

            # Additional startup tasks can be added here

            yield

        finally:
            # Shutdown
            logger.info("Shutting down FLEXT API application")

            # Cleanup storage
            if hasattr(app.state, "storage") and app.state.storage:
                await app.state.storage.close()
                logger.info("Storage closed successfully")

    def create_fastapi_app(self, config: FlextApiAppConfig | None = None) -> FastAPI:
        """Create FastAPI application with all middleware and routes."""
        if config is None:
            config = self._config

        # Use the lifespan method directly since it's already an AsyncGenerator
        lifespan_func = self.lifespan

        # Create FastAPI app with lifespan
        app = FastAPI(
            title="FLEXT API",
            description="Enterprise-grade distributed data integration platform",
            version=config.get_version(),
            lifespan=lifespan_func,
            debug=config.settings.debug if config.settings else True,
        )

        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=config.get_cors_origins(),
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Add GZip middleware
        app.add_middleware(GZipMiddleware, minimum_size=1000)

        # Setup routes
        self._setup_health_endpoints(app)
        self._setup_error_handlers(app)

        self._app_instance = app
        return app

    def _setup_health_endpoints(self, app: FastAPI) -> None:
        """Setup health check endpoints."""

        @app.get("/health")
        async def health_endpoint() -> dict[str, object]:  # pyright: ignore[reportUnusedFunction]
            """Health check endpoint."""
            return await self._health_checker.get_health_status(app)

        @app.get("/health/ready")
        async def readiness_endpoint() -> dict[str, object]:  # pyright: ignore[reportUnusedFunction]
            """Readiness check endpoint."""
            return {
                "status": "ready",
                "timestamp": FlextUtilities.generate_iso_timestamp(),
            }

        @app.get("/health/live")
        async def liveness_endpoint() -> dict[str, object]:  # pyright: ignore[reportUnusedFunction]
            """Liveness check endpoint."""
            return {
                "status": "alive",
                "timestamp": FlextUtilities.generate_iso_timestamp(),
            }

    def _setup_error_handlers(self, app: FastAPI) -> None:
        """Setup global error handlers."""

        @app.exception_handler(FlextApiError)
        async def flext_api_error_handler(  # pyright: ignore[reportUnusedFunction]
            request: Request, exc: FlextApiError
        ) -> JSONResponse:
            """Handle FLEXT API errors."""
            logger.warning(f"API error: {exc}", extra={"path": request.url.path})
            error_response = create_error_response(exc, include_traceback=False)
            return JSONResponse(
                status_code=getattr(exc, "status_code", 500),
                content=error_response,
            )

        @app.exception_handler(Exception)
        async def generic_error_handler(  # pyright: ignore[reportUnusedFunction]
            request: Request, exc: Exception
        ) -> JSONResponse:
            """Handle unexpected errors."""
            error_id = FlextUtilities.generate_uuid()
            logger.error(
                f"Unexpected error [{error_id}]: {exc}",
                extra={"path": request.url.path, "error_id": error_id},
                exc_info=True,
            )
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": {
                        "code": "INTERNAL_SERVER_ERROR",
                        "message": "An unexpected error occurred",
                        "error_id": error_id,
                    },
                    "data": None,
                },
            )

    def run_development_server(
        self,
        host: str = "127.0.0.1",
        port: int | None = None,
        *,
        reload: bool = True,
        log_level: str = "info",
    ) -> None:
        """Run development server with hot reload."""
        if port is None:
            port = self._config.settings.api_port if self._config.settings else 8000

        app = self.create_fastapi_app()
        logger.info("Starting development server", host=host, port=port)

        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=reload,
            log_level=log_level,
        )

    def run_production_server(
        self,
        host: str = "127.0.0.1",
        port: int | None = None,
    ) -> None:
        """Run production server."""
        if port is None:
            port = self._config.settings.api_port if self._config.settings else 8000

        app = self.create_fastapi_app()
        logger.info("Starting production server", host=host, port=port)

        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="warning",
            access_log=False,
        )


# ==============================================================================
# CONVENIENCE ALIASES FOR BACKWARD COMPATIBILITY
# ==============================================================================

# Export consolidated class types for direct access
ResponseLike = FlextApiApp.ResponseLike
ErrorResponse = FlextApiApp.ErrorResponse
FlextApiAppConfig = FlextApiApp.FlextApiAppConfig
FlextApiHealthChecker = FlextApiApp.FlextApiHealthChecker

# ==============================================================================
# FACTORY FUNCTIONS - Delegate to FlextApiApp main class
# ==============================================================================


def create_flext_api_app_consolidated(
    config: FlextApiApp.FlextApiAppConfig | None = None,
) -> FlextApiApp:
    """Create FlextApiApp instance with configuration - consolidated class factory."""
    return FlextApiApp(config)


def create_flext_api_app(config: FlextApiAppConfig | None = None) -> FastAPI:
    """Create FastAPI application instance (legacy compatibility)."""
    app_instance = FlextApiApp(config)
    return app_instance.create_fastapi_app()


def create_flext_api_app_with_settings(**settings_overrides: object) -> FastAPI:
    """Create FastAPI app with settings overrides (legacy compatibility)."""
    # Create settings with overrides
    base_settings_result = create_api_settings(**settings_overrides)
    if not base_settings_result.success:
        # Fallback to empty config
        config = FlextApiAppConfig()
    else:
        base_settings = base_settings_result.value
        # Apply overrides to base settings (simplified for compatibility)
        config = FlextApiAppConfig(base_settings)

    app_instance = FlextApiApp(config)
    return app_instance.create_fastapi_app()


def run_development_server(
    host: str = "127.0.0.1",
    port: int | None = None,
    *,
    reload: bool = True,
    log_level: str = "info",
) -> None:
    """Run development server using FlextApiApp (legacy compatibility)."""
    app_instance = FlextApiApp()
    app_instance.run_development_server(
        host=host, port=port, reload=reload, log_level=log_level
    )


def run_production_server(
    host: str = "127.0.0.1",
    port: int | None = None,
) -> None:
    """Run production server using FlextApiApp (legacy compatibility)."""
    app_instance = FlextApiApp()
    app_instance.run_production_server(host=host, port=port)


# ==============================================================================
# MIDDLEWARE FUNCTIONS
# ==============================================================================


async def add_request_id_middleware(
    request: Request,
    call_next: Callable[[Request], object],
) -> JSONResponse | object:
    """Add request ID to all requests for tracing."""
    request_id = FlextUtilities.generate_uuid()

    # Add request ID to request state
    request.state.request_id = request_id

    # Process request - call_next is a callable per FastAPI contract
    maybe_response = call_next(request)
    if inspect.iscoroutine(maybe_response):
        response = cast("ResponseLike", await maybe_response)
    else:
        response = cast("ResponseLike", maybe_response)

    # Add request ID to response headers when available
    try:
        if hasattr(response, "headers"):
            headers = getattr(response, "headers", None)
            if headers and hasattr(headers, "__setitem__"):
                # Directly set the header on the original headers object
                headers["X-Request-ID"] = request_id
    except Exception as e:
        # For debugging - normally would suppress but let's see what's happening
        logger.debug(
            "Failed to add request ID to headers",
            error=str(e),
            response_type=type(response).__name__,
        )

    return response


async def error_handler_middleware(
    request: Request,
    call_next: Callable[[Request], object],
) -> JSONResponse | object:
    """Global error handler middleware."""
    try:
        # call_next is callable from FastAPI middleware contract
        maybe_response = call_next(request)
        if inspect.iscoroutine(maybe_response):
            return cast("JSONResponse", await maybe_response)
        return cast("JSONResponse", maybe_response)
    except FlextApiError as e:
        logger.exception(
            "API error occurred",
            request_id=getattr(request.state, "request_id", "unknown"),
            error=str(e),
            status_code=e.status_code,
        )

        error_response = cast(
            "ErrorResponse", create_error_response(e, include_traceback=False)
        )
        return JSONResponse(
            content=error_response,
            status_code=e.status_code,
            headers={"X-Error-Type": "FlextApiError"},
        )
    except Exception:
        request_id = getattr(request.state, "request_id", "unknown")
        logger.exception("Unexpected error occurred", request_id=request_id)

        unexpected_error_response: ErrorResponse = {
            "success": False,
            "error": "INTERNAL_SERVER_ERROR",
            "data": None,
            "message": "An unexpected error occurred",
            "timestamp": FlextUtilities.generate_iso_timestamp(),
        }

        return JSONResponse(
            content=unexpected_error_response,
            status_code=500,
            headers={"X-Error-Type": "UnexpectedError"},
        )


# ==============================================================================
# APPLICATION LIFESPAN MANAGEMENT
# ==============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Application lifespan manager."""
    # Startup
    logger.info("Starting FLEXT API application")

    try:
        # Initialize storage
        app.state.storage = create_memory_storage(namespace="flext_api")
        logger.info("Storage initialized successfully")

        # Additional startup tasks can be added here

        yield

    finally:
        # Shutdown
        logger.info("Shutting down FLEXT API application")

        # Cleanup storage
        if hasattr(app.state, "storage") and app.state.storage:
            await app.state.storage.close()
            logger.info("Storage closed successfully")


# ==============================================================================
# ENDPOINT HANDLERS
# ==============================================================================


def setup_health_endpoints(app: FastAPI, config: FlextApiAppConfig) -> None:
    """Set up health check and monitoring endpoints using Strategy Pattern.

    REFACTORED: Applied Strategy Pattern to reduce complexity from 31 to 3.
    Extracted FlextApiHealthChecker class following SOLID principles.
    """
    health_checker = FlextApiHealthChecker(config)

    @app.get("/health", tags=["Health"])
    async def health_check() -> dict[str, object]:  # pyright: ignore[reportUnusedFunction]
        """Comprehensive health check endpoint."""
        return await health_checker.get_health_status(app)

    @app.get("/health/live", tags=["Health"])
    async def liveness_check() -> dict[str, object]:  # pyright: ignore[reportUnusedFunction]
        """Liveness probe for Kubernetes."""
        return {"status": "healthy", "service": "flext-api"}  # Simple liveness check

    @app.get("/health/ready", tags=["Health"])
    async def readiness_check() -> dict[str, object]:  # pyright: ignore[reportUnusedFunction]
        """Readiness probe for Kubernetes."""
        return await health_checker.get_health_status(
            app
        )  # Use comprehensive health check for readiness


def setup_api_endpoints(app: FastAPI, config: FlextApiAppConfig) -> None:
    """Set up main API endpoints."""

    @app.get("/", tags=["Root"])
    async def root() -> dict[str, object]:  # pyright: ignore[reportUnusedFunction]
        """Root endpoint with API information."""
        return {
            "name": "FLEXT API",
            "description": "Enterprise-grade distributed data integration platform",
            "version": config.get_version(),
            "environment": config.settings.environment
            if config.settings
            else "unknown",
            "docs_url": "/docs",
            "health_url": "/health",
        }

    @app.get("/info", tags=["Info"])
    async def api_info() -> dict[str, object]:  # pyright: ignore[reportUnusedFunction]
        """Detailed API information."""
        return {
            "api": {
                "name": "FLEXT API",
                "version": config.get_version(),
                "description": "Enterprise-grade distributed data integration platform",
            },
            "environment": {
                "name": config.settings.environment if config.settings else "unknown",
                "debug": config.settings.debug if config.settings else False,
                "host": config.settings.api_host if config.settings else "127.0.0.1",
                "port": config.settings.api_port if config.settings else 8000,
            },
            "features": {
                "caching": config.settings.enable_caching if config.settings else False,
                "cache_ttl": config.settings.cache_ttl if config.settings else 300,
                "max_retries": config.settings.max_retries if config.settings else 3,
                "timeout": config.settings.default_timeout if config.settings else 30.0,
            },
        }


# ==============================================================================
# APPLICATION INSTANCES AND ENTRY POINTS
# ==============================================================================


# Create default app instance for ASGI servers and testing
try:
    # Allow tests to simulate initialization failure
    import os as _os  # local import to avoid polluting module namespace

    if _os.getenv("FLEXT_API_FORCE_APP_INIT_FAIL", "0") in {"1", "true", "yes"}:
        _forced_init_failure()

    app = create_flext_api_app()
    storage = create_memory_storage()

    # Export app and storage for external use
    __all__ = [
        "ErrorResponse",
        "FlextApiApp",
        "FlextApiAppConfig",
        "FlextApiHealthChecker",
        "ResponseLike",
        "app",
        "create_flext_api_app",
        "create_flext_api_app_consolidated",
        "create_flext_api_app_with_settings",
        "main",
        "run_development_server",
        "run_production_server",
        "storage",
    ]

except Exception as e:
    logger.exception("Failed to create default app instance", error=str(e))
    # Create a minimal app for error cases
    app = FastAPI(
        title="FLEXT API - Error",
        description="Failed to initialize properly",
    )
    # Create storage for error case to prevent import errors
    storage = create_memory_storage()
    error_message = str(e)

    @app.get("/error")
    async def error_info() -> dict[str, str]:
        return {"error": error_message, "status": "failed_to_initialize"}


# ==============================================================================
# CLI ENTRY POINT
# ==============================================================================


def main() -> None:
    """Run CLI entry point."""
    parser = argparse.ArgumentParser(description="FLEXT API Server")
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        help="Port to bind to (default: from settings)",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable hot reload for development",
    )
    parser.add_argument(
        "--production",
        action="store_true",
        help="Run in production mode",
    )
    parser.add_argument(
        "--log-level",
        default="info",
        choices=["debug", "info", "warning", "error"],
        help="Log level",
    )

    args = parser.parse_args()

    if args.production:
        run_production_server(host=args.host, port=args.port)
    else:
        run_development_server(
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level=args.log_level,
        )


# ==============================================================================
# EXPORTS
# ==============================================================================

__all__ = [
    "FlextApiApp",
    "FlextApiAppConfig",
    "FlextApiHealthChecker",
    "api_app",
    "app",
    "create_flext_api_app",
    "create_flext_api_app_consolidated",
    "create_flext_api_app_with_settings",
    "flext_api_create_app",
    "main",
    "run_development_server",
    "run_production_server",
    "setup_api_endpoints",
    "setup_health_endpoints",
    "storage",
]

# Legacy aliases for backward compatibility
flext_api_create_app = create_flext_api_app
api_app = app

if __name__ == "__main__":
    main()
