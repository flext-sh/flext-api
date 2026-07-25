"""gRPC protocol shard."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from flext_api.typings import t
from flext_web import p


class FlextApiProtocolsGrpc:
    """gRPC protocol shard."""

    @runtime_checkable
    class GrpcService(Protocol):
        """Protocol for gRPC service implementations."""

        def handle_request(self, request: t.JsonValue) -> p.Result[t.JsonValue]:
            """Handle gRPC request."""
            ...

        def register_methods(self) -> t.JsonList:
            """Register service methods."""
            ...

    @runtime_checkable
    class ProtobufService(Protocol):
        """Protocol for Protobuf service definitions."""

        def resolve_request_schema(self, method: str) -> p.Result[t.JsonMapping]:
            """Get request schema for method."""
            ...

        def resolve_response_schema(self, method: str) -> p.Result[t.JsonMapping]:
            """Get response schema for method."""
            ...


__all__: list[str] = ["FlextApiProtocolsGrpc"]
