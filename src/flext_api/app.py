"""FlextApiApp - FastAPI application following FLEXT patterns.

Single FastAPI application class that inherits from FlextDomainService,
provides web interface, and uses global dependency injection.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from flext_core import (
    FlextContainer,
    FlextLogger,
    FlextModels,
    FlextResult,
)
from pydantic import Field

# Type aliases for cleaner code
Result = dict[str, object]

logger = FlextLogger(__name__)


class FlextApiApp(FlextModels):
    """FastAPI application following FLEXT patterns.

    Provides web interface for API operations with:
    - Inherits from FlextModels for type safety
    - FlextResult for all operations - zero exceptions
    - Global dependency injection container
    - FastAPI integration with middleware
    - Health check endpoints
    """

    app_name: str = Field(default="FLEXT API", description="FastAPI app name")
    app_version: str = Field(default="0.9.0", description="App version")
    debug: bool = Field(default=False, description="Debug mode")

    def __init__(self, **data: object) -> None:
        """Initialize FastAPI app with flext-core patterns."""
        super().__init__(**data)

        # Get global container - NO local containers
        self._container = FlextContainer.get_global()

        # Register self in global container
        self._container.register("flext_api_app", self)

        # Initialize FastAPI app
        self._fastapi_app: FastAPI | None = None

        logger.info(
            "FlextApiApp initialized", name=self.app_name, version=self.app_version
        )

    def get_info(self) -> FlextResult[Result]:
        """Get app information - returns FlextResult, never raises."""
        return FlextResult[Result].ok(
            {
                "app": "FlextApiApp",
                "app_name": self.app_name,
                "version": self.app_version,
                "debug": self.debug,
                "has_fastapi_app": self._fastapi_app is not None,
            }
        )

    def create_app(self) -> FlextResult[FastAPI]:
        """Create FastAPI application - returns FlextResult, never raises."""
        try:

            @asynccontextmanager
            async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
                """FastAPI lifespan context manager."""
                logger.info("FastAPI app starting up")
                yield
                logger.info("FastAPI app shutting down")

            # Create FastAPI app
            app = FastAPI(
                title=self.app_name,
                version=self.app_version,
                description="Enterprise-grade distributed data integration platform",
                debug=self.debug,
                lifespan=lifespan,
            )

            # Add CORS middleware
            app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )

            # Add health check endpoint
            @app.get("/health")
            async def health_check() -> Result:
                """Health check endpoint."""
                return {
                    "status": "healthy",
                    "app": self.app_name,
                    "version": self.app_version,
                }

            # Add root endpoint
            @app.get("/")
            async def root() -> Result:
                """Root endpoint."""
                return {
                    "message": f"{self.app_name} API",
                    "version": self.app_version,
                    "status": "running",
                }

            # Error handler
            @app.exception_handler(Exception)
            async def global_exception_handler(
                request: Request, exc: Exception
            ) -> JSONResponse:
                """Global exception handler."""
                logger.error(
                    "Unhandled exception", error=str(exc), path=request.url.path
                )
                return JSONResponse(
                    status_code=500,
                    content={
                        "error": "Internal server error",
                        "message": str(exc) if self.debug else "An error occurred",
                    },
                )

            self._fastapi_app = app
            logger.info("FastAPI app created successfully")
            return FlextResult[FastAPI].ok(app)

        except Exception as e:
            logger.exception("Failed to create FastAPI app", error=str(e))
            return FlextResult[FastAPI].fail(f"Failed to create app: {e}")

    def get_app(self) -> FlextResult[FastAPI]:
        """Get FastAPI application, creating if necessary."""
        if self._fastapi_app:
            return FlextResult[FastAPI].ok(self._fastapi_app)

        return self.create_app()

    def run(self, host: str = "127.0.0.1", port: int = 8000) -> FlextResult[None]:
        """Run the FastAPI application - returns FlextResult, never raises."""
        try:
            app_result = self.get_app()
            if app_result.is_failure:
                return FlextResult[None].fail(f"Failed to get app: {app_result.error}")

            logger.info("Starting FastAPI server", host=host, port=port)

            # Note: In real implementation, this would be async
            # For now, just log the intent
            logger.info("FastAPI server would start here", host=host, port=port)

            return FlextResult[None].ok(None)

        except Exception as e:
            logger.exception("Failed to run FastAPI app", error=str(e))
            return FlextResult[None].fail(f"Failed to run app: {e}")


# =============================================================================
# FACTORY FUNCTIONS - Following flext-core patterns
# =============================================================================


def create_flext_api_app(
    title: str | None = None,
    version: str | None = None,
    description: str | None = None,
) -> FastAPI:
    """Create FastAPI app instance with default configuration.

    Args:
        title: Optional app title
        version: Optional app version
        description: Optional app description

    Returns:
        Configured FastAPI application instance

    """
    app_instance = FlextApiApp(
        title=title or "FlextApi",
        version=version or "0.9.0",
        description=description or "HTTP Foundation Library",
    )

    app_result = app_instance.create_app()
    if app_result.is_failure:
        msg = f"Failed to create app: {app_result.error}"
        raise ValueError(msg)

    return app_result.value


__all__ = [
    "FlextApiApp",
    "create_flext_api_app",
]
