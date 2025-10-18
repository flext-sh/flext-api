"""Generic FastAPI Application Factory - HTTP application creation.

Provides generic FastAPI application creation with server integration.
Domain-agnostic and reusable across any HTTP application.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from fastapi import FastAPI
from flext_core import FlextLogger, FlextResult, FlextService

from flext_api.config import FlextWebConfig


class FlextApiApp(FlextService[object]):
    """Generic FastAPI application factory.

    Integrated with flext-core for application lifecycle management.
    Domain-agnostic and reusable across any HTTP application.

    Follows FLEXT pattern: one class per module with nested subclasses.
    """

    def execute(self, *_args: object, **_kwargs: object) -> FlextResult[object]:
        """Execute app service lifecycle operations.

        FlextService requires this method for service execution.
        For app factory, this is a no-op as app creation is static method-based.

        Returns:
            FlextResult[object]: Success result

        """
        return FlextResult[object].ok(None)

    class _Factory:
        """Nested factory for FastAPI instance creation."""

        @staticmethod
        def create_instance(
            title: str | None = None,
            version: str | None = None,
            description: str | None = None,
            docs_url: str | None = None,
            redoc_url: str | None = None,
            openapi_url: str | None = None,
        ) -> object:
            """Internal FastAPI instance creation.

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

    @staticmethod
    def create_fastapi_app(config: FlextWebConfig) -> object:
        """Create a FastAPI application with flext-core integration.

        Args:
            config: Application configuration

        Returns:
            FastAPI application instance with flext-core services integrated

        """
        # Initialize flext-core services for application
        logger = FlextLogger(__name__)
        # NOTE: FlextContext will be used for request context
        # management in future enhancement
        # NOTE: FlextBus is a CQRS command/query bus, not an event emitter

        logger.info(
            "Creating FastAPI application",
            title=config.title,
            version=config.app_version,
        )

        app = FlextApiApp._Factory.create_instance(
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
            logger.info("Health check endpoint registered at /health")

        logger.info("FastAPI application created successfully")

        return app


__all__ = ["FlextApiApp"]
