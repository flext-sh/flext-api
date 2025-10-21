"""FastAPI application factory following SOLID principles.

Generic HTTP application creation using flext-core patterns.
Single responsibility: FastAPI application instantiation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from fastapi import FastAPI

from flext_api.config import FlextApiConfig


class FlextApiApp:
    """FastAPI application factory following SOLID principles.

    Single responsibility: FastAPI application creation.
    Uses flext-core patterns for configuration and error handling.
    """

    @staticmethod
    def create(
        _config: FlextApiConfig,
        *,
        title: str | None = None,
        version: str | None = None,
        description: str | None = None,
        docs_url: str | None = None,
        redoc_url: str | None = None,
        openapi_url: str | None = None,
    ) -> FastAPI:
        """Create FastAPI application with flext-core integration.

        Args:
        _config: Application configuration
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


__all__ = ["FlextApiApp"]
