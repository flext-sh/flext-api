"""Protocol definitions for flext-api domain.

All protocol interfaces are centralized here following FLEXT standards.
Single unified class with nested protocol definitions - no multiple top-level classes.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from flext_core import FlextProtocols, FlextResult, FlextTypes

from .models import FlextApiModels
from .typings import FlextApiTypes


class FlextApiProtocols(FlextProtocols):
    """Single unified API protocols class extending flext-core FlextProtocols.

    Contains all protocol definitions for API domain operations using nested classes.
    Follows FLEXT namespace class pattern - single class with nested protocol definitions.
    """

    # =========================================================================
    # API-SPECIFIC PROTOCOLS - Nested classes within unified namespace
    # =========================================================================

    @runtime_checkable
    class HttpClientProtocol(Protocol):
        """Protocol for HTTP client implementations."""

        def request(
            self,
            method: str,
            url: str,
            **kwargs: object,
        ) -> FlextResult[FlextApiModels.HttpResponse]:
            """Execute an HTTP request."""

        def get(
            self,
            url: str,
            **kwargs: object,
        ) -> FlextResult[FlextApiModels.HttpResponse]:
            """Execute HTTP GET request."""

        def post(
            self,
            url: str,
            **kwargs: object,
        ) -> FlextResult[FlextApiModels.HttpResponse]:
            """Execute HTTP POST request."""

        def put(
            self,
            url: str,
            **kwargs: object,
        ) -> FlextResult[FlextApiModels.HttpResponse]:
            """Execute HTTP PUT request."""

        def delete(
            self,
            url: str,
            **kwargs: object,
        ) -> FlextResult[FlextApiModels.HttpResponse]:
            """Execute HTTP DELETE request."""

    @runtime_checkable
    class StorageBackendProtocol(Protocol):
        """Protocol for storage backend implementations."""

        def get(
            self, key: str, default: FlextApiTypes.JsonValue = None
        ) -> FlextResult[FlextApiTypes.JsonValue]:
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

        def keys(self) -> FlextResult[FlextTypes.StringList]:
            """Get all keys."""
            ...

    @runtime_checkable
    class LoggerProtocol(Protocol):
        """Protocol for logger implementations."""

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
