"""FlextApiClient Protocols - Modern API abstraction protocols for FLEXT ecosystem.

Provides abstract contracts for HTTP client operations, API management,
and service lifecycle patterns that other projects can implement.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Protocol, runtime_checkable

from flext_core import FlextProtocols, FlextResult, FlextTypes


class FlextApiProtocols:
    """Unified API protocols using flext-core extensively - ZERO DUPLICATION."""

    # =============================================================================
    # Direct re-export of flext-core protocols - NO DUPLICATION
    # =============================================================================

    # Infrastructure protocols from flext-core
    Infrastructure = FlextProtocols.Infrastructure

    # =============================================================================
    # HTTP-specific protocols - Only what's not in flext-core
    # =============================================================================

    @runtime_checkable
    class HttpClient(Protocol):
        """HTTP client protocol using flext-core patterns."""

        @abstractmethod
        async def get(self, url: str, **kwargs: object) -> FlextResult[object]:
            """Make GET request."""
            ...

        @abstractmethod
        async def post(self, url: str, **kwargs: object) -> FlextResult[object]:
            """Make POST request."""
            ...

        @abstractmethod
        async def put(self, url: str, **kwargs: object) -> FlextResult[object]:
            """Make PUT request."""
            ...

        @abstractmethod
        async def delete(self, url: str, **kwargs: object) -> FlextResult[object]:
            """Make DELETE request."""
            ...

        @abstractmethod
        async def start(self) -> FlextResult[None]:
            """Start client."""
            ...

        @abstractmethod
        async def stop(self) -> FlextResult[None]:
            """Stop client."""
            ...

        @abstractmethod
        def health_check(self) -> FlextTypes.Core.Dict:
            """Health check."""
            ...

    @runtime_checkable
    class ApiManager(Protocol):
        """API manager extending flext-core manager protocol."""

        @abstractmethod
        def create_client(
            self, config: FlextTypes.Core.Dict
        ) -> FlextResult[FlextApiProtocols.HttpClient]:
            """Create HTTP client."""
            ...

        @abstractmethod
        def get_client(self) -> FlextApiProtocols.HttpClient | None:
            """Get current client."""
            ...

    @runtime_checkable
    class Authentication(Protocol):
        """Authentication protocol using flext-core patterns."""

        @abstractmethod
        async def authenticate(self) -> FlextResult[FlextTypes.Core.Dict]:
            """Authenticate."""
            ...

        @abstractmethod
        def get_auth_headers(self) -> FlextTypes.Core.Headers:
            """Get auth headers."""
            ...

        @abstractmethod
        def is_authenticated(self) -> bool:
            """Check authentication status."""
            ...


__all__ = ["FlextApiProtocols"]
