"""FastAPI application factory following SOLID principles.

Generic HTTP application creation using flext-core patterns.
Single responsibility: FastAPI application instantiation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from fastapi import FastAPI

from flext_api import FlextApiSettings, t


class FlextApiApp:
    """FastAPI application factory following SOLID principles.

    Single responsibility: FastAPI application creation.
    Uses flext-core patterns for configuration and error handling.
    """

    @staticmethod
    def create(
        config: FlextApiSettings,
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
        config: Application configuration
        title: Application title
        version: Application version
        description: Application description
        docs_url: Documentation URL
        redoc_url: ReDoc URL
        openapi_url: OpenAPI JSON URL

        Returns:
        FastAPI application instance.

        """
        app = FastAPI(
            title=title or "FlextAPI",
            version=version or "1.0.0",
            description=description or "FlextAPI Application",
            docs_url=docs_url or "/docs",
            redoc_url=redoc_url or "/redoc",
            openapi_url=openapi_url or "/openapi.json",
        )
        app.state.flext_api_settings = config
        return app


__all__: t.MutableSequenceOf[str] = ["FlextApiApp"]
