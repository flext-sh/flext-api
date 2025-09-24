"""FLEXT API Application Factory - FastAPI application creation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from fastapi import FastAPI

from flext_api.models import FlextApiModels
from flext_core import FlextService


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
    # FastAPI is already imported at module level

    try:
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


class FlextApiApp(FlextService[object]):
    """Single unified API app class following FLEXT standards.

    Contains all FastAPI application creation and management functionality.
    Follows FLEXT pattern: one class per module with nested subclasses.
    """

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

        if hasattr(app, "get") and hasattr(app, "add_api_route"):

            def health_check() -> dict[str, str]:
                return {"status": "healthy", "service": "flext-api"}

            # Use add_api_route instead of decorator to avoid type issues
            add_route = getattr(app, "add_api_route")
            add_route("/health", health_check, methods=["GET"])

        return app


__all__ = ["FlextApiApp"]
