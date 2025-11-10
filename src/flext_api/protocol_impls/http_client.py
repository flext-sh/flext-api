"""HTTP Client Protocol Implementation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import Any, Self

import httpx
from flext_core import FlextLogger, FlextResult

from flext_api.models import FlextApiModels
from flext_api.protocols import FlextApiProtocols


class FlextWebClientImplementation(FlextApiProtocols.HttpClientProtocol):
    """HTTP client implementation conforming to FlextWebClientProtocol."""

    def __init__(self, client_config: FlextApiModels.ClientConfig) -> None:
        """Initialize HTTP client protocol implementation.

        Args:
        client_config: HTTP client configuration

        """
        self._config = client_config
        self.logger = FlextLogger(__name__)

        # Create httpx client with configuration
        self._client = httpx.Client(
            timeout=httpx.Timeout(
                timeout=client_config.timeout,
                connect=client_config.timeout,
                read=client_config.timeout,
                write=client_config.timeout,
                pool=client_config.timeout,
            ),
            limits=httpx.Limits(
                max_connections=100,  # Connection pooling
                max_keepalive_connections=20,
            ),
            follow_redirects=True,
            verify=client_config.verify_ssl,
        )

    def _prepare_request_headers(self, kwargs: dict[str, object]) -> dict[str, str]:
        """Prepare merged headers from config and request."""
        headers = dict(self._config.headers)
        kwargs_headers = kwargs.get("headers")
        if isinstance(kwargs_headers, dict):
            headers.update({
                k: v for k, v in kwargs_headers.items() if isinstance(v, str)
            })
        return headers

    def _extract_request_data(self, kwargs: dict[str, object]) -> dict[str, Any]:
        """Extract and type request data parameters."""
        return {
            "params": kwargs.get("params")
            if isinstance(kwargs.get("params"), dict)
            else None,
            "json": kwargs.get("json"),
            "content": kwargs.get("content"),
            "data": kwargs.get("data"),
            "files": kwargs.get("files"),
        }

    def _create_response_from_httpx(
        self, httpx_response: httpx.Response
    ) -> FlextApiModels.HttpResponse:
        """Convert httpx response to FlextApiModels.HttpResponse."""
        return FlextApiModels.HttpResponse(
            status_code=httpx_response.status_code,
            headers=dict(httpx_response.headers),
            body=httpx_response.content,
        )

    def _handle_http_error(
        self, e: httpx.HTTPStatusError
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Handle HTTP status errors."""
        error_msg = f"HTTP error {e.response.status_code}: {e.response.text}"
        self.logger.warning(error_msg)
        response = self._create_response_from_httpx(e.response)
        return FlextResult[FlextApiModels.HttpResponse].ok(response)

    def _handle_request_exception(
        self, e: Exception, error_prefix: str
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Handle general request exceptions."""
        error_msg = f"{error_prefix}: {e}"
        if isinstance(e, (httpx.TimeoutException, httpx.NetworkError)):
            self.logger.warning(error_msg)
        else:
            self.logger.error(error_msg)
        return FlextResult[FlextApiModels.HttpResponse].fail(error_msg)

    def request(
        self,
        method: str,
        url: str,
        **kwargs: object,
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Execute an HTTP request conforming to protocol."""
        try:
            full_url = self._build_full_url(url)
            headers = self._prepare_request_headers(kwargs)
            request_data = self._extract_request_data(kwargs)

            # Make the HTTP request
            httpx_response = self._client.request(
                method=method,
                url=full_url,
                headers=headers,
                **request_data,
            )

            response = self._create_response_from_httpx(httpx_response)
            return FlextResult[FlextApiModels.HttpResponse].ok(response)

        except httpx.HTTPStatusError as e:
            return self._handle_http_error(e)
        except (httpx.TimeoutException, httpx.NetworkError, Exception) as e:
            error_prefix = (
                "HTTP request timeout"
                if isinstance(e, httpx.TimeoutException)
                else "HTTP network error"
                if isinstance(e, httpx.NetworkError)
                else "HTTP protocol request failed"
            )
            return self._handle_request_exception(e, error_prefix)

    def _build_full_url(self, url: str) -> str:
        """Build full URL from configuration base_url and provided path.

        Args:
        url: The URL path or full URL

        Returns:
        Full URL string

        """
        if url.startswith(("http://", "https://")):
            return url

        base_url = str(self._config.base_url or "http://localhost:8000").rstrip("/")
        path = str(url).lstrip("/")
        return f"{base_url}/{path}" if path else base_url

    def close(self) -> None:
        """Close the HTTP client and cleanup resources."""
        if hasattr(self, "_client"):
            self._client.close()

    def __enter__(self) -> Self:
        """Enter context manager."""
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        """Exit context manager and close client."""
        self.close()

    def get(
        self,
        url: str,
        **kwargs: object,
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Execute HTTP GET request."""
        return self.request("GET", url, **kwargs)

    def post(
        self,
        url: str,
        **kwargs: object,
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Execute HTTP POST request."""
        return self.request("POST", url, **kwargs)

    def put(
        self,
        url: str,
        **kwargs: object,
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Execute HTTP PUT request."""
        return self.request("PUT", url, **kwargs)

    def delete(
        self,
        url: str,
        **kwargs: object,
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Execute HTTP DELETE request."""
        return self.request("DELETE", url, **kwargs)
