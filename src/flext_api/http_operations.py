"""Generic HTTP Operations following SOLID principles.

Domain-agnostic HTTP method implementations using flext-core patterns.
Single responsibility: HTTP method execution with railway error handling.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_core import FlextResult


class FlextApiOperations:
    """Generic HTTP operation methods following SOLID principles.

    Single responsibility: HTTP method execution with railway error handling.
    Uses flext-core patterns for type safety and composability.
    """

    @staticmethod
    def execute_get(
        url: str,
        *,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> FlextResult[dict[str, object]]:
        """Execute HTTP GET request with railway error handling."""
        # This method delegates to the actual HTTP client implementation
        # The HTTP client should implement this method
        msg = "HTTP client must implement execute_get"
        raise NotImplementedError(msg)

    @staticmethod
    def execute_post(
        url: str,
        data: object | None = None,
        *,
        json_data: object | None = None,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> FlextResult[dict[str, object]]:
        """Execute HTTP POST request with JSON/data support."""
        # This method delegates to the actual HTTP client implementation
        # The HTTP client should implement this method
        msg = "HTTP client must implement execute_post"
        raise NotImplementedError(msg)

    @staticmethod
    def execute_put(
        url: str,
        data: object | None = None,
        *,
        json_data: object | None = None,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> FlextResult[dict[str, object]]:
        """Execute HTTP PUT request with JSON/data support."""
        # This method delegates to the actual HTTP client implementation
        # The HTTP client should implement this method
        msg = "HTTP client must implement execute_put"
        raise NotImplementedError(msg)

    @staticmethod
    def execute_delete(
        url: str,
        *,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> FlextResult[dict[str, object]]:
        """Execute HTTP DELETE request with railway error handling."""
        # This method delegates to the actual HTTP client implementation
        # The HTTP client should implement this method
        msg = "HTTP client must implement execute_delete"
        raise NotImplementedError(msg)


__all__ = ["FlextApiOperations"]
