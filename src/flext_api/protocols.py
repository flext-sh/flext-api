"""FlextApi Protocols - Modern API abstraction protocols for FLEXT ecosystem.

Provides abstract contracts for HTTP client operations, API management,
and service lifecycle patterns that other projects can implement.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Protocol, cast, runtime_checkable

from flext_core import FlextResult

from flext_api.client import FlextApiClient as ConcreteClient

# Type variables moved inside protocol classes to avoid module-level declarations


# =============================================================================
# FLEXT API PROTOCOLS - Modern HTTP API abstraction patterns
# =============================================================================


@runtime_checkable
class FlextApiClientProtocol(Protocol):
    """Modern HTTP API client protocol for type-safe HTTP operations.

    Defines the contract that all FLEXT API clients must implement,
    providing standardized HTTP operations with FlextResult error handling.
    """

    @abstractmethod
    async def get(
        self, path: str, params: dict[str, object] | None = None
    ) -> FlextResult[object]:
        """Execute HTTP GET request with type-safe response."""
        ...

    @abstractmethod
    async def post(
        self,
        path: str,
        json_data: dict[str, object] | None = None,
        data: bytes | None = None,
    ) -> FlextResult[object]:
        """Execute HTTP POST request with type-safe response."""
        ...

    @abstractmethod
    async def put(
        self,
        path: str,
        json_data: dict[str, object] | None = None,
        data: bytes | None = None,
    ) -> FlextResult[object]:
        """Execute HTTP PUT request with type-safe response."""
        ...

    @abstractmethod
    async def delete(
        self, path: str, params: dict[str, object] | None = None
    ) -> FlextResult[object]:
        """Execute HTTP DELETE request with type-safe response."""
        ...

    @abstractmethod
    async def start(self) -> FlextResult[None]:
        """Start HTTP client session."""
        ...

    @abstractmethod
    async def stop(self) -> FlextResult[None]:
        """Stop HTTP client session."""
        ...

    @abstractmethod
    def health_check(self) -> dict[str, object]:
        """Get client health status."""
        ...


@runtime_checkable
class FlextApiManagerProtocol(Protocol):
    """Modern HTTP API management protocol for service orchestration.

    Defines the contract for creating and managing HTTP clients,
    providing factory methods and service lifecycle management.
    """

    @abstractmethod
    def create_client(
        self, config: dict[str, object]
    ) -> FlextResult[FlextApiClientProtocol]:
        """Create HTTP client with configuration."""
        ...

    @abstractmethod
    def get_client(self) -> FlextApiClientProtocol | None:
        """Get current HTTP client instance."""
        ...

    @abstractmethod
    def get_info(self) -> FlextResult[dict[str, object]]:
        """Get API service information."""
        ...

    @abstractmethod
    def get_builder(self) -> object:
        """Get builder instance for queries and responses."""
        ...


@runtime_checkable
class FlextApiService(Protocol):
    """Modern HTTP API service protocol for lifecycle management.

    Defines the contract for API services with async lifecycle support
    and comprehensive health checking capabilities.
    """

    @abstractmethod
    async def start_async(self) -> FlextResult[None]:
        """Start API service asynchronously."""
        ...

    @abstractmethod
    async def stop_async(self) -> FlextResult[None]:
        """Stop API service asynchronously."""
        ...

    @abstractmethod
    async def health_check_async(self) -> FlextResult[dict[str, object]]:
        """Perform comprehensive async health check."""
        ...


@runtime_checkable
class FlextApiDiscovery(Protocol):
    """Modern API discovery protocol for entity and schema discovery.

    Defines the contract for discovering APIs, entities, and schemas
    from external services with type-safe error handling.
    """

    @abstractmethod
    async def discover_entities(self) -> FlextResult[list[dict[str, object]]]:
        """Discover available entities from the API."""
        ...

    @abstractmethod
    async def get_entity_schema(
        self, entity_name: str
    ) -> FlextResult[dict[str, object]]:
        """Get schema for a specific entity."""
        ...

    @abstractmethod
    async def get_entity_data(
        self, entity_name: str, **kwargs: object
    ) -> FlextResult[dict[str, object] | list[dict[str, object]]]:
        """Get data for a specific entity with query parameters."""
        ...


@runtime_checkable
class FlextApiAuthentication(Protocol):
    """Modern API authentication protocol for secure access.

    Defines the contract for authentication providers that can
    authenticate requests across different authentication methods.
    """

    @abstractmethod
    async def authenticate(self) -> FlextResult[dict[str, object]]:
        """Authenticate and return authentication data."""
        ...

    @abstractmethod
    async def refresh_authentication(self) -> FlextResult[dict[str, object]]:
        """Refresh authentication credentials."""
        ...

    @abstractmethod
    def get_auth_headers(self) -> dict[str, str]:
        """Get authentication headers for requests."""
        ...

    @abstractmethod
    def is_authenticated(self) -> bool:
        """Check if currently authenticated."""
        ...


# =============================================================================
# FACTORY CLASS - Modern API creation patterns consolidated
# =============================================================================


class FlextApiFactory:
    """Factory class for creating API clients and managers following flext-core patterns.

    Consolidates all factory methods in a single class to eliminate helper functions.
    """

    @staticmethod
    def create_client(
        config: dict[str, object],
    ) -> FlextResult[FlextApiClientProtocol]:
        """Factory function to create FlextApiClient implementation.

        Args:
            config: Client configuration dictionary

        Returns:
            FlextResult containing configured API client

        """
        # This would be implemented by the concrete implementation

        try:
            if not config.get("base_url"):
                return FlextResult[FlextApiClientProtocol].fail("base_url is required")

            # Extract timeout value safely
            timeout_val = config.get("timeout", 30.0)
            timeout = (
                float(timeout_val) if isinstance(timeout_val, (int, float)) else 30.0
            )

            # Extract max_retries value safely
            retries_val = config.get("max_retries", 3)
            max_retries = retries_val if isinstance(retries_val, int) else 3

            client = ConcreteClient(
                base_url=str(config["base_url"]),
                timeout=timeout,
                headers=cast("dict[str, str]", config.get("headers", {})),
                max_retries=max_retries,
            )
            return FlextResult[FlextApiClientProtocol].ok(
                cast("FlextApiClientProtocol", client)
            )

        except Exception as e:
            return FlextResult[FlextApiClientProtocol].fail(
                f"Failed to create client: {e}"
            )

    @staticmethod
    def create_manager(
        service_name: str | None = None,
        service_version: str | None = None,
        default_base_url: str | None = None,
    ) -> FlextResult[FlextApiManagerProtocol]:
        """Factory function to create FlextApiManager implementation.

        Args:
            service_name: Optional service name
            service_version: Optional service version
            default_base_url: Optional default base URL

        Returns:
            FlextResult containing configured API manager

        """
        from flext_api.api import FlextApi  # noqa: PLC0415

        try:
            manager = FlextApi(
                service_name=service_name or "flext-api",
                service_version=service_version or "0.9.0",
                default_base_url=default_base_url or "http://localhost:8000",
            )
            return FlextResult[FlextApiManagerProtocol].ok(
                cast("FlextApiManagerProtocol", manager)
            )

        except Exception as e:
            return FlextResult[FlextApiManagerProtocol].fail(
                f"Failed to create manager: {e}"
            )


__all__ = [
    "FlextApiAuthentication",
    "FlextApiClientProtocol",
    "FlextApiDiscovery",
    "FlextApiFactory",
    "FlextApiManagerProtocol",
    "FlextApiService",
]
