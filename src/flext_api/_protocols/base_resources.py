"""Resource lifecycle protocol shard."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


class FlextApiProtocolsResources:
    """Resource lifecycle protocol shard."""

    @runtime_checkable
    class HttpResource(Protocol):
        """Protocol for HTTP resources that can be managed."""

        async def aclose(self) -> None:
            """Close the resource asynchronously."""
            ...

        def close(self) -> None:
            """Close the resource synchronously."""
            ...


__all__: list[str] = ["FlextApiProtocolsResources"]
