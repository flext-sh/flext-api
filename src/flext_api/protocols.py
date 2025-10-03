"""Protocol definitions for flext-api domain.

All protocol interfaces are centralized here for better type safety and dependency inversion.
Following FLEXT standards: protocols only, no implementations.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from flext_core import FlextProtocols, FlextResult

from .models import FlextApiModels
from .typings import FlextApiTypes


class FlextApiProtocols:
    """Single unified API protocols class following FLEXT standards.

    Contains all protocol definitions for API domain operations.
    All protocols exposed as direct attributes for hierarchical access.
    """

    # =========================================================================
    # RE-EXPORT FOUNDATION PROTOCOLS - Use FlextProtocols from flext-core
    # =========================================================================

    Foundation = FlextProtocols.Foundation
    Domain = FlextProtocols.Domain
    Application = FlextProtocols.Application
    Infrastructure = FlextProtocols.Infrastructure
    Extensions = FlextProtocols.Extensions
    Commands = FlextProtocols.Commands

    # =========================================================================
    # API-SPECIFIC PROTOCOLS - Direct attributes for hierarchical access
    # =========================================================================


@runtime_checkable
class _HttpClientProtocol(Protocol):
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
class _StorageBackendProtocol(Protocol):
    """Protocol for storage backend implementations."""

    def get(
        self, key: str, default: FlextApiTypes.JsonValue = None
    ) -> FlextResult[FlextApiTypes.JsonValue]:
        """Retrieve value by key."""

    def set(
        self,
        key: str,
        value: object,
        timeout: int | None = None,
    ) -> FlextResult[None]:
        """Store value with optional timeout."""

    def delete(self, key: str) -> FlextResult[None]:
        """Delete value by key."""

    def exists(self, key: str) -> FlextResult[bool]:
        """Check if key exists."""

    def clear(self) -> FlextResult[None]:
        """Clear all stored values."""

    def keys(self: object) -> FlextResult[list[str]]:
        """Get all keys."""


@runtime_checkable
class _LoggerProtocol(Protocol):
    """Protocol for logger implementations."""

    def info(self, message: str, **kwargs: object) -> None:
        """Log info message."""

    def error(self, message: str, **kwargs: object) -> None:
        """Log error message."""

    def debug(self, message: str, **kwargs: object) -> None:
        """Log debug message."""

    def warning(self, message: str, **kwargs: object) -> None:
        """Log warning message."""


# =========================================================================
# API-SPECIFIC PROTOCOLS - Direct attributes for hierarchical access
# =========================================================================

# Direct protocol attributes (defined after class definitions to avoid forward reference issues)
FlextApiProtocols.LoggerProtocol = _LoggerProtocol

# =========================================================================
# RE-EXPORT FOUNDATION PROTOCOLS - Use FlextProtocols from flext-core
# =========================================================================

FlextApiProtocols.Foundation = FlextProtocols.Foundation
FlextApiProtocols.Domain = FlextProtocols.Domain
FlextApiProtocols.Application = FlextProtocols.Application
FlextApiProtocols.Infrastructure = FlextProtocols.Infrastructure
FlextApiProtocols.Extensions = FlextProtocols.Extensions
FlextApiProtocols.Commands = FlextProtocols.Commands

# Direct protocol attributes
FlextApiProtocols.HttpClientProtocol = _HttpClientProtocol
FlextApiProtocols.StorageBackendProtocol = _StorageBackendProtocol


__all__ = [
    "FlextApiProtocols",
]
