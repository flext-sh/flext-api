"""Generic plugin system for flext-api using FLEXT patterns.

Delegates to external libraries and flext-core for plugin management.
Provides abstract plugin types with Clean Architecture patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from flext_api import c, t
from flext_web import p


class FlextApiProtocolsBase:
    """FLEXT API transport implementations."""

    @runtime_checkable
    class HttpClient(Protocol):
        """Protocol for generic HTTP client implementations."""

        def delete(
            self,
            url: str,
            **kwargs: t.JsonValue,
        ) -> p.Result[t.Api.HttpResponseDict]:
            """Execute HTTP DELETE request."""
            ...

        def get(
            self,
            url: str,
            **kwargs: t.JsonValue,
        ) -> p.Result[t.Api.HttpResponseDict]:
            """Execute HTTP GET request."""
            ...

        def post(
            self,
            url: str,
            **kwargs: t.JsonValue,
        ) -> p.Result[t.Api.HttpResponseDict]:
            """Execute HTTP POST request."""
            ...

        def put(
            self,
            url: str,
            **kwargs: t.JsonValue,
        ) -> p.Result[t.Api.HttpResponseDict]:
            """Execute HTTP PUT request."""
            ...

        def request(
            self,
            method: c.Api.Method | str,
            url: str,
            **kwargs: t.JsonValue,
        ) -> p.Result[t.Api.HttpResponseDict]:
            """Execute an HTTP request."""
            ...

    @runtime_checkable
    class StorageBackend(Protocol):
        """Protocol for generic storage backend implementations."""

        def clear(self) -> p.Result[bool]:
            """Clear all stored values."""
            ...

        def delete(self, key: str) -> p.Result[bool]:
            """Delete value by key."""
            ...

        def exists(self, key: str) -> p.Result[bool]:
            """Check if key exists."""
            ...

        def get(self, key: str) -> p.Result[t.JsonValue]:
            """Retrieve value by key. Returns error if key not found (no fallback)."""
            ...

        def keys(self) -> p.Result[t.StrSequence]:
            """Get all keys."""
            ...

        def set(
            self,
            key: str,
            value: t.JsonValue,
            timeout: int | None = None,
        ) -> p.Result[bool]:
            """Store value with optional timeout."""
            ...

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

        def deserialize(self, data: bytes) -> t.JsonValue:
            """Deserialize bytes to data.

            Args:
                data: Bytes to deserialize

            Returns:
                Deserialized data

            """
            ...

        def serialize(self, data: t.JsonValue) -> bytes:
            """Serialize data to bytes.

            Args:
                data: Data to serialize

            Returns:
                Serialized bytes

            """
            ...

    @runtime_checkable
    class HttpResource(Protocol):
        """Protocol for HTTP resources that can be managed."""

        async def aclose(self) -> None:
            """Close the resource asynchronously."""

        def close(self) -> None:
            """Close the resource synchronously."""
            ...

    @runtime_checkable
    class TransportPlugin(Protocol):
        """Protocol for transport plugins.

        Defines the interface for transport implementations
        including HTTP, WebSocket, SSE, GraphQL, and gRPC.
        """

        def connect(
            self,
            url: str,
            **options: t.JsonValue,
        ) -> p.Result[str]:
            """Connect to endpoint."""
            ...

        def disconnect(
            self,
            connection: str,
        ) -> p.Result[bool]:
            """Disconnect from endpoint."""
            ...

        def send(
            self,
            connection: str,
            data: t.JsonMapping | t.Api.RequestBody,
        ) -> p.Result[t.Api.HttpResponseDict | str]:
            """Send data through connection."""
            ...

    @runtime_checkable
    class ProtocolHandler(Protocol):
        """Protocol handler interface for server registration."""

        def supports_protocol(self, protocol: str) -> bool:
            """Check if handler supports protocol."""
            ...

    @runtime_checkable
    class GrpcService(Protocol):
        """Protocol for gRPC service implementations.

        This protocol defines the interface that gRPC services should
        implement when flext-grpc is integrated.
        """

        def handle_request(self, request: t.JsonValue) -> p.Result[t.JsonValue]:
            """Handle gRPC request.

            Args:
                request: gRPC request

            Returns:
                r containing response or error

            """
            ...

        def register_methods(self) -> t.JsonList:
            """Register service methods.

            Returns:
                List of method descriptors (GrpcMethod when integrated)

            """
            ...

    @runtime_checkable
    class ProtobufService(Protocol):
        """Protocol for Protobuf service definitions.

        This protocol defines the interface for Protobuf-based services
        when flext-grpc is integrated.
        """

        def resolve_request_schema(
            self,
            method: str,
        ) -> p.Result[t.JsonMapping]:
            """Get request schema for method.

            Args:
                method: Method name

            Returns:
                r containing schema or error

            """
            ...

        def resolve_response_schema(self, method: str) -> p.Result[t.JsonMapping]:
            """Get response schema for method.

            Args:
                method: Method name

            Returns:
                r containing schema or error

            """
            ...
