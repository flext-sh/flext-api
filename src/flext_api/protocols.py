"""Generic protocol definitions for HTTP operations.

All protocol interfaces are centralized here following FLEXT standards.
Single unified class with nested protocol definitions - no multiple top-level classes.
Domain-agnostic and reusable across any HTTP implementation.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from flext_core import FlextProtocols, FlextResult


class FlextApiProtocols(FlextProtocols):
    """Single unified HTTP protocols class extending flext-core FlextProtocols.

    Contains all protocol definitions for HTTP operations using nested classes.
    Follows FLEXT namespace class pattern - single class with nested protocol definitions.
    Domain-agnostic and reusable across any HTTP client implementation.
    """

    # =========================================================================
    # GENERIC HTTP PROTOCOLS - Nested classes within unified namespace
    # =========================================================================

    @runtime_checkable
    class HttpClientProtocol(Protocol):
        """Protocol for generic HTTP client implementations."""

        def request(
            self,
            method: str,
            url: str,
            **kwargs: object,
        ) -> FlextResult[Any]:
            """Execute an HTTP request."""
            ...

        def get(
            self,
            url: str,
            **kwargs: object,
        ) -> FlextResult[Any]:
            """Execute HTTP GET request."""
            ...

        def post(
            self,
            url: str,
            **kwargs: object,
        ) -> FlextResult[Any]:
            """Execute HTTP POST request."""
            ...

        def put(
            self,
            url: str,
            **kwargs: object,
        ) -> FlextResult[Any]:
            """Execute HTTP PUT request."""
            ...

        def delete(
            self,
            url: str,
            **kwargs: object,
        ) -> FlextResult[Any]:
            """Execute HTTP DELETE request."""
            ...

    @runtime_checkable
    class StorageBackendProtocol(Protocol):
        """Protocol for generic storage backend implementations."""

        def get(self, key: str, default: object = None) -> FlextResult[object]:
            """Retrieve value by key."""
            ...

        def set(
            self,
            key: str,
            value: object,
            timeout: int | None = None,
        ) -> FlextResult[None]:
            """Store value with optional timeout."""
            ...

        def delete(self, key: str) -> FlextResult[None]:
            """Delete value by key."""
            ...

        def exists(self, key: str) -> FlextResult[bool]:
            """Check if key exists."""
            ...

        def clear(self) -> FlextResult[None]:
            """Clear all stored values."""
            ...

        def keys(self) -> FlextResult[list[str]]:
            """Get all keys."""
            ...

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


__all__ = [
    "FlextApiProtocols",
]
