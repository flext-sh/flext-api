"""Main FlextApi service class for HTTP operations.

Core service class that extends FlextApiBaseService and composes HTTP client
and builder functionality through composition patterns. Provides factory methods
for HTTP client creation with configuration validation.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TypedDict, cast, override

from flext_core import FlextDomainService, FlextLogger, FlextResult, get_flext_container
from pydantic import Field

from flext_api.client import FlextApiBuilder, FlextApiClient, FlextApiClientConfig
from flext_api.models import DEFAULT_MAX_RETRIES, DEFAULT_TIMEOUT, ClientConfig
from flext_api.protocols import (
    FlextApiHttpClientProtocol,
    FlextApiQueryBuilderProtocol,
    FlextApiResponseBuilderProtocol,
)

logger = FlextLogger(__name__)


class ClientConfigDict(TypedDict, total=False):
    """Type definition for client configuration dictionary."""

    base_url: str
    timeout: float | int
    headers: dict[str, str]
    max_retries: int


__version__ = "0.9.0"


class FlextApi(FlextDomainService[dict[str, object]]):
    """Unified API service using flext-core patterns.

    Extends FlextDomainService to provide HTTP client and builder functionality
    through composition. Follows SOLID principles with proper separation of concerns.
    """

    service_name: str = Field(default="FlextApi", description="Service name")
    service_version: str = Field(default=__version__, description="Service version")
    # Composition of services
    _builder: FlextApiBuilder | None = None
    _client: FlextApiHttpClientProtocol | None = None
    _client_config: ClientConfig | None = None

    def __init__(self, **_data: object) -> None:
        """Initialize FlextApi service with builder and dependency injection."""
        # Initialize base class without extra data (base class forbids extra fields)
        super().__init__()

        # Dependency injection following FLEXT-core patterns
        self._container = get_flext_container()

        # Register services in container
        self._container.register("flext_api", self)
        self._container.register_factory("api_builder", FlextApiBuilder)

        # Initialize composed services
        self._builder = FlextApiBuilder()
        self._is_running = False

        logger.info("FlextApi service initialized", version=self.service_version)

    @override
    def execute(self) -> FlextResult[dict[str, object]]:
        """Execute the domain service operation (required by FlextDomainService)."""
        return FlextResult[dict[str, object]].ok({
            "status": "ready",
            "service": "FlextApi",
            "version": self.service_version,
        })

    def start(self) -> FlextResult[None]:
        """Start the service."""
        logger.info("Starting service", service_type=type(self).__name__)
        self._is_running = True
        return FlextResult[None].ok(None)

    def stop(self) -> FlextResult[None]:
        """Stop the service."""
        logger.info("Stopping service", service_type=type(self).__name__)
        self._is_running = False
        return FlextResult[None].ok(None)

    def health_check(self) -> FlextResult[dict[str, object]]:
        """Perform health check."""
        return FlextResult[dict[str, object]].ok({
            "status": "healthy" if self._is_running else "stopped",
            "service": type(self).__name__,
            "is_running": self._is_running,
            "client_configured": self._client is not None,
            "builder_available": self._builder is not None,
        })

    @property
    def is_running(self) -> bool:
        """Check if service is running."""
        return self._is_running

    # Async service variants
    async def start_async(self) -> FlextResult[None]:
        """Start the FlextApi service (async interface)."""
        result = self.start()
        if result.success:
            logger.debug("FlextApi service startup complete")
        return result

    async def stop_async(self) -> FlextResult[None]:
        """Stop the FlextApi service (async interface)."""
        try:
            # Close client if exists
            if self._client:
                await self._client.close()
                self._client = None
            logger.debug("FlextApi service shutdown complete")
            return self.stop()
        except Exception as e:
            logger.exception("Error during service shutdown")
            return FlextResult[None].fail(f"Shutdown error: {e}")

    async def health_check_async(self) -> FlextResult[dict[str, object]]:
        """Health check with async details."""
        base_result = self.health_check()
        if not base_result.success:
            return base_result

        # Service is already providing comprehensive health details
        return base_result

    # Compatibility: allow calling health_check in sync contexts within tests
    def sync_health_check(self) -> FlextResult[dict[str, object]]:
        """Run health check synchronously for compatibility tests."""
        return self.health_check()

    def health_check_sync(self) -> FlextResult[dict[str, object]]:
        """Synchronous wrapper for health_check for legacy tests."""
        return self.sync_health_check()

    def create_client(
        self,
        config: ClientConfigDict | None = None,
    ) -> FlextResult[FlextApiHttpClientProtocol]:
        """Create HTTP client with configuration using modern FlextCallable patterns.

        Args:
            config: Client configuration dictionary with:
                - base_url: Required string, must start with http:// or https://
                - timeout: Optional float, defaults to 30.0 seconds
                - headers: Optional dict of string key-value pairs
                - max_retries: Optional int, defaults to 3
        Returns:
            FlextResult[FlextApiHttpClientProtocol]: Success with client or failure with error

        """

        # Railway-oriented programming pattern (FLEXT-core proven pattern)
        def create_config(config_dict: dict[str, object]) -> FlextResult[ClientConfig]:
            """Create and validate client configuration."""
            try:
                timeout_value = config_dict.get("timeout") or DEFAULT_TIMEOUT
                timeout: float = (
                    float(timeout_value) if timeout_value else DEFAULT_TIMEOUT
                )

                headers_value = config_dict.get("headers") or {}
                headers: dict[str, str] = cast("dict[str, str]", headers_value)

                retries_value = config_dict.get("max_retries") or DEFAULT_MAX_RETRIES
                max_retries: int = (
                    int(retries_value) if retries_value else DEFAULT_MAX_RETRIES
                )

                client_config = ClientConfig(
                    base_url=str(config_dict.get("base_url", "")),
                    timeout=timeout,
                    headers=headers,
                    max_retries=max_retries,
                )
                return FlextResult[ClientConfig].ok(client_config)
            except Exception as e:
                return FlextResult[ClientConfig].fail(
                    f"Configuration creation failed: {e}"
                )

        def validate_config(client_config: ClientConfig) -> FlextResult[ClientConfig]:
            """Validate configuration using business rules."""
            validation_result = client_config.validate_business_rules()
            if not validation_result:
                return FlextResult[ClientConfig].fail(
                    validation_result.error or "Invalid client configuration"
                )
            return FlextResult[ClientConfig].ok(client_config)

        def create_client(
            client_config: ClientConfig,
        ) -> FlextResult[FlextApiHttpClientProtocol]:
            """Create API client from validated configuration."""
            try:
                legacy_config = FlextApiClientConfig(
                    base_url=client_config.base_url,
                    timeout=client_config.timeout,
                    headers=client_config.headers,
                    max_retries=client_config.max_retries,
                )

                api_client = FlextApiClient(legacy_config)
                self._client = cast("FlextApiHttpClientProtocol", api_client)
                self._client_config = client_config
                logger.info("HTTP client created", base_url=client_config.base_url)

                return FlextResult[FlextApiHttpClientProtocol].ok(
                    cast("FlextApiHttpClientProtocol", api_client)
                )
            except Exception as e:
                logger.exception("Client creation failed")
                return FlextResult[FlextApiHttpClientProtocol].fail(
                    f"Client creation error: {e}"
                )

        # Railway-oriented composition (MANDATORY pattern)
        config_dict = cast("dict[str, object]", config or {})
        return (
            create_config(config_dict)
            .flat_map(validate_config)  # Chain validation
            .flat_map(create_client)  # Chain client creation
            .tap_error(
                lambda e: logger.error(f"HTTP client setup failed: {e}")
            )  # Log errors
        )

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
        # FlextApiQueryBuilder implements FlextApiQueryBuilderProtocol
        return cast("FlextApiQueryBuilderProtocol", self.get_builder().for_query())

    def get_response_builder(self) -> FlextApiResponseBuilderProtocol:
        """Get response builder for constructing API responses.

        Returns:
            Response builder instance

        """
        # FlextApiResponseBuilder implements FlextApiResponseBuilderProtocol
        return cast(
            "FlextApiResponseBuilderProtocol",
            self.get_builder().for_response(),
        )

    def get_client(self) -> FlextApiHttpClientProtocol | None:
        """Get current client instance.

        Returns:
            Current client instance or None if not configured

        """
        return self._client

    @override
    def get_service_info(self) -> dict[str, object]:
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

    def _create_client_impl(
        self,
        config: ClientConfigDict | None = None,
    ) -> FlextResult[FlextApiClient]:
        """Create internal client for testing and edge cases.

        Args:
            config: Client configuration dictionary
        Returns:
            FlextResult containing FlextApiClient instance

        """
        try:
            config_dict = config or {}
            # Type-safe extraction using TypedDict structure
            base_url = str(config_dict.get("base_url", ""))
            if not base_url:
                return FlextResult[FlextApiClient].fail(
                    "Invalid URL format: base_url cannot be empty"
                )

            timeout: float = config_dict.get("timeout") or DEFAULT_TIMEOUT
            max_retries: int = config_dict.get("max_retries") or DEFAULT_MAX_RETRIES
            headers: dict[str, str] = config_dict.get("headers") or {}
            # Create ClientConfig and validate
            client_config = ClientConfig(
                base_url=base_url,
                timeout=timeout,
                headers=headers,
                max_retries=max_retries,
            )
            # Validate configuration - use modern FlextResult pattern
            validation_result = client_config.validate_business_rules()
            if not validation_result:  # FlextResult has __bool__ support
                return FlextResult[FlextApiClient].fail(
                    validation_result.error or "Invalid URL format"
                )
            # Convert to legacy config format
            legacy_config = FlextApiClientConfig(
                base_url=client_config.base_url,
                timeout=client_config.timeout,
                headers=client_config.headers,
                max_retries=client_config.max_retries,
            )
            client = FlextApiClient(legacy_config)
            return FlextResult[FlextApiClient].ok(client)
        except Exception as e:
            logger.exception("Failed to create client implementation", error=str(e))
            return FlextResult[FlextApiClient].fail(f"Client creation failed: {e}")


def create_flext_api(**config: object) -> FlextApi:
    """Create FlextApi service instance.

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
