"""FLEXT API - Service using flext-core structural patterns.

Uses FlextService for proper service architecture and dependency injection.
Follows FLEXT-core patterns for maximum code reduction and alignment.
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
            await self._client.stop()
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
