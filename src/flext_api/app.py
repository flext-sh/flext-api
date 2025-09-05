"""FLEXT API App - FastAPI application implementation.

Real FastAPI application with FlextResult patterns.
Production-ready HTTP server implementation.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from fastapi import FastAPI
from flext_core import flext_logger

logger = flext_logger(__name__)


class FlextApiApp:
    """FastAPI application wrapper for FLEXT API."""

    def __init__(self) -> None:
        """Initialize FastAPI application."""
        self.app = FastAPI(
            title="FLEXT API",
            description="FLEXT HTTP Foundation Library",
            version="0.9.0",
        )
        self._setup_routes()

    def _setup_routes(self) -> None:
        """Setup API routes."""

        @self.app.get("/health")
        async def health_check() -> dict[str, str]:
            """Health check endpoint."""
            return {"status": "healthy", "service": "flext-api"}

        @self.app.get("/")
        async def root() -> dict[str, str]:
            """Root endpoint."""
            return {"message": "FLEXT API is running"}

    def get_app(self) -> FastAPI:
        """Get the FastAPI application instance."""
        return self.app


def create_flext_app() -> FlextApiApp:
    """Factory function to create FLEXT API app instance."""
    return FlextApiApp()


def create_flext_api_app(_config: object = None) -> FastAPI:
    """Factory function to create FastAPI app instance directly."""
    # Note: config parameter reserved for future configuration options
    app_wrapper = FlextApiApp()
    return app_wrapper.get_app()


__all__ = ["FlextApiApp", "create_flext_api_app", "create_flext_app"]
