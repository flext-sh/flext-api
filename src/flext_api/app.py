"""FLEXT API Application Factory - FastAPI application creation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_api.models import FlextApiModels


# Internal abstraction - FastAPI is imported at runtime only
def _create_fastapi_instance(
    title: str | None = None,
    version: str | None = None,
    description: str | None = None,
    docs_url: str | None = None,
    redoc_url: str | None = None,
    openapi_url: str | None = None,
) -> object:
    """Internal FastAPI instance creation with runtime import.

    Args:
        title: Application title
        version: Application version
        description: Application description
        docs_url: Documentation URL
        redoc_url: ReDoc URL
        openapi_url: OpenAPI JSON URL

    Returns:
        FastAPI application instance.

    Raises:
        ImportError: If FastAPI is not installed.

    """
    # Import FastAPI only at runtime to avoid direct import exposure
    try:
        from fastapi import FastAPI

        return FastAPI(
            title=title or "FlextAPI",
            version=version or "1.0.0",
            description=description or "FlextAPI Application",
            docs_url=docs_url or "/docs",
            redoc_url=redoc_url or "/redoc",
            openapi_url=openapi_url or "/openapi.json",
        )
    except ImportError as e:
        error_msg = "FastAPI is required for FlextAPI application creation"
        raise ImportError(error_msg) from e


class FlextApiApp:
    """FLEXT API Application Factory - FastAPI application creation following FLEXT architecture."""

    @staticmethod
    def create_fastapi_app(config: FlextApiModels.AppConfig) -> object:
        """Create a FastAPI application with the given configuration.

        Args:
            config: Application configuration

        Returns:
            FastAPI application instance

        """
        app = _create_fastapi_instance(
            title=config.title,
            version=config.app_version,
            description=getattr(config, "description", "FlextAPI Application"),
            docs_url=getattr(config, "docs_url", "/docs"),
            redoc_url=getattr(config, "redoc_url", "/redoc"),
            openapi_url=getattr(config, "openapi_url", "/openapi.json"),
        )

        # Add health endpoint
        if hasattr(app, "get"):

            @app.get("/health")
            def health_check() -> dict[str, str]:  # pyright: ignore[reportUnusedFunction]
                return {"status": "healthy", "service": "flext-api"}

        return app


# Direct class access only - no backward compatibility aliases

__all__ = ["FlextApiApp"]
