"""Generic Server Factory - HTTP server creation.

Provides generic HTTP server creation with protocol handler support.
Domain-agnostic and reusable across any HTTP server implementation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext import r
from flext_api.server import FlextApiServer
from flext_api.webhook import FlextWebhookHandler


class FlextApiServerFactory:
    """Generic HTTP server factory with single responsibility.

    Delegates to specialized services for server and webhook creation.
    Follows SOLID principles with clear separation of concerns.
    """

    @staticmethod
    def create_server(
        host: str = "localhost",
        port: int = 8000,
        title: str = "Flext API Server",
        version: str = "1.0.0",
    ) -> r[object]:
        """Create FlextApiServer instance with protocol handler support.

        Single responsibility: create server instances.
        Delegates error handling to railway pattern.

        Args:
        host: Server host address
        port: Server port
        title: API server title
        version: API server version

        Returns:
        FlextResult containing FlextApiServer instance or error

        """
        server = FlextApiServer(
            host=host,
            port=port,
            title=title,
            version=version,
        )
        return r[object].ok(server)

    @staticmethod
    def create_webhook_handler(
        secret: str | None = None,
        max_retries: int = 3,
    ) -> r[object]:
        """Create FlextWebhookHandler instance.

        Single responsibility: create webhook handler instances.
        Delegates error handling to railway pattern.

        Args:
        secret: Webhook signing secret
        max_retries: Maximum retry attempts

        Returns:
        FlextResult containing FlextWebhookHandler instance or error

        """
        handler = FlextWebhookHandler(
            secret=secret,
            max_retries=max_retries,
        )
        return r[object].ok(handler)


__all__ = ["FlextApiServerFactory"]
