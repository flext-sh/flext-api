"""FLEXT API Application Factory - FastAPI application creation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from fastapi import FastAPI

from flext_api.models import FlextApiModels


def create_fastapi_app(config: FlextApiModels.AppConfig) -> object:
    """Create a FastAPI application with the given configuration.

    Args:
        config: Application configuration

    Returns:
        FastAPI application instance

    """
    app = FastAPI(
        title=config.title,
        version=config.app_version,
        description=getattr(config, "description", "FlextAPI Application"),
        docs_url=getattr(config, "docs_url", "/docs"),
        redoc_url=getattr(config, "redoc_url", "/redoc"),
        openapi_url=getattr(config, "openapi_url", "/openapi.json"),
    )

    # Add health endpoint
    @app.get("/health")
    async def health_check() -> dict[str, str]:
        return {"status": "healthy", "service": "flext-api"}

    return app


__all__ = ["create_fastapi_app"]
