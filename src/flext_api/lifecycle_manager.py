"""HTTP Resource Lifecycle Manager following SOLID principles.

Generic lifecycle management for HTTP resources using flext-core patterns.
Single responsibility: HTTP resource lifecycle management.
Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from flext_api.protocols import p

# Protocol reference for backward compatibility
HttpResourceProtocol = p.Api.Lifecycle.HttpResourceProtocol


class FlextApiLifecycleManager:
    """HTTP resource lifecycle manager following SOLID principles.

    Single responsibility: HTTP resource lifecycle management.
    Uses flext-core patterns for async resource management.
    """

    @staticmethod
    @asynccontextmanager
    async def manage_http_resource(resource: HttpResourceProtocol) -> AsyncIterator[HttpResourceProtocol]:
        """Manage HTTP resource lifecycle with proper cleanup."""
        try:
            yield resource
        finally:
            if hasattr(resource, "aclose") and callable(
                getattr(resource, "aclose", None),
            ):
                await resource.aclose()
            elif hasattr(resource, "close") and callable(
                getattr(resource, "close", None),
            ):
                resource.close()

    @staticmethod
    def manage_sync_http_resource(resource: HttpResourceProtocol) -> HttpResourceProtocol:
        """Manage synchronous HTTP resource lifecycle."""
        try:
            return resource
        finally:
            if hasattr(resource, "close") and callable(
                getattr(resource, "close", None),
            ):
                resource.close()


__all__ = [
    "FlextApiLifecycleManager",
    "HttpResourceProtocol",
]
