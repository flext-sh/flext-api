"""FLEXT API Client Module.

Compatibility module that bridges to api_client.py functionality.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

# Import specific exports from api_client for compatibility
from flext_api.api_client import (
    FlextApiBuilder,
    FlextApiClient,
    FlextApiClientConfig,
    FlextApiClientRequest,
    FlextApiClientResponse,
    FlextApiClientStatus,
    FlextApiPlugin,
    FlextApiQueryBuilder,
    FlextApiResponseBuilder,
    create_client,
)

# Add any missing compatibility classes
try:
    from flext_api.api_client import FlextApiClientMethod
except ImportError:
    # Create compatibility enum if missing
    from enum import StrEnum

    class FlextApiClientMethod(StrEnum):
        """HTTP methods for API client."""

        GET = "GET"
        POST = "POST"
        PUT = "PUT"
        PATCH = "PATCH"
        DELETE = "DELETE"
        HEAD = "HEAD"
        OPTIONS = "OPTIONS"

# Add missing factory functions
def create_client_with_plugins(config=None, plugins=None):
    """Create client with plugins support."""
    # Handle None config - use empty base_url for test compatibility
    if config is None:
        config = {"base_url": ""}

    # If config is already a FlextApiClientConfig, use it directly
    if hasattr(config, "base_url"):
        client = FlextApiClient(config, plugins)
    else:
        client = create_client(config)
        if plugins:
            client.plugins.extend(plugins)

    return client

# Re-export all for compatibility
__all__ = [
    "FlextApiBuilder",
    "FlextApiClient",
    "FlextApiClientConfig",
    "FlextApiClientMethod",
    "FlextApiClientRequest",
    "FlextApiClientResponse",
    "FlextApiClientStatus",
    "FlextApiPlugin",
    "FlextApiQueryBuilder",
    "FlextApiResponseBuilder",
    "create_client",
    "create_client_with_plugins",
]
