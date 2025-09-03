"""FlextApi - Main API class following FLEXT patterns.

Single API class that orchestrates HTTP operations and provides factory methods
for client creation. Uses flext-core patterns with FlextResult.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import cast

from flext_core import FlextContainer, FlextDomainService, FlextLogger, FlextResult
from pydantic import Field

from flext_api.client import FlextApiClient
from flext_api.models import FlextApiModels
from flext_api.typings import FlextApiTypes

# Type aliases for cleaner code
ClientConfigDict = FlextApiTypes.Client.ClientConfigDict
Result = dict[str, object]

logger = FlextLogger(__name__)


class FlextApi(FlextDomainService):
    """Main API class providing HTTP client and builder functionality.

    Single class following FLEXT patterns with FlextResult for all operations.
    Provides HTTP client creation, builder patterns, and service lifecycle.
    """

    # Pydantic fields
    service_name: str = Field(default="FlextApi", description="Service name")
    service_version: str = Field(default="0.9.0", description="Service version")
    default_base_url: str = Field(
        default="http://localhost:8000", description="Default base URL"
    )

    def __init__(self, **kwargs: object) -> None:
        """Initialize API with flext-core patterns."""
        # Ensure service_name defaults to "FlextApi" for compatibility
        kwargs.setdefault("service_name", "FlextApi")
        super().__init__(**kwargs)

        # Internal state
        self._is_running = False
        self._client: FlextApiClient | None = None
        self._builder: FlextApiModels | None = None

        # Get global container - NO local containers ever
        self._container = FlextContainer.get_global()

        # Register self in global container
        self._container.register("flext_api", self)

        logger.info("FlextApi initialized", version=self.service_version)

    def execute(self) -> FlextResult[dict[str, object]]:
        """Execute API service lifecycle."""
        try:
            service_info: dict[str, object] = {
                "service_name": self.service_name,
                "service_version": self.service_version,
                "default_base_url": self.default_base_url,
                "status": "active",
            }
            logger.info(
                "FlextApi service executed successfully", service_info=service_info
            )
            return FlextResult[dict[str, object]].ok(service_info)
        except Exception as e:
            logger.exception("Failed to execute FlextApi service")
            return FlextResult[dict[str, object]].fail(f"Service execution failed: {e}")

    def get_info(self) -> FlextResult[Result]:
        """Get API service information - returns FlextResult, never raises."""
        try:
            info_data = {
                "service": "FlextApi",
                "name": self.service_name,
                "version": self.service_version,
                "base_url": self.default_base_url,
                "running": self._is_running,
                "has_client": self._client is not None,
            }
            return FlextResult[Result].ok(info_data)
        except Exception as e:
            logger.exception("Failed to get API info", error=str(e))
            return FlextResult[Result].fail(f"Failed to get info: {e}")

    def get_client(self) -> FlextApiClient | None:
        """Get current HTTP client instance."""
        return self._client

    def get_builder(self) -> FlextApiModels:
        """Get builder instance for queries and responses."""
        if self._builder is None:
            self._builder = FlextApiModels()
        return self._builder

    def create_client(
        self, config: ClientConfigDict | None = None
    ) -> FlextResult[FlextApiClient]:
        """Create HTTP client with configuration - returns FlextResult, never raises."""
        try:
            # Validate config
            if config is None:
                return FlextResult[FlextApiClient].fail("base_url is required")

            if not config.get("base_url"):
                return FlextResult[FlextApiClient].fail("base_url is required")

            # Type-safe client initialization with proper field types
            self._client = FlextApiClient(
                base_url=cast("str", config["base_url"]),
                timeout=cast("float", config.get("timeout", 30.0)),
                headers=cast("dict[str, str]", config.get("headers", {})),
                max_retries=cast("int", config.get("max_retries", 3)),
            )

            logger.info("HTTP client created", base_url=self._client.base_url)
            return FlextResult[FlextApiClient].ok(self._client)

        except Exception as e:
            logger.exception("Failed to create HTTP client", error=str(e))
            return FlextResult[FlextApiClient].fail(
                f"Failed to create HTTP client: {e}"
            )

    async def start_async(self) -> FlextResult[None]:
        """Start the API service asynchronously."""
        try:
            self._is_running = True
            logger.info("FlextApi started", service=self.service_name)
            return FlextResult[None].ok(None)
        except Exception as e:
            logger.exception("Failed to start API", error=str(e))
            return FlextResult[None].fail(f"Failed to start: {e}")

    async def stop_async(self) -> FlextResult[None]:
        """Stop the API service asynchronously."""
        try:
            self._is_running = False
            if self._client:
                await self._client.stop()
                self._client = None
            logger.info("FlextApi stopped", service=self.service_name)
            return FlextResult[None].ok(None)
        except Exception as e:
            logger.exception("Failed to stop API", error=str(e))
            return FlextResult[None].fail(f"Failed to stop: {e}")

    async def health_check_async(self) -> FlextResult[Result]:
        """Perform async health check."""
        try:
            health_data: dict[str, object] = {
                "status": "healthy" if self._is_running else "stopped",
                "service": self.service_name,
                "version": self.service_version,
                "has_client": self._client is not None,
                "default_base_url": self.default_base_url,
            }
            return FlextResult[Result].ok(health_data)
        except Exception as e:
            logger.exception("Health check failed", error=str(e))
            return FlextResult[Result].fail(f"Health check failed: {e}")

    # =========================================================================
    # FACTORY METHODS - Following flext-core patterns
    # =========================================================================

    @staticmethod
    def create_instance(
        service_name: str | None = None,
        service_version: str | None = None,
        default_base_url: str | None = None,
    ) -> FlextApi:
        """Create FlextApi instance with optional configuration.

        Args:
            service_name: Optional service name
            service_version: Optional service version
            default_base_url: Optional default base URL

        Returns:
            Configured FlextApi instance

        """
        return FlextApi(
            service_name=service_name or "FlextApi",
            service_version=service_version or "0.9.0",
            default_base_url=default_base_url or "http://localhost:8000",
        )


__all__ = [
    "FlextApi",
]
