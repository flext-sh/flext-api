"""Main FlextApi service class for HTTP operations.

Core service class that extends FlextApiBaseService and composes HTTP client
and builder functionality through composition patterns. Provides factory methods
for HTTP client creation with configuration validation.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import asyncio as _asyncio
from threading import Thread
from typing import TypedDict, cast, override

from flext_core import FlextResult, FlextResult as _Res, get_logger
from pydantic import Field

from flext_api.base_service import (
    FlextApiBaseService,
    FlextApiBaseService as _Base,
)
from flext_api.client import FlextApiBuilder, FlextApiClient, FlextApiClientConfig
from flext_api.models import DEFAULT_MAX_RETRIES, DEFAULT_TIMEOUT, ClientConfig
from flext_api.protocols import (
    FlextApiHttpClientProtocol,
    FlextApiQueryBuilderProtocol,
    FlextApiResponseBuilderProtocol,
)
from flext_api.typings import FlextTypes

logger = get_logger(__name__)


class ClientConfigDict(TypedDict, total=False):
    """Type definition for client configuration dictionary."""

    base_url: str
    timeout: float | int
    headers: dict[str, str]
    max_retries: int


__version__ = "0.9.0"


class FlextApi(FlextApiBaseService):
    """Unified API service using flext-core patterns.

    Extends FlextApiBaseService to provide HTTP client and builder functionality
    through composition. Follows SOLID principles with proper separation of concerns.
    """

    service_name: str = Field(default="FlextApi", description="Service name")
    service_version: str = Field(default=__version__, description="Service version")
    # Composition of services
    _builder: FlextApiBuilder | None = None
    _client: FlextApiHttpClientProtocol | None = None
    _client_config: ClientConfig | None = None

    def __init__(self, **_data: object) -> None:
        """Initialize FlextApi service with builder."""
        # Initialize base class without extra data (base class forbids extra fields)
        super().__init__()
        self._builder = FlextApiBuilder()
        logger.info("FlextApi service initialized", version=self.service_version)

    @override
    async def _do_start(self) -> FlextResult[None]:
        """Perform service-specific startup logic."""
        logger.debug("FlextApi service startup complete")
        return FlextResult[None].ok(None)

    @override
    async def _do_stop(self) -> FlextResult[None]:
        """Perform service-specific shutdown logic."""
        try:
            # Close client if exists
            if self._client:
                await self._client.close()
                self._client = None
            logger.debug("FlextApi service shutdown complete")
            return FlextResult[None].ok(None)
        except Exception as e:
            logger.exception("Error during service shutdown")
            return FlextResult[None].fail(f"Shutdown error: {e}")

    @override
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
        return FlextResult[FlextTypes.Core.JsonDict].ok(details)

    # Use inherited sync methods from base class and add async variants
    async def start_async(self) -> FlextResult[None]:
        """Start the FlextApi service (async interface)."""
        result = super().start()
        if result.success:
            return await self._do_start()
        return result

    async def stop_async(self) -> FlextResult[None]:
        """Stop the FlextApi service (async interface)."""
        shutdown_result = await self._do_stop()
        if shutdown_result.success:
            return super().stop()
        return shutdown_result

    async def health_check_async(self) -> FlextResult[dict[str, object]]:
        """Health check with async details."""
        base_result = super().health_check()
        if not base_result.success:
            return base_result

        # Add service-specific health details
        details_result = await self._get_health_details()
        if details_result.success:
            health_data = base_result.value
            health_data.update(details_result.value)
            return FlextResult[dict[str, object]].ok(health_data)
        return base_result

    # Compatibility: allow calling health_check in sync contexts within tests
    def sync_health_check(self) -> FlextResult[dict[str, object]]:
        """Run health check synchronously for compatibility tests.

        Always uses a private event loop to avoid interfering with pytest's loop.
        """
        # If a loop is already running (pytest-asyncio), run the coroutine in a
        # separate thread with its own event loop to avoid nested-loop errors.
        try:
            _asyncio.get_running_loop()
            result_holder: list[_Res[dict[str, object]]] = []
            error_holder: list[BaseException] = []

            def _runner() -> None:
                loop_inner = _asyncio.new_event_loop()
                try:
                    res = _Base.health_check(self)
                    result_holder.append(res)
                except BaseException as exc:  # pragma: no cover - defensive
                    error_holder.append(exc)
                finally:
                    loop_inner.close()

            t = Thread(target=_runner, daemon=True)
            t.start()
            t.join()
            if result_holder:
                return result_holder[0]
            if error_holder:
                return FlextResult[dict[str, object]].fail(
                    f"Failed to run health check: {error_holder[0]}"
                )
            return FlextResult[dict[str, object]].fail(
                "Failed to run health check: unknown error"
            )
        except RuntimeError:
            loop = _asyncio.new_event_loop()
            try:
                return _Base.health_check(self)
            finally:
                loop.close()

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
        try:
            config_dict = config or {}

            # Type-safe extraction using TypedDict structure
            timeout: float = config_dict.get("timeout") or DEFAULT_TIMEOUT
            headers: dict[str, str] = config_dict.get("headers") or {}
            max_retries: int = config_dict.get("max_retries") or DEFAULT_MAX_RETRIES

            # Create and validate configuration
            client_config = ClientConfig(
                base_url=str(config_dict.get("base_url", "")),
                timeout=timeout,
                headers=headers,
                max_retries=max_retries,
            )

            # Validate configuration - use FlextResult pattern
            validation_result = client_config.validate_business_rules()
            if not validation_result:
                return FlextResult[FlextApiHttpClientProtocol].fail(
                    validation_result.error or "Invalid client configuration"
                )

            # Convert to legacy config format for backward compatibility
            legacy_config = FlextApiClientConfig(
                base_url=client_config.base_url,
                timeout=client_config.timeout,
                headers=client_config.headers,
                max_retries=client_config.max_retries,
            )

            # Create client
            api_client = FlextApiClient(legacy_config)
            self._client = cast("FlextApiHttpClientProtocol", api_client)
            self._client_config = client_config
            logger.info("HTTP client created", base_url=client_config.base_url)

            return FlextResult[FlextApiHttpClientProtocol].ok(
                cast("FlextApiHttpClientProtocol", api_client)
            )

        except Exception as e:
            logger.exception("Client creation failed")
            return FlextResult[FlextApiHttpClientProtocol].fail(f"Client creation error: {e}")

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
                return FlextResult[FlextApiClient].fail("Invalid URL format: base_url cannot be empty")

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
                return FlextResult[FlextApiClient].fail(validation_result.error or "Invalid URL format")
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
