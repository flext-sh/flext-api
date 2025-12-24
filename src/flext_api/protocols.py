"""Generic protocol definitions for HTTP operations.

All protocol interfaces are centralized here following FLEXT standards.
Single unified class with nested protocol definitions organized under .Api namespace.
Domain-agnostic and reusable across any HTTP implementation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from flext_core.protocols import FlextProtocols

from flext import FlextResult as r
from flext_api.constants import FlextApiConstants


class FlextApiProtocols(FlextProtocols):
    """Single unified HTTP protocols class extending flext-core FlextProtocols.

    Contains all protocol definitions for HTTP operations organized under the .Api namespace.
    Follows FLEXT namespace class pattern - single class with nested protocol definitions.
    Domain-agnostic and reusable across any HTTP client implementation.

    **Namespace Structure:**
    All API-specific protocols are organized under the `.Api` namespace
    to enable proper namespace separation and access from dependent projects.

    **Usage:**
    ```python
    from flext_api.protocols import p

    # Access API protocols via .Api namespace
    client: p.Api.Client.HttpClientProtocol
    storage: p.Api.Storage.StorageBackendProtocol
    logger: p.Api.Logger.LoggerProtocol
    ```
    """

    class Api:
        """API-specific protocol namespace.

        All API domain-specific protocols are organized here to enable
        proper namespace separation. Parent protocols from flext-core are
        accessible via parent class (e.g., `p.Result`).
        """

        class Client:
            """HTTP client protocols."""

            @runtime_checkable
            class HttpClientProtocol(Protocol):
                """Protocol for generic HTTP client implementations."""

                def request(
                    self,
                    method: FlextApiConstants.Api.Method | str,
                    url: str,
                    **kwargs: object,
                ) -> r[dict[str, object]]:
                    """Execute an HTTP request."""
                    ...

                def get(
                    self,
                    url: str,
                    **kwargs: object,
                ) -> r[dict[str, object]]:
                    """Execute HTTP GET request."""
                    ...

                def post(
                    self,
                    url: str,
                    **kwargs: object,
                ) -> r[dict[str, object]]:
                    """Execute HTTP POST request."""
                    ...

                def put(
                    self,
                    url: str,
                    **kwargs: object,
                ) -> r[dict[str, object]]:
                    """Execute HTTP PUT request."""
                    ...

                def delete(
                    self,
                    url: str,
                    **kwargs: object,
                ) -> r[dict[str, object]]:
                    """Execute HTTP DELETE request."""
                    ...

        class Storage:
            """Storage backend protocols."""

            @runtime_checkable
            class StorageBackendProtocol(Protocol):
                """Protocol for generic storage backend implementations."""

                def get(self, key: str) -> r[object]:
                    """Retrieve value by key. Returns error if key not found (no fallback)."""
                    ...

                def set(
                    self,
                    key: str,
                    value: object,
                    timeout: int | None = None,
                ) -> r[bool]:
                    """Store value with optional timeout."""
                    ...

                def delete(self, key: str) -> r[bool]:
                    """Delete value by key."""
                    ...

                def exists(self, key: str) -> r[bool]:
                    """Check if key exists."""
                    ...

                def clear(self) -> r[bool]:
                    """Clear all stored values."""
                    ...

                def keys(self) -> r[list[str]]:
                    """Get all keys."""
                    ...

        class Logger:
            """Logger protocols for API operations."""

            @runtime_checkable
            class LoggerProtocol(Protocol):
                """Protocol for generic logger implementations."""

                def info(self, message: str, **kwargs: object) -> None:
                    """Log info message."""

                def error(self, message: str, **kwargs: object) -> None:
                    """Log error message."""

                def debug(self, message: str, **kwargs: object) -> None:
                    """Log debug message."""

                def warning(self, message: str, **kwargs: object) -> None:
                    """Log warning message."""

        class Serialization:
            """Serialization protocols."""

            @runtime_checkable
            class SerializerProtocol(Protocol):
                """Protocol for custom serializers.

                Defines the interface for serialization implementations
                including JSON, MessagePack, CBOR, etc.
                """

                def serialize(self, data: object) -> bytes:
                    """Serialize data to bytes.

                    Args:
                        data: Data to serialize

                    Returns:
                        Serialized bytes

                    """
                    ...

                def deserialize(self, data: bytes) -> object:
                    """Deserialize bytes to data.

                    Args:
                        data: Bytes to deserialize

                    Returns:
                        Deserialized data

                    """
                    ...

                @property
                def content_type(self) -> str:
                    """Get content type for this serializer."""
                    ...

        class Lifecycle:
            """HTTP resource lifecycle protocols."""

            @runtime_checkable
            class HttpResourceProtocol(Protocol):
                """Protocol for HTTP resources that can be managed."""

                def close(self) -> None:
                    """Close the resource synchronously."""
                    ...

                async def aclose(self) -> None:
                    """Close the resource asynchronously."""

        class Transport:
            """Transport layer protocols."""

            @runtime_checkable
            class TransportPlugin(Protocol):
                """Protocol for transport plugins.

                Defines the interface for transport implementations
                including HTTP, WebSocket, SSE, GraphQL, and gRPC.
                """

                def connect(self, url: str, **options: object) -> r[object]:
                    """Connect to endpoint."""
                    ...

                def disconnect(self, connection: object) -> r[bool]:
                    """Disconnect from endpoint."""
                    ...

                def send(self, connection: object, data: object) -> r[object]:
                    """Send data through connection."""
                    ...

        class Server:
            """Server registration protocols."""

            @runtime_checkable
            class ProtocolHandler(Protocol):
                """Protocol handler interface for server registration."""

                def supports_protocol(self, protocol: str) -> bool:
                    """Check if handler supports protocol."""
                    ...

        class Grpc:
            """gRPC-related protocols (stubs until flext-grpc integration)."""

            @runtime_checkable
            class GrpcServiceProtocol(Protocol):
                """Protocol for gRPC service implementations.

                This protocol defines the interface that gRPC services should
                implement when flext-grpc is integrated.
                """

                def register_methods(self) -> list[object]:
                    """Register service methods.

                    Returns:
                        List of method descriptors (GrpcMethod when integrated)

                    """
                    ...

                def handle_request(
                    self,
                    request: object,
                ) -> r[object]:
                    """Handle gRPC request.

                    Args:
                        request: gRPC request

                    Returns:
                        FlextResult containing response or error

                    """
                    ...

        class Protobuf:
            """Protobuf-related protocols (stubs until flext-grpc integration)."""

            @runtime_checkable
            class ProtobufServiceProtocol(Protocol):
                """Protocol for Protobuf service definitions.

                This protocol defines the interface for Protobuf-based services
                when flext-grpc is integrated.
                """

                def get_request_schema(self, method: str) -> r[object]:
                    """Get request schema for method.

                    Args:
                        method: Method name

                    Returns:
                        FlextResult containing schema or error

                    """
                    ...

                def get_response_schema(self, method: str) -> r[object]:
                    """Get response schema for method.

                    Args:
                        method: Method name

                    Returns:
                        FlextResult containing schema or error

                    """
                    ...


# Alias for simplified usage - exported for domain usage
p = FlextApiProtocols

__all__ = [
    "FlextApiProtocols",
    "p",
]
