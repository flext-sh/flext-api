"""FLEXT API FastAPI application factory."""

from __future__ import annotations

from fastapi import FastAPI

from flext_api.api import create_flext_api


def flext_api_create_app() -> FastAPI:
    """Create and configure FastAPI application instance."""
    # Create FlextApi service instance
    flext_api = create_flext_api()

    # Create FastAPI app
    app = FastAPI(
        title="FLEXT API",
        description="Enterprise-grade distributed data integration platform",
        version="1.0.0",
    )

    # Health check endpoint
    @app.get("/health")
    async def health_check() -> dict[str, object]:
        """Health check endpoint."""
        result = flext_api.health_check()
        return result.data if result.data is not None else {}

    return app
