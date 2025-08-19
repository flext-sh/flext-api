"""FLEXT API FastAPI application.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import argparse
import datetime
import sys
import uuid
from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager, suppress as _suppress

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from flext_core import FlextConstants, get_logger

from flext_api.config import FlextApiSettings, create_api_settings
from flext_api.exceptions import FlextApiError, create_error_response
from flext_api.storage import FlextApiStorage, create_memory_storage

logger = get_logger(__name__)


# Internal helper to intentionally fail initialization for tests
def _forced_init_failure() -> None:
    raise RuntimeError


# ==============================================================================
# APPLICATION CONFIGURATION
# ==============================================================================


class FlextApiAppConfig:
    """Configuration for FastAPI application."""

    def __init__(self, settings: FlextApiSettings | None = None) -> None:
        """Initialize application configuration."""
        if settings is None:
            settings_result = create_api_settings()
            if not settings_result.success:
                msg = f"Failed to create settings: {settings_result.error}"
                raise RuntimeError(msg)
            settings = settings_result.data

        self.settings = settings
        self.storage: FlextApiStorage | None = None

    def get_cors_origins(self) -> list[str]:
        """Get CORS origins from configuration."""
        if self.settings and self.settings.cors_origins:
            return self.settings.cors_origins

        # Default CORS origins for development - derive from core Platform constants
        try:
            host = FlextConstants.Platform.DEFAULT_HOST
            return [
                f"http://{host}:{FlextConstants.Platform.FLEXT_WEB_PORT}",
                f"http://{host}:{FlextConstants.Platform.FLEXCORE_PORT}",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:8080",
                "http://127.0.0.1:4200",
            ]
        except Exception:
            return [
                "http://localhost:3000",
                "http://localhost:8080",
                "http://localhost:4200",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:8080",
                "http://127.0.0.1:4200",
            ]

    def get_title(self) -> str:
        """Get application title."""
        return "FLEXT API"

    def get_description(self) -> str:
        """Get application description."""
        return "Enterprise-grade distributed data integration platform"

    def get_version(self) -> str:
        """Get application version."""
        return "0.9.0"


# ==============================================================================
# MIDDLEWARE FUNCTIONS
# ==============================================================================


async def add_request_id_middleware(
    request: Request,
    call_next: Callable[[Request], object],
) -> JSONResponse | object:
    """Add request ID to all requests for tracing."""
    request_id = str(uuid.uuid4())

    # Add request ID to request state
    request.state.request_id = request_id

    # Process request - call_next is a callable per FastAPI contract
    maybe_response = call_next(request)
    response: object = (
        await maybe_response if hasattr(maybe_response, "__await__") else maybe_response
    )

    # Add request ID to response headers when available
    with _suppress(Exception):
        headers_obj = getattr(response, "headers", None)
        if headers_obj is not None:
            headers_obj["X-Request-ID"] = request_id

    return response


async def error_handler_middleware(
    request: Request,
    call_next: Callable[[Request], object],
) -> JSONResponse | object:
    """Global error handler middleware."""
    try:
        # call_next is callable from FastAPI middleware contract
        maybe_response = call_next(request)
        result: object = (
            await maybe_response
            if hasattr(maybe_response, "__await__")
            else maybe_response
        )
        return result
    except FlextApiError as e:
        logger.exception(
            "API error occurred",
            request_id=getattr(request.state, "request_id", "unknown"),
            error=str(e),
            status_code=e.status_code,
        )

        error_response = create_error_response(e, include_traceback=False)
        return JSONResponse(
            content=error_response,
            status_code=e.status_code,
            headers={"X-Error-Type": "FlextApiError"},
        )
    except Exception:
        request_id = getattr(request.state, "request_id", "unknown")
        logger.exception("Unexpected error occurred", request_id=request_id)

        error_response = {
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "status_code": 500,
                "context": {"request_id": request_id},
            },
            "data": None,
        }

        return JSONResponse(
            content=error_response,
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


class FlextApiHealthChecker:
    """Health check service implementing Strategy Pattern to reduce complexity.

    Refactored from setup_health_endpoints to follow SOLID principles:
    - Single Responsibility: Only handles health check logic
    - Open/Closed: Extensible with new health check strategies
    - Interface Segregation: Clean health check interface
    """

    def __init__(self, config: FlextApiAppConfig) -> None:
        """Initialize health checker with configuration."""
        self.config = config

    def _get_current_timestamp(self) -> str:
        """Get current UTC timestamp in ISO format (DRY pattern)."""
        return datetime.datetime.now(datetime.UTC).isoformat()

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
        storage_status: dict[str, object] = {
            "status": "healthy" if hasattr(app.state, "storage") else "unavailable",
            "type": "memory",
        }

        if hasattr(app.state, "storage") and app.state.storage:
            try:
                test_key = "health_check_test"
                set_coro = getattr(app.state.storage, "set", None)
                del_coro = getattr(app.state.storage, "delete", None)

                if set_coro and del_coro:
                    result_set = set_coro(
                        test_key,
                        {"timestamp": health_data["timestamp"]},
                    )
                    if hasattr(result_set, "__await__"):
                        await result_set
                    result_del = del_coro(test_key)
                    if hasattr(result_del, "__await__"):
                        await result_del
                storage_status["last_check"] = "successful"

            except Exception as e:
                logger.warning("Storage health check failed", error=str(e))
                storage_status.update({"status": "degraded", "error": str(e)})
                health_data["status"] = "degraded"

        services = health_data.get("services", {})
        if isinstance(services, dict):
            services["storage"] = storage_status
            health_data["services"] = services

    async def comprehensive_health_check(self, app: FastAPI) -> dict[str, object]:
        """Perform comprehensive health check with all strategies."""
        try:
            health_data = self._build_base_health_data()
            await self._check_storage_health(app, health_data)
            return health_data
        except Exception:
            logger.exception("Health check failed")
            return {}

    def liveness_check(self) -> dict[str, object]:
        """Liveness probe for Kubernetes - simple health indicator."""
        return {
            "status": "alive",
            "timestamp": self._get_current_timestamp(),
        }

    def readiness_check(self, app: FastAPI) -> dict[str, object]:
        """Readiness probe for Kubernetes - service dependency check."""
        is_ready = hasattr(app.state, "storage")
        return {
            "status": "ready" if is_ready else "not_ready",
            "timestamp": self._get_current_timestamp(),
            "services": {
                "storage": "ready" if is_ready else "not_ready",
            },
        }


def setup_health_endpoints(app: FastAPI, config: FlextApiAppConfig) -> None:
    """Set up health check and monitoring endpoints using Strategy Pattern.

    REFACTORED: Applied Strategy Pattern to reduce complexity from 31 to 3.
    Extracted FlextApiHealthChecker class following SOLID principles.
    """
    health_checker = FlextApiHealthChecker(config)

    @app.get("/health", tags=["Health"])
    async def health_check() -> dict[str, object]:  # pyright: ignore[reportUnusedFunction]
        """Comprehensive health check endpoint."""
        return await health_checker.comprehensive_health_check(app)

    @app.get("/health/live", tags=["Health"])
    async def liveness_check() -> dict[str, object]:  # pyright: ignore[reportUnusedFunction]
        """Liveness probe for Kubernetes."""
        return health_checker.liveness_check()

    @app.get("/health/ready", tags=["Health"])
    async def readiness_check() -> dict[str, object]:  # pyright: ignore[reportUnusedFunction]
        """Readiness probe for Kubernetes."""
        return health_checker.readiness_check(app)


def setup_api_endpoints(app: FastAPI, config: FlextApiAppConfig) -> None:
    """Set up main API endpoints."""

    @app.get("/", tags=["Root"])
    async def root() -> dict[str, object]:  # pyright: ignore[reportUnusedFunction]
        """Root endpoint with API information."""
        return {
            "name": config.get_title(),
            "description": config.get_description(),
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
                "name": config.get_title(),
                "version": config.get_version(),
                "description": config.get_description(),
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
# APPLICATION FACTORY
# ==============================================================================


def create_flext_api_app(config: FlextApiAppConfig | None = None) -> FastAPI:
    """Create and configure FastAPI application instance.

    Args:
      config: Optional application configuration

    Returns:
      Configured FastAPI application instance

    """
    if config is None:
        config = FlextApiAppConfig()

    # Create FastAPI app with lifespan management
    app = FastAPI(
        title=config.get_title(),
        description=config.get_description(),
        version=config.get_version(),
        lifespan=lifespan,
        # Always expose OpenAPI paths for tests; UI routes conditioned on debug
        docs_url="/docs" if config.settings and config.settings.debug else None,
        redoc_url="/redoc" if config.settings and config.settings.debug else None,
        openapi_url="/openapi.json",
    )

    # Use FastAPI's default route registration without additional wrappers to
    # preserve strict typing and avoid mypy mismatches.

    # Add middleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.get_cors_origins(),
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    # Add custom middleware
    app.middleware("http")(add_request_id_middleware)
    app.middleware("http")(error_handler_middleware)

    # Setup endpoints
    setup_health_endpoints(app, config)
    setup_api_endpoints(app, config)

    # Store config in app state for access in endpoints
    app.state.config = config

    logger.info(
        "FLEXT API application created successfully",
        title=config.get_title(),
        version=config.get_version(),
        environment=config.settings.environment if config.settings else "unknown",
    )

    return app


def create_flext_api_app_with_settings(**settings_overrides: object) -> FastAPI:
    """Create FastAPI app with custom settings.

    Args:
      **settings_overrides: Settings to override

    Returns:
      Configured FastAPI application instance

    """
    settings_result = create_api_settings(**settings_overrides)
    if not settings_result.success:
        msg = f"Failed to create settings: {settings_result.error}"
        raise RuntimeError(msg)

    config = FlextApiAppConfig(settings_result.data)
    return create_flext_api_app(config)


# ==============================================================================
# APPLICATION INSTANCES AND ENTRY POINTS
# ==============================================================================


def run_development_server(
    host: str = "127.0.0.1",  # Use localhost instead of binding to all interfaces
    port: int | None = None,
    *,
    reload: bool = True,
    log_level: str = "info",
) -> None:
    """Run development server with hot reload.

    Args:
      host: Host to bind to
      port: Port to bind to (defaults to settings)
      reload: Enable hot reload
      log_level: Logging level

    """
    # Create app for development
    app = create_flext_api_app()

    # Get port from settings if not specified
    if port is None:
        port = app.state.config.settings.api_port if app.state.config.settings else 8000

    logger.info("Starting development server", host=host, port=port, reload=reload)

    uvicorn.run(
        "flext_api.api_app:create_flext_api_app",
        host=host,
        port=port or 8000,
        reload=reload,
        log_level=log_level,
        factory=True,
    )


def run_production_server(
    host: str | None = None,
    port: int | None = None,
) -> None:
    """Run production server.

    Args:
      host: Host to bind to (defaults to settings)
      port: Port to bind to (defaults to settings)

    """
    # Create app for production
    settings_result = create_api_settings()
    if not settings_result.success:
        msg = f"Failed to create settings: {settings_result.error}"
        raise RuntimeError(msg)

    settings = settings_result.data

    # Use settings defaults if not specified
    if host is None:
        host = settings.api_host if settings else "127.0.0.1"
    if port is None:
        port = settings.api_port if settings else 8000

    app = create_flext_api_app_with_settings(api_host=host, api_port=port, debug=False)

    logger.info("Starting production server", host=host, port=port)

    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="warning",
        access_log=False,
    )


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
        "app",
        "create_flext_api_app",
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
    # storage is already defined above, just assign None
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


# Create default app instance for testing and legacy compatibility
app = create_flext_api_app()

if __name__ == "__main__":
    main()
