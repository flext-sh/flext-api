"""FLEXT API - Main API class implementation.

Real API functionality with FlextResult patterns.
Factory functions and main API class.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextResult, flext_logger

from flext_api.client import FlextApiClient
from flext_api.models import FlextApiModels
from flext_api.storage import FlextApiStorage

logger = flext_logger(__name__)


class FlextApi:
    """Main FLEXT API class."""

    def __init__(self) -> None:
        """Initialize FLEXT API."""
        self._clients: dict[str, FlextApiClient] = {}
        self._storages: dict[str, FlextApiStorage] = {}
        self._current_client: FlextApiClient | None = None
        self._current_builder: FlextApiModels.Builder | None = None

    @property
    def service_version(self) -> str:
        """Get service version."""
        return "0.9.0"

    @property
    def default_base_url(self) -> str:
        """Get default base URL."""
        return "https://api.flext.io"

    def create_client(self, config: dict[str, object]) -> FlextResult[FlextApiClient]:
        """Create HTTP client with configuration."""
        try:
            client_config = FlextApiModels.ClientConfig(**config)
            client = FlextApiClient(client_config)
            self._current_client = client
            return FlextResult.ok(client)
        except Exception as e:
            logger.exception("Failed to create client", config=config, error=str(e))
            return FlextResult.fail(f"Failed to create client: {e}")

    def get_client(self) -> FlextApiClient | None:
        """Get current client instance."""
        return self._current_client

    def get_builder(self) -> FlextApiModels.Builder:
        """Get current builder instance."""
        if self._current_builder is None:
            self._current_builder = FlextApiModels.Builder()
        return self._current_builder

    def create_storage(self, config: dict[str, object]) -> FlextResult[FlextApiStorage]:
        """Create storage backend with configuration."""
        try:
            storage = FlextApiStorage(config)
            return FlextResult.ok(storage)
        except Exception as e:
            logger.exception("Failed to create storage", config=config, error=str(e))
            return FlextResult.fail(f"Failed to create storage: {e}")


def create_flext_api() -> FlextApi:
    """Factory function to create FLEXT API instance."""
    return FlextApi()


def create_client(config: dict[str, object]) -> FlextResult[FlextApiClient]:
    """Factory function to create HTTP client directly."""
    api = create_flext_api()
    return api.create_client(config)


__all__ = ["FlextApi", "create_flext_api", "create_client"]
