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

# =============================================================================
# FLEXT API PROTOCOLS - Modern HTTP API abstraction patterns
# =============================================================================


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
        ) -> FlextResult[object]: ...

        @abstractmethod
        async def post(
            self,
            path: str,
            json_data: FlextApiTypes.Core.Dict | None = None,
            data: bytes | None = None,
        ) -> FlextResult[object]: ...

        @abstractmethod
        async def put(
            self,
            path: str,
            json_data: FlextApiTypes.Core.Dict | None = None,
            data: bytes | None = None,
        ) -> FlextResult[object]: ...

        @abstractmethod
        async def delete(
            self,
            path: str,
            params: FlextApiTypes.Core.Dict | None = None,
        ) -> FlextResult[object]: ...

        @abstractmethod
        async def start(self) -> FlextResult[None]: ...

        @abstractmethod
        async def stop(self) -> FlextResult[None]: ...

        @abstractmethod
        def health_check(self) -> FlextApiTypes.Core.Dict: ...

    @runtime_checkable
    class Manager(Protocol):
        """API management protocol for client orchestration."""

        @abstractmethod
        def create_client(
            self,
            config: FlextApiTypes.Core.Dict,
        ) -> FlextResult[FlextApiProtocols.Client]: ...

        @abstractmethod
        def get_client(self) -> FlextApiProtocols.Client | None: ...

        @abstractmethod
        def get_info(self) -> FlextResult[FlextApiTypes.Core.Dict]: ...

        @abstractmethod
        def get_builder(self) -> object: ...

    @runtime_checkable
    class Service(Protocol):
        """API service lifecycle management protocol."""

        @abstractmethod
        async def start_async(self) -> FlextResult[None]: ...

        @abstractmethod
        async def stop_async(self) -> FlextResult[None]: ...

        @abstractmethod
        async def health_check_async(self) -> FlextResult[FlextApiTypes.Core.Dict]: ...

    @runtime_checkable
    class Discovery(Protocol):
        """Entity and schema discovery protocol."""

        @abstractmethod
        async def discover_entities(
            self,
        ) -> FlextResult[list[FlextApiTypes.Core.Dict]]: ...

        @abstractmethod
        async def get_entity_schema(
            self,
            entity_name: str,
        ) -> FlextResult[FlextApiTypes.Core.Dict]: ...

        @abstractmethod
        async def get_entity_data(
            self,
            entity_name: str,
            **kwargs: object,
        ) -> FlextResult[FlextApiTypes.Core.Dict | list[FlextApiTypes.Core.Dict]]: ...

    @runtime_checkable
    class Authentication(Protocol):
        """Authentication provider protocol."""

        @abstractmethod
        async def authenticate(self) -> FlextResult[FlextApiTypes.Core.Dict]: ...

        @abstractmethod
        async def refresh_authentication(
            self,
        ) -> FlextResult[FlextApiTypes.Core.Dict]: ...

        @abstractmethod
        def get_auth_headers(self) -> FlextApiTypes.HttpHeaders: ...

        @abstractmethod
        def is_authenticated(self) -> bool: ...


__all__ = ["FlextApiProtocols"]
