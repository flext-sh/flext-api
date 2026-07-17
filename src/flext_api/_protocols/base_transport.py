"""Transport protocol shard."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from flext_api import p, t


class FlextApiProtocolsTransport:
    """Transport protocol shard."""

    @runtime_checkable
    class TransportPlugin(Protocol):
        """Protocol for transport plugins."""

        def connect(self, url: str, **options: t.JsonValue) -> p.Result[str]:
            """Connect to endpoint."""
            ...

        def disconnect(self, connection: str) -> p.Result[bool]:
            """Disconnect from endpoint."""
            ...

        def send(
            self, connection: str, data: t.JsonMapping | t.Api.RequestBody
        ) -> p.Result[t.Api.HttpResponseDict | str]:
            """Send data through connection."""
            ...

    @runtime_checkable
    class ProtocolHandler(Protocol):
        """Protocol handler interface for server registration."""

        def supports_protocol(self, protocol: str) -> bool:
            """Check if handler supports protocol."""
            ...


__all__: list[str] = ["FlextApiProtocolsTransport"]
