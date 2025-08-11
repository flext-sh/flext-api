"""Main FlextApi service class for HTTP operations.

Core service class that extends FlextApiBaseService and composes HTTP client
and builder functionality through composition patterns. Provides factory methods
for HTTP client creation with configuration validation.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core import FlextResult, FlextTypes, get_logger
from pydantic import Field

if TYPE_CHECKING:
    from flext_api.api_protocols import (
        FlextApiClientProtocol,
        FlextApiQueryBuilderProtocol,
        FlextApiResponseBuilderProtocol,
    )

from flext_api.api_client import FlextApiBuilder, FlextApiClient, FlextApiClientConfig
from flext_api.api_models import ClientConfig
from flext_api.base_service import FlextApiBaseService

logger = get_logger(__name__)

# Import version from package
try:
    from flext_api import __version__ as _version
except ImportError:
    _version = "0.9.0"


class FlextApi(FlextApiBaseService):
    """Unified API service using flext-core patterns.

    Extends FlextApiBaseService to provide HTTP client and builder functionality
    through composition. Follows SOLID principles with proper separation of concerns.
    """

    service_name: str = Field(default="FlextApi", description="Service name")
    service_version: str = Field(default=_version, description="Service version")

    # Composition of services
    _builder: FlextApiBuilder | None = None
    _client: FlextApiClientProtocol | None = None
    _client_config: ClientConfig | None = None

    def __init__(self, **data: object) -> None:
        """Initialize FlextApi service with builder."""
        super().__init__(**data)
        self._builder = FlextApiBuilder()
        logger.info("FlextApi service initialized", version=self.service_version)

    async def _do_start(self) -> FlextResult[None]:
        """Perform service-specific startup logic."""
        logger.debug("FlextApi service startup complete")
        return FlextResult.ok(None)

    async def _do_stop(self) -> FlextResult[None]:
        """Perform service-specific shutdown logic."""
        try:
            # Close client if exists
            if self._client:
                await self._client.close()
                self._client = None

            logger.debug("FlextApi service shutdown complete")
            return FlextResult.ok(None)
        except Exception as e:
            logger.exception("Error during service shutdown")
            return FlextResult.fail(f"Shutdown error: {e}")

    async def _get_health_details(self) -> FlextResult[FlextTypes.Core.JsonDict]:
        """Get service-specific health details."""
        details: FlextTypes.Core.JsonDict = {
            "client_configured": self._client is not None,
            "client_type": type(self._client).__name__ if self._client else None,
            "builder_available": self._builder is not None,
        }

        if self._client_config:
            details["client_base_url"] = self._client_config.base_url
            details["client_timeout"] = self._client_config.timeout

        return FlextResult.ok(details)

    def create_client(
        self,
        config: FlextTypes.Core.JsonDict | None = None,
    ) -> FlextResult[FlextApiClientProtocol]:
        """Create HTTP client with configuration using FlextResult pattern.

        Args:
            config: Client configuration dictionary with:
                - base_url: Required string, must start with http:// or https://
                - timeout: Optional float, defaults to 30.0 seconds
                - headers: Optional dict of string key-value pairs
                - max_retries: Optional int, defaults to 3

        Returns:
            FlextResult containing configured client or error

        """
        try:
            # Create ClientConfig value object
            config_dict = config or {}
            client_config = ClientConfig(
                base_url=str(config_dict.get("base_url", "")),
                timeout=float(config_dict.get("timeout", 30.0)),
                headers=dict(config_dict.get("headers", {})),
                max_retries=int(config_dict.get("max_retries", 3)),
            )

            # Validate configuration
            validation_result = client_config.validate_business_rules()
            if not validation_result.success:
                return FlextResult.fail(validation_result.error or "Invalid client configuration")

            # Convert to legacy config format for backward compatibility
            legacy_config = FlextApiClientConfig(
                base_url=client_config.base_url,
                timeout=client_config.timeout,
                headers=client_config.headers,
                max_retries=client_config.max_retries,
            )

            # Create client
            self._client = FlextApiClient(legacy_config)
            self._client_config = client_config

            logger.info("HTTP client created", base_url=client_config.base_url)
            return FlextResult.ok(self._client)

        except Exception as e:
            logger.exception("Failed to create client")
            return FlextResult.fail(f"Failed to create client: {e}")

    def get_builder(self) -> FlextApiBuilder:
        """Get builder instance for advanced operations.

        Returns:
            FlextApiBuilder instance for query/response construction

        """
        if not self._builder:
            self._builder = FlextApiBuilder()
        return self._builder

    def get_query_builder(self) -> FlextApiQueryBuilderProtocol:
        """Get query builder for constructing API queries.

        Returns:
            Query builder instance

        """
        return self.get_builder().for_query()

    def get_response_builder(self) -> FlextApiResponseBuilderProtocol:
        """Get response builder for constructing API responses.

        Returns:
            Response builder instance

        """
        return self.get_builder().for_response()

    def get_client(self) -> FlextApiClientProtocol | None:
        """Get current client instance.

        Returns:
            Current client instance or None if not configured

        """
        return self._client

    def get_service_info(self) -> FlextTypes.Core.JsonDict:
        """Get detailed service information.

        Returns:
            Dictionary with service details

        """
        return {
            "name": self.service_name,
            "version": self.service_version,
            "is_running": self.is_running,
            "client_configured": self._client is not None,
            "client_type": type(self._client).__name__ if self._client else None,
            "builder_available": self._builder is not None,
        }

    def _create_client_impl(self, config: FlextTypes.Core.JsonDict | None = None) -> FlextApiClient:
        """Internal client creation method for testing and edge cases.

        Args:
            config: Client configuration dictionary

        Returns:
            FlextApiClient instance

        Raises:
            ValueError: If configuration is invalid

        """
        config_dict = config or {}

        # Handle invalid types gracefully with defaults
        base_url = str(config_dict.get("base_url", ""))
        if not base_url:
            raise ValueError("Invalid URL format")

        try:
            timeout = float(config_dict.get("timeout", 30.0))
        except (ValueError, TypeError):
            timeout = 30.0

        try:
            max_retries = int(float(config_dict.get("max_retries", 3)))
        except (ValueError, TypeError):
            max_retries = 3

        headers = config_dict.get("headers", {})
        if not isinstance(headers, dict):
            headers = {}

        # Create ClientConfig and validate
        client_config = ClientConfig(
            base_url=base_url,
            timeout=timeout,
            headers=headers,
            max_retries=max_retries,
        )

        # Validate configuration
        validation_result = client_config.validate_business_rules()
        if not validation_result.success:
            raise ValueError(validation_result.error or "Invalid URL format")

        # Convert to legacy config format
        legacy_config = FlextApiClientConfig(
            base_url=client_config.base_url,
            timeout=client_config.timeout,
            headers=client_config.headers,
            max_retries=client_config.max_retries,
        )

        return FlextApiClient(legacy_config)

    # Legacy compatibility methods
    def flext_api_create_client(
        self,
        config: FlextTypes.Core.JsonDict | None = None,
    ) -> FlextResult[FlextApiClient]:
        """Legacy method for creating HTTP client.

        DEPRECATED: Use create_client() instead.

        Args:
            config: Client configuration dictionary

        Returns:
            FlextResult containing client or error

        """
        logger.warning("Using deprecated method flext_api_create_client")
        result = self.create_client(config)
        if result.success and isinstance(result.data, FlextApiClient):
            return FlextResult.ok(result.data)
        # Wrap error message to match test expectations
        error_msg = result.error or "Unknown error"
        return FlextResult.fail(f"Failed to create client: {error_msg}")


def create_flext_api(**config: object) -> FlextApi:
    """Factory function to create FlextApi service instance.

    Args:
        **config: Optional configuration parameters

    Returns:
        Configured FlextApi service instance

    """
    return FlextApi(**config)


# Legacy compatibility
def create_api_service() -> FlextApi:
    """Legacy factory function.

    DEPRECATED: Use create_flext_api() instead.

    Returns:
        FlextApi service instance

    """
    logger.warning("Using deprecated function create_api_service")
    return create_flext_api()


# ==============================================================================
# EXPORTS
# ==============================================================================

__all__ = [
    "FlextApi",
    "create_api_service",  # Legacy
    "create_flext_api",
]
