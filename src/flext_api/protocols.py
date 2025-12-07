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

from flext_api.constants import FlextApiConstants
from flext_api.typings import t


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
        accessible via parent class (e.g., `p.Foundation.Result`).
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
                ) -> FlextProtocols.Result[t.HttpResponseDict]:
                    """Execute an HTTP request."""
                    ...

                def get(
                    self,
                    url: str,
                    **kwargs: object,
                ) -> FlextProtocols.Result[t.HttpResponseDict]:
                    """Execute HTTP GET request."""
                    ...

                def post(
                    self,
                    url: str,
                    **kwargs: object,
                ) -> FlextProtocols.Result[t.HttpResponseDict]:
                    """Execute HTTP POST request."""
                    ...

                def put(
                    self,
                    url: str,
                    **kwargs: object,
                ) -> FlextProtocols.Result[t.HttpResponseDict]:
                    """Execute HTTP PUT request."""
                    ...

                def delete(
                    self,
                    url: str,
                    **kwargs: object,
                ) -> FlextProtocols.Result[t.HttpResponseDict]:
                    """Execute HTTP DELETE request."""
                    ...

        class Storage:
            """Storage backend protocols."""

            @runtime_checkable
            class StorageBackendProtocol(Protocol):
                """Protocol for generic storage backend implementations."""

                def get(self, key: str) -> FlextProtocols.Result[object]:
                    """Retrieve value by key. Returns error if key not found (no fallback)."""
                    ...

                def set(
                    self,
                    key: str,
                    value: object,
                    timeout: int | None = None,
                ) -> FlextProtocols.Result[bool]:
                    """Store value with optional timeout."""
                    ...

                def delete(self, key: str) -> FlextProtocols.Result[bool]:
                    """Delete value by key."""
                    ...

                def exists(self, key: str) -> FlextProtocols.Result[bool]:
                    """Check if key exists."""
                    ...

                def clear(self) -> FlextProtocols.Result[bool]:
                    """Clear all stored values."""
                    ...

                def keys(self) -> FlextProtocols.Result[list[str]]:
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


# Alias for simplified usage - exported for domain usage
p = FlextApiProtocols

__all__ = [
    "FlextApiProtocols",
    "p",
]
