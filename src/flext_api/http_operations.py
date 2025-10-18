"""Generic HTTP Operations - Domain-agnostic HTTP method implementations.

This module provides HttpOperations, containing all HTTP method
implementations (GET, POST, PUT, DELETE, etc.) with flext-core patterns
and railway-oriented error handling. Completely generic and reusable
across any domain.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import TypeVar

from flext_core import FlextResult

T = TypeVar("T")


class HttpOperations[T]:
    """Generic HTTP operation methods with flext-core railway patterns.

    Provides all standard HTTP methods (GET, POST, PUT, DELETE, etc.) with
    consistent error handling and type safety. Each method follows the
    railway pattern, returning FlextResult for composable error handling.
    Completely domain-agnostic and reusable across any HTTP client implementation.
    """

    def get(
        self,
        url: str,
        *,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> FlextResult[T]:
        """Perform HTTP GET request with railway error handling."""
        return self._execute_request(
            "GET", url, params=params, headers=headers, timeout=timeout
        )

    def post(
        self,
        url: str,
        data: object | None = None,
        *,
        json: object | None = None,
        json_data: object | None = None,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> FlextResult[T]:
        """Perform HTTP POST request with JSON/data support."""
        # Support both json and json_data parameters for backward compatibility
        request_data = json_data if json_data is not None else (json if json is not None else data)

        # Use the json_data parameter if available (newer API)
        if json_data is not None:
            return self._execute_request(
                "POST",
                url,
                data=request_data,
                params=params,
                headers=headers,
                timeout=timeout,
                json_data=json_data,
            )
        else:
            return self._execute_request(
                "POST",
                url,
                data=request_data,
                params=params,
                headers=headers,
                timeout=timeout,
            )

    def put(
        self,
        url: str,
        data: object | None = None,
        *,
        json: object | None = None,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> FlextResult[T]:
        """Perform HTTP PUT request with JSON/data support."""
        request_data = json if json is not None else data
        return self._execute_request(
            "PUT",
            url,
            data=request_data,
            params=params,
            headers=headers,
            timeout=timeout,
        )

    def patch(
        self,
        url: str,
        data: object | None = None,
        *,
        json: object | None = None,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> FlextResult[T]:
        """Perform HTTP PATCH request with JSON/data support."""
        request_data = json if json is not None else data
        return self._execute_request(
            "PATCH",
            url,
            data=request_data,
            params=params,
            headers=headers,
            timeout=timeout,
        )

    def delete(
        self,
        url: str,
        *,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> FlextResult[T]:
        """Perform HTTP DELETE request."""
        return self._execute_request(
            "DELETE", url, params=params, headers=headers, timeout=timeout
        )

    def head(
        self,
        url: str,
        *,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> FlextResult[T]:
        """Perform HTTP HEAD request."""
        return self._execute_request(
            "HEAD", url, params=params, headers=headers, timeout=timeout
        )

    def options(
        self,
        url: str,
        *,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> FlextResult[T]:
        """Perform HTTP OPTIONS request."""
        return self._execute_request(
            "OPTIONS", url, params=params, headers=headers, timeout=timeout
        )

    def request(
        self,
        method: str,
        url: str,
        *,
        data: object | None = None,
        json: object | None = None,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> FlextResult[T]:
        """Perform generic HTTP request with full parameter support."""
        request_data = json if json is not None else data
        return self._execute_request(
            method,
            url,
            data=request_data,
            params=params,
            headers=headers,
            timeout=timeout,
        )

    def _execute_request(
        self,
        method: str,
        url: str,
        *,
        data: object | None = None,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> FlextResult[T]:
        """Execute HTTP request - implemented by concrete client classes."""
        msg = "HTTP request execution must be implemented by concrete client"
        raise NotImplementedError(msg)
