"""Generic protocol definitions for HTTP operations.

All protocol interfaces are centralized here following FLEXT standards.
Single unified class with nested protocol definitions organized under .Api namespace.
Domain-agnostic and reusable across any HTTP implementation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol, runtime_checkable

from flext_cli import p

from flext_api import c, t
from flext_api._protocols.serialization import FlextApiProtocolsSerialization
from flext_core import r
from flext_web import FlextWebProtocols


class FlextApiProtocols(FlextWebProtocols, p):
    """Single unified HTTP protocols class extending flext-core FlextProtocols."""

    class Api:
        """API-specific protocol namespace.

        All API domain-specific protocols are organized here to enable
        proper namespace separation. Parent protocols from flext-core are
        accessible via parent class (e.g., `p.Result`).
        """

        class Client:
            """HTTP client protocols."""

            @runtime_checkable
            class HttpClient(Protocol):
                """Protocol for generic HTTP client implementations."""

                def delete(
                    self,
                    url: str,
                    **kwargs: t.ApiJsonValue,
                ) -> r[t.Api.HttpResponseDict]:
                    """Execute HTTP DELETE request."""
                    ...

                def get(
                    self,
                    url: str,
                    **kwargs: t.ApiJsonValue,
                ) -> r[t.Api.HttpResponseDict]:
                    """Execute HTTP GET request."""
                    ...

                def post(
                    self,
                    url: str,
                    **kwargs: t.ApiJsonValue,
                ) -> r[t.Api.HttpResponseDict]:
                    """Execute HTTP POST request."""
                    ...

                def put(
                    self,
                    url: str,
                    **kwargs: t.ApiJsonValue,
                ) -> r[t.Api.HttpResponseDict]:
                    """Execute HTTP PUT request."""
                    ...

                def request(
                    self,
                    method: c.Api.Method | str,
                    url: str,
                    **kwargs: t.ApiJsonValue,
                ) -> r[t.Api.HttpResponseDict]:
                    """Execute an HTTP request."""
                    ...

        class Storage:
            """Storage backend protocols."""

            @runtime_checkable
            class StorageBackend(Protocol):
                """Protocol for generic storage backend implementations."""

                def clear(self) -> r[bool]:
                    """Clear all stored values."""
                    ...

                def delete(self, key: str) -> r[bool]:
                    """Delete value by key."""
                    ...

                def exists(self, key: str) -> r[bool]:
                    """Check if key exists."""
                    ...

                def get(self, key: str) -> r[t.ApiJsonValue]:
                    """Retrieve value by key. Returns error if key not found (no fallback)."""
                    ...

                def keys(self) -> r[t.StrSequence]:
                    """Get all keys."""
                    ...

                def set(
                    self,
                    key: str,
                    value: t.ApiJsonValue,
                    timeout: int | None = None,
                ) -> r[bool]:
                    """Store value with optional timeout."""
                    ...

        class Logger:
            """Logger protocols for API operations."""

            @runtime_checkable
            class Logger(Protocol):
                """Protocol for generic logger implementations."""

                def debug(self, message: str, **kwargs: t.ApiJsonValue) -> None:
                    """Log debug message."""

                def error(self, message: str, **kwargs: t.ApiJsonValue) -> None:
                    """Log error message."""

                def info(self, message: str, **kwargs: t.ApiJsonValue) -> None:
                    """Log info message."""

                def warning(self, message: str, **kwargs: t.ApiJsonValue) -> None:
                    """Log warning message."""

        class Serialization:
            """Serialization protocols."""

            MsgpackModule = FlextApiProtocolsSerialization.MsgpackModule

            @runtime_checkable
            class Serializer(Protocol):
                """Protocol for custom serializers.

                Defines the interface for serialization implementations
                including JSON, MessagePack, CBOR, etc.
                """

                @property
                def content_type(self) -> str:
                    """Get content type for this serializer."""
                    ...

                def deserialize(self, data: bytes) -> t.ApiJsonValue:
                    """Deserialize bytes to data.

                    Args:
                        data: Bytes to deserialize

                    Returns:
                        Deserialized data

                    """
                    ...

                def serialize(self, data: t.ApiJsonValue) -> bytes:
                    """Serialize data to bytes.

                    Args:
                        data: Data to serialize

                    Returns:
                        Serialized bytes

                    """
                    ...

        class Lifecycle:
            """HTTP resource lifecycle protocols."""

            @runtime_checkable
            class HttpResource(Protocol):
                """Protocol for HTTP resources that can be managed."""

                async def aclose(self) -> None:
                    """Close the resource asynchronously."""

                def close(self) -> None:
                    """Close the resource synchronously."""
                    ...

        class Transport:
            """Transport layer protocols."""

            @runtime_checkable
            class TransportPlugin(Protocol):
                """Protocol for transport plugins.

                Defines the interface for transport implementations
                including HTTP, WebSocket, SSE, GraphQL, and gRPC.
                """

                def connect(self, url: str, **options: t.ApiJsonValue) -> r[str]:
                    """Connect to endpoint."""
                    ...

                def disconnect(self, connection: str) -> r[bool]:
                    """Disconnect from endpoint."""
                    ...

                def send(
                    self,
                    connection: str,
                    data: t.ContainerValueMapping | t.Api.RequestBody,
                ) -> r[t.Api.HttpResponseDict | str]:
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
            """gRPC-related protocols exposed through the flext-grpc boundary."""

            @runtime_checkable
            class GrpcService(Protocol):
                """Protocol for gRPC service implementations.

                This protocol defines the interface that gRPC services should
                implement when flext-grpc is integrated.
                """

                def handle_request(self, request: t.ApiJsonValue) -> r[t.ApiJsonValue]:
                    """Handle gRPC request.

                    Args:
                        request: gRPC request

                    Returns:
                        r containing response or error

                    """
                    ...

                def register_methods(self) -> Sequence[t.ApiJsonValue]:
                    """Register service methods.

                    Returns:
                        List of method descriptors (GrpcMethod when integrated)

                    """
                    ...

        class Protobuf:
            """Protobuf-related protocols exposed through the flext-grpc boundary."""

            @runtime_checkable
            class ProtobufService(Protocol):
                """Protocol for Protobuf service definitions.

                This protocol defines the interface for Protobuf-based services
                when flext-grpc is integrated.
                """

                def resolve_request_schema(self, method: str) -> r[t.JsonObject]:
                    """Get request schema for method.

                    Args:
                        method: Method name

                    Returns:
                        r containing schema or error

                    """
                    ...

                def resolve_response_schema(self, method: str) -> r[t.JsonObject]:
                    """Get response schema for method.

                    Args:
                        method: Method name

                    Returns:
                        r containing schema or error

                    """
                    ...


__all__: list[str] = ["FlextApiProtocols", "p"]

p = FlextApiProtocols
