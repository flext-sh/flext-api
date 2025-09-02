"""FlextApi Protocols - Modern API abstraction protocols for FLEXT ecosystem.

Provides abstract contracts for HTTP client operations, API management,
and service lifecycle patterns that other projects can implement.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Protocol, TypeVar, cast, runtime_checkable

from flext_core import FlextResult

# Type variables for generic protocols
T = TypeVar("T")
TData = TypeVar("TData")


# =============================================================================
# FLEXT API PROTOCOLS - Modern HTTP API abstraction patterns
# =============================================================================

@runtime_checkable
class FlextApiClientProtocol(Protocol[TData]):
    """Modern HTTP API client protocol for type-safe HTTP operations.

    Defines the contract that all FLEXT API clients must implement,
    providing standardized HTTP operations with FlextResult error handling.
    """

    @abstractmethod
    async def get(
        self,
        path: str,
        params: dict[str, object] | None = None
    ) -> FlextResult[TData]:
        """Execute HTTP GET request with type-safe response."""
        ...

    @abstractmethod
    async def post(
        self,
        path: str,
        json_data: dict[str, object] | None = None,
        data: bytes | None = None
    ) -> FlextResult[TData]:
        """Execute HTTP POST request with type-safe response."""
        ...

    @abstractmethod
    async def put(
        self,
        path: str,
        json_data: dict[str, object] | None = None,
        data: bytes | None = None
    ) -> FlextResult[TData]:
        """Execute HTTP PUT request with type-safe response."""
        ...

    @abstractmethod
    async def delete(
        self,
        path: str,
        params: dict[str, object] | None = None
    ) -> FlextResult[TData]:
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
        self,
        config: dict[str, object]
    ) -> FlextResult[FlextApiClientProtocol[object]]:
        """Create HTTP client with configuration."""
        ...

    @abstractmethod
    def get_client(self) -> FlextApiClientProtocol[object] | None:
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
        self,
        entity_name: str
    ) -> FlextResult[dict[str, object]]:
        """Get schema for a specific entity."""
        ...

    @abstractmethod
    async def get_entity_data(
        self,
        entity_name: str,
        **kwargs: object
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
# FACTORY FUNCTIONS - Modern API creation patterns
# =============================================================================

def create_flext_api_client(config: dict[str, object]) -> FlextResult[FlextApiClientProtocol[object]]:
    """Factory function to create FlextApiClient implementation.

    Args:
        config: Client configuration dictionary

    Returns:
        FlextResult containing configured API client

    """
    # This would be implemented by the concrete implementation
    from flext_api.client import FlextApiClient as ConcreteClient

    try:
        if not config.get("base_url"):
            return FlextResult[FlextApiClientProtocol[object]].fail("base_url is required")

        client = ConcreteClient(
            base_url=str(config["base_url"]),
            timeout=float(config.get("timeout", 30.0)) if config.get("timeout") else 30.0,
            headers=cast("dict[str, str]", config.get("headers", {})),
            max_retries=int(config.get("max_retries", 3)) if config.get("max_retries") else 3,
        )
        return FlextResult[FlextApiClientProtocol[object]].ok(cast("FlextApiClientProtocol[object]", client))

    except Exception as e:
        return FlextResult[FlextApiClientProtocol[object]].fail(f"Failed to create client: {e}")


def create_flext_api_manager(
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
    from typing import cast

    from flext_api.api import FlextApi

    try:
        manager = FlextApi(
            service_name=service_name or "flext-api",
            service_version=service_version or "0.9.0",
            default_base_url=default_base_url or "http://localhost:8000",
        )
        return FlextResult[FlextApiManagerProtocol].ok(cast("FlextApiManagerProtocol", manager))

    except Exception as e:
        return FlextResult[FlextApiManagerProtocol].fail(f"Failed to create manager: {e}")


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "FlextApiAuthentication",
    # Protocol definitions
    "FlextApiClientProtocol",
    "FlextApiDiscovery",
    "FlextApiManagerProtocol",
    "FlextApiService",
    # Factory functions
    "create_flext_api_client",
    "create_flext_api_manager",
]
