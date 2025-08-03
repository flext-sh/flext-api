"""Main FlextApi service class for HTTP operations.

Core service class that composes HTTP client and builder functionality through
composition patterns. Provides factory methods for HTTP client creation with
configuration validation.

Actual Implementation:
    - HTTP client factory with dictionary-based configuration
    - Query/response builder access through get_builder()
    - Basic service lifecycle with async start()/stop() methods
    - Health check returning service status dictionary
    - Composition of FlextApiClient and FlextApiBuilder instances

Current Architecture:
    FlextApi (composition root)
    ├── FlextApiClient (HTTP operations)
    └── FlextApiBuilder (query/response building)

Key Methods:
    - flext_api_create_client(config): Create HTTP client with config dict
    - get_builder(): Access builder instance for query construction
    - get_client(): Access current client instance or None
    - start()/stop(): Async service lifecycle methods
    - health_check(): Return service health status

Configuration Support:
    - base_url: Required string, must start with http:// or https://
    - timeout: Optional float, defaults to 30.0 seconds
    - headers: Optional dict of string key-value pairs
    - max_retries: Optional int, defaults to 3

Error Handling:
    - flext_api_create_client() returns FlextResult[FlextApiClient]
    - ValueError exceptions for invalid base_url (lines 199, 202)
    - Configuration type conversion with safe defaults

Known Issues:
    - Uses structlog directly instead of flext_core.get_logger()
    - Raises exceptions instead of returning FlextResult consistently
    - Does not inherit from FlextService base class
    - Limited plugin architecture integration

"""

from __future__ import annotations

import structlog
from flext_core import FlextResult

from flext_api import __version__
from flext_api.builder import FlextApiBuilder
from flext_api.client import FlextApiClient, FlextApiClientConfig

logger = structlog.get_logger(__name__)


class FlextApi:
    """Unified API service using flext-core patterns.

    Provides HTTP client and builder functionality through composition.
    Uses flext-core structural patterns for consistency and code reduction.
    """

    def __init__(self) -> None:
        """Initialize FlextApi service."""
        self._builder = FlextApiBuilder()
        self._client: FlextApiClient | None = None
        logger.info("FlextApi service initialized")

    async def start(self) -> FlextResult[None]:
        """Start the service."""
        logger.info("FlextApi service started")
        return FlextResult.ok(None)

    async def stop(self) -> FlextResult[None]:
        """Stop the service."""
        if self._client:
            await self._client.stop()  # Async method
        logger.info("FlextApi service stopped")
        return FlextResult.ok(None)

    def health_check(self) -> FlextResult[dict[str, object]]:
        """Health check."""
        health_data = {
            "service": "FlextApi",
            "status": "healthy",
            "client_configured": self._client is not None,
        }
        return FlextResult.ok(health_data)

    def get_service_info(self) -> dict[str, object]:
        """Get service information."""
        return {
            "name": "FlextApi",
            "service": "FlextApi",
            "version": __version__,
            "client_configured": self._client is not None,
            "client_type": type(self._client).__name__ if self._client else None,
        }

    def flext_api_create_client(
        self,
        config: dict[str, object] | None = None,
    ) -> FlextResult[FlextApiClient]:
        """Create HTTP client with configuration using FlextResult pattern."""
        try:
            return FlextResult.ok(self._create_client_impl(config or {}))
        except (RuntimeError, ValueError, TypeError) as e:
            logger.exception("Failed to create client")
            return FlextResult.fail(f"Failed to create client: {e}")

    def _create_client_impl(self, config: dict[str, object]) -> FlextApiClient:
        """Create client implementation with configuration."""
        # Convert config to appropriate types for dataclass
        base_url = str(config.get("base_url", ""))

        # Validate base_url is required for client creation
        if not base_url:
            msg = "base_url is required"
            raise ValueError(msg)
        if not base_url.startswith(("http://", "https://")):
            msg = "Invalid URL format"
            raise ValueError(msg)

        timeout_val = config.get("timeout", 30.0)
        timeout = float(timeout_val) if isinstance(timeout_val, (int, float)) else 30.0
        headers = None
        if "headers" in config and isinstance(config["headers"], dict):
            headers = {str(k): str(v) for k, v in config["headers"].items()}
        max_retries_val = config.get("max_retries", 3)
        max_retries = (
            int(max_retries_val) if isinstance(max_retries_val, (int, float)) else 3
        )

        client_config = FlextApiClientConfig(
            base_url=base_url,
            timeout=timeout,
            headers=headers,
            max_retries=max_retries,
        )
        self._client = FlextApiClient(client_config)
        return self._client

    def get_builder(self) -> FlextApiBuilder:
        """Get builder instance for advanced operations."""
        return self._builder

    def get_client(self) -> FlextApiClient | None:
        """Get current client instance."""
        return self._client


def create_flext_api() -> FlextApi:
    """Create FlextApi service instance."""
    return FlextApi()
