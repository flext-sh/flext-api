"""Generic Server Factory - HTTP server creation.

Provides generic HTTP server creation with protocol handler support.
Domain-agnostic and reusable across any HTTP server implementation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_core import FlextResult

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
    ) -> FlextResult[object]:
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

        Single responsibility: create webhook handler instances.
        Delegates error handling to railway pattern.

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


__all__ = ["FlextApiServerFactory"]
