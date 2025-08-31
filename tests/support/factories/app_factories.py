"""App-related test factories using simple factory functions.

Provides factory functions for FastAPI app configurations.
"""

from __future__ import annotations

from fastapi import FastAPI

from flext_api import FlextApiApp
from flext_api.config import FlextApiConfig


def create_flext_api_app_config(
    settings: object | None = None,
) -> FlextApiApp:
    """Create FlextApiApp for testing."""
    if settings is None:
        return FlextApiApp(settings=None)
    if isinstance(settings, FlextApiConfig):
        return FlextApiApp(settings=settings)
    return FlextApiApp(settings=None)  # Fallback for object type


def create_fastapi_application(
    title: str = "Test FLEXT API",
    description: str = "Test API Description",
    version: str = "0.1.0",
    *,
    debug: bool = True,
    docs_url: str = "/docs",
    redoc_url: str = "/redoc",
    openapi_url: str = "/openapi.json",
) -> FastAPI:
    """Create FastAPI application for testing."""
    return FastAPI(
        title=title,
        description=description,
        version=version,
        debug=debug,
        docs_url=docs_url,
        redoc_url=redoc_url,
        openapi_url=openapi_url,
    )


# Legacy aliases for backwards compatibility
FlextApiConfigFactory = create_flext_api_app_config
FastAPIApplicationFactory = create_fastapi_application
