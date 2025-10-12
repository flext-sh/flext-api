"""HTTP Operations for FlextApiClient.

This module contains the core HTTP operation methods extracted from FlextApiClient
to improve maintainability and reduce the size of the main client class.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextCore

from flext_api.typings import FlextApiTypes


class HttpOperations:
    """HTTP operation methods extracted from FlextApiClient."""

    def get(
        self,
        url: str,
        *,
        params: FlextCore.Types.Dict | None = None,
        headers: FlextCore.Types.Dict | None = None,
        timeout: float | None = None,
        **kwargs: object,
    ) -> FlextCore.Result[FlextApiTypes.JsonValue]:
        """Perform HTTP GET request.

        Args:
            url: Request URL path or full URL
            params: Query parameters
            headers: Additional headers
            timeout: Request timeout in seconds
            **kwargs: Additional request options

        Returns:
            FlextCore.Result containing response data or error

        """
        return self._execute_request(
            "GET", url, params=params, headers=headers, timeout=timeout, **kwargs
        )

    def post(
        self,
        url: str,
        data: FlextApiTypes.JsonValue | None = None,
        *,
        json: FlextApiTypes.JsonValue | None = None,
        params: FlextCore.Types.Dict | None = None,
        headers: FlextCore.Types.Dict | None = None,
        timeout: float | None = None,
        **kwargs: object,
    ) -> FlextCore.Result[FlextApiTypes.JsonValue]:
        """Perform HTTP POST request.

        Args:
            url: Request URL path or full URL
            data: Request body data
            json: JSON data to send
            params: Query parameters
            headers: Additional headers
            timeout: Request timeout in seconds
            **kwargs: Additional request options

        Returns:
            FlextCore.Result containing response data or error

        """
        if json is not None:
            data = json

        return self._execute_request(
            "POST",
            url,
            data=data,
            params=params,
            headers=headers,
            timeout=timeout,
            **kwargs,
        )

    def put(
        self,
        url: str,
        data: FlextApiTypes.JsonValue | None = None,
        *,
        json: FlextApiTypes.JsonValue | None = None,
        params: FlextCore.Types.Dict | None = None,
        headers: FlextCore.Types.Dict | None = None,
        timeout: float | None = None,
        **kwargs: object,
    ) -> FlextCore.Result[FlextApiTypes.JsonValue]:
        """Perform HTTP PUT request.

        Args:
            url: Request URL path or full URL
            data: Request body data
            json: JSON data to send
            params: Query parameters
            headers: Additional headers
            timeout: Request timeout in seconds
            **kwargs: Additional request options

        Returns:
            FlextCore.Result containing response data or error

        """
        if json is not None:
            data = json

        return self._execute_request(
            "PUT",
            url,
            data=data,
            params=params,
            headers=headers,
            timeout=timeout,
            **kwargs,
        )

    def patch(
        self,
        url: str,
        data: FlextApiTypes.JsonValue | None = None,
        *,
        json: FlextApiTypes.JsonValue | None = None,
        params: FlextCore.Types.Dict | None = None,
        headers: FlextCore.Types.Dict | None = None,
        timeout: float | None = None,
        **kwargs: object,
    ) -> FlextCore.Result[FlextApiTypes.JsonValue]:
        """Perform HTTP PATCH request.

        Args:
            url: Request URL path or full URL
            data: Request body data
            json: JSON data to send
            params: Query parameters
            headers: Additional headers
            timeout: Request timeout in seconds
            **kwargs: Additional request options

        Returns:
            FlextCore.Result containing response data or error

        """
        if json is not None:
            data = json

        return self._execute_request(
            "PATCH",
            url,
            data=data,
            params=params,
            headers=headers,
            timeout=timeout,
            **kwargs,
        )

    def delete(
        self,
        url: str,
        *,
        params: FlextCore.Types.Dict | None = None,
        headers: FlextCore.Types.Dict | None = None,
        timeout: float | None = None,
        **kwargs: object,
    ) -> FlextCore.Result[FlextApiTypes.JsonValue]:
        """Perform HTTP DELETE request.

        Args:
            url: Request URL path or full URL
            params: Query parameters
            headers: Additional headers
            timeout: Request timeout in seconds
            **kwargs: Additional request options

        Returns:
            FlextCore.Result containing response data or error

        """
        return self._execute_request(
            "DELETE", url, params=params, headers=headers, timeout=timeout, **kwargs
        )

    def head(
        self,
        url: str,
        *,
        params: FlextCore.Types.Dict | None = None,
        headers: FlextCore.Types.Dict | None = None,
        timeout: float | None = None,
        **kwargs: object,
    ) -> FlextCore.Result[FlextApiTypes.JsonValue]:
        """Perform HTTP HEAD request.

        Args:
            url: Request URL path or full URL
            params: Query parameters
            headers: Additional headers
            timeout: Request timeout in seconds
            **kwargs: Additional request options

        Returns:
            FlextCore.Result containing response headers or error

        """
        return self._execute_request(
            "HEAD", url, params=params, headers=headers, timeout=timeout, **kwargs
        )

    def options(
        self,
        url: str,
        *,
        params: FlextCore.Types.Dict | None = None,
        headers: FlextCore.Types.Dict | None = None,
        timeout: float | None = None,
        **kwargs: object,
    ) -> FlextCore.Result[FlextApiTypes.JsonValue]:
        """Perform HTTP OPTIONS request.

        Args:
            url: Request URL path or full URL
            params: Query parameters
            headers: Additional headers
            timeout: Request timeout in seconds
            **kwargs: Additional request options

        Returns:
            FlextCore.Result containing allowed methods or error

        """
        return self._execute_request(
            "OPTIONS", url, params=params, headers=headers, timeout=timeout, **kwargs
        )

    def request(
        self,
        method: str,
        url: str,
        *,
        data: FlextApiTypes.JsonValue | None = None,
        json: FlextApiTypes.JsonValue | None = None,
        params: FlextCore.Types.Dict | None = None,
        headers: FlextCore.Types.Dict | None = None,
        timeout: float | None = None,
        **kwargs: object,
    ) -> FlextCore.Result[FlextApiTypes.JsonValue]:
        """Perform generic HTTP request.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            url: Request URL path or full URL
            data: Request body data
            json: JSON data to send
            params: Query parameters
            headers: Additional headers
            timeout: Request timeout in seconds
            **kwargs: Additional request options

        Returns:
            FlextCore.Result containing response data or error

        """
        if json is not None:
            data = json

        return self._execute_request(
            method,
            url,
            data=data,
            params=params,
            headers=headers,
            timeout=timeout,
            **kwargs,
        )

    def _execute_request(
        self,
        method: str,
        url: str,
        *,
        data: FlextApiTypes.JsonValue | None = None,
        params: FlextCore.Types.Dict | None = None,
        headers: FlextCore.Types.Dict | None = None,
        timeout: float | None = None,
        **kwargs: object,
    ) -> FlextCore.Result[FlextApiTypes.JsonValue]:
        """Execute HTTP request (implemented by main client).

        This method should be implemented by the client class that inherits from HttpOperations.
        """
        # This will be implemented by the FlextApiClient class
        msg = "HTTP request execution must be implemented by client"
        raise NotImplementedError(msg)


__all__ = ["HttpOperations"]
