"""App-related test factories using simple factory functions.

Provides factory functions for FastAPI app configurations.
"""

from __future__ import annotations

from fastapi import FastAPI

from flext_api import FlextApiAppConfig


def create_flext_api_app_config(
    settings: object | None = None,
) -> FlextApiAppConfig:
    """Create FlextApiAppConfig for testing."""
    return FlextApiAppConfig(settings=settings)  # type: ignore[arg-type] # Testing purpose


def create_fastapi_application(
    title: str = "Test FLEXT API",
    description: str = "Test API Description",
    version: str = "0.1.0",
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
FlextApiAppConfigFactory = create_flext_api_app_config
FastAPIApplicationFactory = create_fastapi_application
