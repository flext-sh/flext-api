"""FLEXT API protocols leveraging flext-core hierarchical architecture.

This module provides type-safe protocols by composing flext-core's hierarchical
protocol architecture instead of defining local protocol duplications.

Following CLAUDE.md Phase 2: Eliminate duplication using flext-core patterns.
"""

from __future__ import annotations

from typing import Protocol

from flext_core import FlextResult
from flext_core.protocols import FlextProtocols

# ============================================================================
# API-SPECIFIC PROTOCOLS USING FLEXT-CORE FOUNDATION
# ============================================================================


class FlextApiHttpClientProtocol(FlextProtocols.Infrastructure.Connection, Protocol):
    """HTTP client protocol extending flext-core Infrastructure.Connection."""

    async def request(
        self, method: str, url: str, **kwargs: object
    ) -> FlextResult[object]:
        """Make HTTP request with FlextResult error handling."""
        ...

    async def close(self) -> None:
        """Close client session."""
        ...

    # HTTP convenience methods
    async def get(self, url: str, **kwargs: object) -> FlextResult[object]:
        """GET request."""
        ...

    async def post(self, url: str, **kwargs: object) -> FlextResult[object]:
        """POST request."""
        ...

    async def put(self, url: str, **kwargs: object) -> FlextResult[object]: ...

    async def delete(self, url: str, **kwargs: object) -> FlextResult[object]:
        """DELETE request."""
        ...

    # Plugin system
    @property
    def plugins(self) -> list[object]:
        """Get list of plugins."""
        ...


class FlextApiQueryBuilderProtocol(FlextProtocols.Foundation.Factory[object], Protocol):
    """Query builder protocol extending flext-core Foundation.Factory."""

    def build(self) -> object:
        """Build query object (implements Factory.create pattern)."""
        ...

    def create(self, **kwargs: object) -> FlextResult[object]:
        """Factory method for query creation."""
        ...


class FlextApiResponseBuilderProtocol(
    FlextProtocols.Foundation.Factory[object], Protocol
):
    """Response builder protocol extending flext-core Foundation.Factory."""

    def build(self) -> object:
        """Build response object (implements Factory.create pattern)."""
        ...

    def create(self, **kwargs: object) -> FlextResult[object]:
        """Factory method for response creation."""
        ...


# Export API-specific protocols (eliminate local duplication)
__all__: list[str] = [
    "FlextApiHttpClientProtocol",
    "FlextApiQueryBuilderProtocol",
    "FlextApiResponseBuilderProtocol",
]
