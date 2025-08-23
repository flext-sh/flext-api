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
from flext_core.decorators import FlextDecorators
from pydantic import Field

from flext_api.base_service import FlextApiBaseService, FlextApiBaseService as _Base
from flext_api.client import FlextApiBuilder, FlextApiClient, FlextApiClientConfig
from flext_api.models import ClientConfig
from flext_api.protocols import (
    FlextApiClientProtocol,
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
    _client: FlextApiClientProtocol | None = None
    _client_config: ClientConfig | None = None

    def __init__(self, **_data: object) -> None:
        """Initialize FlextApi service with builder."""
        # Initialize base class with default field values, ignoring extra data
        super().__init__(
            service_name="FlextApi", service_version=__version__, is_running=False
        )
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

    @override
    async def health_check(self) -> FlextResult[dict[str, object]]:
        """Health check following parent async signature."""
        return await super().health_check()

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
                    res = loop_inner.run_until_complete(_Base.health_check(self))
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
                return loop.run_until_complete(_Base.health_check(self))
            finally:
                loop.close()

    def health_check_sync(self) -> FlextResult[dict[str, object]]:
        """Synchronous wrapper for health_check for legacy tests."""
        return self.sync_health_check()

    @FlextDecorators.safe_result  # type: ignore[arg-type]
    def create_client(
        self,
        config: ClientConfigDict | None = None,
    ) -> FlextApiClientProtocol:
        """Create HTTP client with configuration using modern FlextCallable patterns.

        Args:
            config: Client configuration dictionary with:
                - base_url: Required string, must start with http:// or https://
                - timeout: Optional float, defaults to 30.0 seconds
                - headers: Optional dict of string key-value pairs
                - max_retries: Optional int, defaults to 3
        Returns:
            FlextApiClientProtocol (automatically wrapped in FlextResult by decorator)

        """
        # Modern FlextCallable pattern - decorator handles exception wrapping
        config_dict = config or {}

        # Type-safe extraction with safe conversion
        timeout_val = config_dict.get("timeout", 30.0)
        try:
            timeout = (
                float(timeout_val)
                if isinstance(timeout_val, (int, float, str))
                else 30.0
            )
        except (ValueError, TypeError):
            timeout = 30.0

        headers_val = config_dict.get("headers", {})
        headers: dict[str, str] = (
            dict(headers_val) if isinstance(headers_val, dict) else {}
        )

        max_retries_val = config_dict.get("max_retries", 3)
        try:
            max_retries = (
                int(max_retries_val)
                if isinstance(max_retries_val, (int, float, str))
                else 3
            )
        except (ValueError, TypeError):
            max_retries = 3

        # Create and validate configuration
        client_config = ClientConfig(
            base_url=str(config_dict.get("base_url", "")),
            timeout=timeout,
            headers=headers,
            max_retries=max_retries,
        )

        # Validate configuration - let decorator handle failure cases
        validation_result = client_config.validate_business_rules()
        if not validation_result:
            raise ValueError(validation_result.error or "Invalid client configuration")

        # Convert to legacy config format for backward compatibility
        legacy_config = FlextApiClientConfig(
            base_url=client_config.base_url,
            timeout=client_config.timeout,
            headers=client_config.headers,
            max_retries=client_config.max_retries,
        )

        # Create client - decorator handles FlextResult wrapping
        api_client = FlextApiClient(legacy_config)
        self._client = cast("FlextApiClientProtocol", api_client)
        self._client_config = client_config
        logger.info("HTTP client created", base_url=client_config.base_url)

        return cast("FlextApiClientProtocol", api_client)

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

    def get_client(self) -> FlextApiClientProtocol | None:
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
    ) -> FlextApiClient:
        """Create internal client for testing and edge cases.

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
            msg = "Invalid URL format"
            raise ValueError(msg)
        # Type-safe extraction of timeout
        timeout_val = config_dict.get("timeout", 30.0)
        try:
            timeout = (
                float(timeout_val)
                if isinstance(timeout_val, (int, float, str))
                else 30.0
            )
        except (ValueError, TypeError):
            timeout = 30.0
        # Type-safe extraction of max_retries
        max_retries_val = config_dict.get("max_retries", 3)
        try:
            max_retries = (
                int(float(max_retries_val))
                if isinstance(max_retries_val, (int, float, str))
                else 3
            )
        except (ValueError, TypeError):
            max_retries = 3
        headers_raw = config_dict.get("headers", {})
        headers: dict[str, str] = headers_raw if isinstance(headers_raw, dict) else {}
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
            raise ValueError(validation_result.error or "Invalid URL format")
        # Convert to legacy config format
        legacy_config = FlextApiClientConfig(
            base_url=client_config.base_url,
            timeout=client_config.timeout,
            headers=client_config.headers,
            max_retries=client_config.max_retries,
        )
        return FlextApiClient(legacy_config)


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
