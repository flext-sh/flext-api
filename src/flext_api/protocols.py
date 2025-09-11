"""FlextApi Protocols - Modern API abstraction protocols for FLEXT ecosystem.

Provides abstract contracts for HTTP client operations, API management,
and service lifecycle patterns that other projects can implement.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Protocol, runtime_checkable

from flext_core import FlextResult

from flext_api.typings import FlextApiTypes

"""Somente contratos (Protocols) - sem implementações ou fábricas concretas.

Qualquer lógica de criação permanece em `FlextApiClient.create` ou em camadas
de aplicação. Este módulo não deve depender de implementações concretas.
"""


class FlextApiProtocols:
    """Single aggregation namespace with nested protocol definitions (flext-core pattern)."""

    @runtime_checkable
    class Client(Protocol):
        """HTTP API client protocol for type-safe HTTP operations."""

        @abstractmethod
        async def get(
            self,
            path: str,
            params: FlextApiTypes.Core.Dict | None = None,
        ) -> FlextResult[object]:
            """Perform HTTP GET request.

            Args:
                path: Request path.
                params: Query parameters.

            Returns:
                FlextResult[object]: Response data.

            """
            ...

        @abstractmethod
        async def post(
            self,
            path: str,
            json_data: FlextApiTypes.Core.Dict | None = None,
            data: bytes | None = None,
        ) -> FlextResult[object]:
            """Perform HTTP POST request.

            Args:
                path: Request path.
                json_data: JSON data to send.
                data: Raw data to send.

            Returns:
                FlextResult[object]: Response data.

            """
            ...

        @abstractmethod
        async def put(
            self,
            path: str,
            json_data: FlextApiTypes.Core.Dict | None = None,
            data: bytes | None = None,
        ) -> FlextResult[object]:
            """Perform HTTP PUT request.

            Args:
                path: Request path.
                json_data: JSON data to send.
                data: Raw data to send.

            Returns:
                FlextResult[object]: Response data.

            """
            ...

        @abstractmethod
        async def delete(
            self,
            path: str,
            params: FlextApiTypes.Core.Dict | None = None,
        ) -> FlextResult[object]:
            """Perform HTTP DELETE request.

            Args:
                path: Request path.
                params: Query parameters.

            Returns:
                FlextResult[object]: Response data.

            """
            ...

        @abstractmethod
        async def start(self) -> FlextResult[None]:
            """Start the client.

            Returns:
                FlextResult[None]: Success or failure result.

            """
            ...

        @abstractmethod
        async def stop(self) -> FlextResult[None]:
            """Stop the client.

            Returns:
                FlextResult[None]: Success or failure result.

            """
            ...

        @abstractmethod
        def health_check(self) -> FlextApiTypes.Core.Dict:
            """Check client health.

            Returns:
                FlextApiTypes.Core.Dict: Health status information.

            """
            ...

    @runtime_checkable
    class Manager(Protocol):
        """API management protocol for client orchestration."""

        @abstractmethod
        def create_client(
            self,
            config: FlextApiTypes.Core.Dict,
        ) -> FlextResult[FlextApiProtocols.Client]:
            """Create new client instance.

            Args:
                config: Client configuration.

            Returns:
                FlextResult[FlextApiProtocols.Client]: Created client or error.

            """
            ...

        @abstractmethod
        def get_client(self) -> FlextApiProtocols.Client | None:
            """Get current client instance.

            Returns:
                FlextApiProtocols.Client | None: Current client or None.

            """
            ...

        @abstractmethod
        def get_info(self) -> FlextResult[FlextApiTypes.Core.Dict]:
            """Get manager information.

            Returns:
                FlextResult[FlextApiTypes.Core.Dict]: Manager info or error.

            """
            ...

        @abstractmethod
        def get_builder(self) -> object:
            """Get builder instance.

            Returns:
                object: Builder instance.

            """
            ...

    @runtime_checkable
    class Service(Protocol):
        """API service lifecycle management protocol."""

        @abstractmethod
        async def start_async(self) -> FlextResult[None]:
            """Start service asynchronously.

            Returns:
                FlextResult[None]: Success or failure result.

            """
            ...

        @abstractmethod
        async def stop_async(self) -> FlextResult[None]:
            """Stop service asynchronously.

            Returns:
                FlextResult[None]: Success or failure result.

            """
            ...

        @abstractmethod
        async def health_check_async(self) -> FlextResult[FlextApiTypes.Core.Dict]:
            """Check service health asynchronously.

            Returns:
                FlextResult[FlextApiTypes.Core.Dict]: Health status or error.

            """
            ...

    @runtime_checkable
    class Discovery(Protocol):
        """Entity and schema discovery protocol."""

        @abstractmethod
        async def discover_entities(
            self,
        ) -> FlextResult[list[FlextApiTypes.Core.Dict]]:
            """Discover available entities.

            Returns:
                FlextResult[list[FlextApiTypes.Core.Dict]]: Entity list or error.

            """
            ...

        @abstractmethod
        async def get_entity_schema(
            self,
            entity_name: str,
        ) -> FlextResult[FlextApiTypes.Core.Dict]:
            """Get entity schema.

            Args:
                entity_name: Name of the entity.

            Returns:
                FlextResult[FlextApiTypes.Core.Dict]: Schema or error.

            """
            ...

        @abstractmethod
        async def get_entity_data(
            self,
            entity_name: str,
            **kwargs: object,
        ) -> FlextResult[FlextApiTypes.Core.Dict | list[FlextApiTypes.Core.Dict]]:
            """Get entity data.

            Args:
                entity_name: Name of the entity.
                **kwargs: Additional parameters.

            Returns:
                FlextResult[FlextApiTypes.Core.Dict | list[FlextApiTypes.Core.Dict]]: Data or error.

            """
            ...

    @runtime_checkable
    class Authentication(Protocol):
        """Authentication provider protocol."""

        @abstractmethod
        async def authenticate(self) -> FlextResult[FlextApiTypes.Core.Dict]:
            """Authenticate with the service.

            Returns:
                FlextResult[FlextApiTypes.Core.Dict]: Authentication result or error.

            """
            ...

        @abstractmethod
        async def refresh_authentication(
            self,
        ) -> FlextResult[FlextApiTypes.Core.Dict]:
            """Refresh authentication token.

            Returns:
                FlextResult[FlextApiTypes.Core.Dict]: Refresh result or error.

            """
            ...

        @abstractmethod
        def get_auth_headers(self) -> FlextApiTypes.HttpHeaders:
            """Get authentication headers.

            Returns:
                FlextApiTypes.HttpHeaders: Authentication headers.

            """
            ...

        @abstractmethod
        def is_authenticated(self) -> bool:
            """Check if currently authenticated.

            Returns:
                bool: True if authenticated, False otherwise.

            """
            ...


__all__ = ["FlextApiProtocols"]
