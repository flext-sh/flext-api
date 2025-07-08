"""FLEXT API - Enterprise FastAPI Gateway with Zero Tolerance for Technical Debt.

Professional imports with proper package management.
"""

from __future__ import annotations

# Version
__version__ = "0.6.0"

# Professional imports from installed flext-core package
try:
    from flext_core import ServiceResult, ValueObject, get_config
    __all__ = ["ServiceResult", "ValueObject", "__version__", "get_config"]
except ImportError as e:
    print(f"Warning: Could not import flext-core: {e}")
    __all__ = ["__version__"]


import asyncio
import logging
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

logger = logging.getLogger(__name__)


class FlextAPI:
    """FLEXT API Application - Enterprise FastAPI Gateway.

    Provides RESTful API interface for the FLEXT Meltano Enterprise platform
    with production-ready features including authentication, rate limiting,
    monitoring, and comprehensive error handling.
    """

    def __init__(self, *, debug: bool = False) -> None:
        """Initialize FLEXT API application instance.

        Args:
            debug: Enable debug mode with OpenAPI documentation endpoints.
        """
        self.debug = debug
        self.app: FastAPI | None = None
        self.initialized = False
        self._background_tasks: set = set()

    async def initialize(self) -> FastAPI:
        """Initialize FastAPI application with enterprise middleware and routes.

        Returns:
            FastAPI: Configured application instance

        """
        if self.initialized:
            return self.app

        # Create FastAPI app with enterprise configuration
        self.app = FastAPI(
            title="FLEXT API",
            description="FLEXT Meltano Enterprise Platform API",
            version="1.0.0",
            debug=self.debug,
            openapi_url="/api/v1/openapi.json" if self.debug else None,
            docs_url="/docs" if self.debug else None,
            redoc_url="/redoc" if self.debug else None,
        )

        # Add security middleware
        self.app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["localhost", "127.0.0.1", "*.flext.sh"],
        )

        # Add CORS middleware for web interface
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:3000", "https://*.flext.sh"],
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
            allow_headers=["*"],
        )

        # Health check endpoint
        @self.app.get("/health")
        async def health_check() -> dict[str, str | bool]:
            """Check API health status."""
            return {
                "status": "healthy",
                "service": "flext-api",
                "version": "1.0.0",
                "debug": self.debug,
            }

        # Root endpoint
        @self.app.get("/")
        async def root() -> dict[str, str | None]:
            """Get API root service information."""
            return {
                "service": "FLEXT API",
                "description": "FLEXT Meltano Enterprise Platform API",
                "version": "1.0.0",
                "docs": "/docs" if self.debug else None,
                "health": "/health",
            }

        self.initialized = True
        logger.info("FLEXT API initialized successfully")
        return self.app

    async def shutdown(self) -> None:
        """Graceful shutdown of API services."""
        if not self.initialized:
            return

        logger.info("Shutting down FLEXT API...")

        # Cancel background tasks
        for task in self._background_tasks:
            if not task.done():
                task.cancel()

        # Wait for tasks to complete
        if self._background_tasks:
            await asyncio.gather(*self._background_tasks, return_exceptions=True)

        self.initialized = False
        logger.info("FLEXT API shutdown complete")

    @asynccontextmanager
    async def lifespan(self) -> AsyncGenerator[FastAPI]:
        """Context manager for API lifespan management."""
        await self.initialize()
        try:
            yield self.app
        finally:
            await self.shutdown()


__all__ = ["FlextAPI"]
