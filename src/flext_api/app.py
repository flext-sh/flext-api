"""FLEXT API Application Factory - FastAPI application creation with server integration.

Provides backward-compatible FastAPI application creation with enhanced server support.
Integrates with FlextApiServer for protocol handlers, middleware, and webhooks.

See TRANSFORMATION_PLAN.md - Phase 6 for implementation details.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from fastapi import FastAPI
from flext_core import FlextLogger, FlextResult, FlextService, FlextTypes

from flext_api.models import FlextApiModels
from flext_api.server import FlextApiServer
from flext_api.webhook import FlextWebhookHandler


class FlextApiApp(FlextService[object]):
    """FastAPI application factory with flext-core integration.

    Integrated with flext-core:
    - Extends FlextService for application lifecycle management
    - Uses FlextContext for request context management (future enhancement)
    - Uses FlextLogger for structured logging

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
    def create_fastapi_app(config: FlextApiModels.AppConfig) -> object:
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

            def health_check() -> FlextTypes.StringDict:
                return {"status": "healthy", "service": "flext-api"}

            # Use add_api_route instead of decorator to avoid type issues
            add_route = getattr(app, "add_api_route")
            add_route("/health", health_check, methods=["GET"])
            logger.info("Health check endpoint registered at /health")

        logger.info("FastAPI application created successfully")

        return app

    @staticmethod
    def create_server(
        host: str = "localhost",
        port: int = 8000,
        title: str = "Flext API Server",
        version: str = "1.0.0",
    ) -> FlextResult[object]:
        """Create FlextApiServer instance with protocol handler support.

        This is the enhanced server creation method that supports
        protocol handlers, middleware, and webhook integration.

        Args:
            host: Server host address
            port: Server port
            title: API server title
            version: API server version

        Returns:
            FlextResult containing FlextApiServer instance or error

        """
        try:
            server = FlextApiServer(
                host=host,
                port=port,
                title=title,
                version=version,
            )

            return FlextResult[object].ok(server)

        except ImportError as e:
            return FlextResult[object].fail(f"Failed to import FlextApiServer: {e}")
        except Exception as e:
            return FlextResult[object].fail(f"Failed to create server: {e}")

    @staticmethod
    def create_webhook_handler(
        secret: str | None = None,
        max_retries: int = 3,
    ) -> FlextResult[object]:
        """Create FlextWebhookHandler instance.

        Args:
            secret: Webhook signing secret
            max_retries: Maximum retry attempts

        Returns:
            FlextResult containing FlextWebhookHandler instance or error

        """
        try:
            handler = FlextWebhookHandler(
                secret=secret,
                max_retries=max_retries,
            )

            return FlextResult[object].ok(handler)

        except ImportError as e:
            return FlextResult[object].fail(
                f"Failed to import FlextWebhookHandler: {e}"
            )
        except Exception as e:
            return FlextResult[object].fail(f"Failed to create webhook handler: {e}")


__all__ = ["FlextApiApp"]
