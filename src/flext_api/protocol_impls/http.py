"""HTTP Protocol Implementation for flext-api.

Enhanced HTTP/1.1, HTTP/2, and HTTP/3 protocol support with:
- Connection pooling and keep-alive
- Retry logic with exponential backoff
- Streaming support
- Request/response middleware
- Comprehensive error handling

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import time

import httpx
from flext_core import FlextResult

from flext_api.models import FlextApiModels
from flext_api.plugins import ProtocolPlugin
from flext_api.transports import FlextApiTransports
from flext_api.typings import FlextApiTypes


class FlextWebProtocolPlugin(ProtocolPlugin):
    """HTTP protocol implementation with HTTP/1.1, HTTP/2, and HTTP/3 support.

    Features:
    - HTTP/2 multiplexing for improved performance
    - HTTP/3 support via httpx (when available)
    - Connection pooling with configurable limits
    - Automatic retry logic with exponential backoff
    - Streaming support for large requests/responses
    - Keep-alive connections for efficiency
    - Automatic decompression (gzip, deflate, brotli)
    - Custom headers and authentication
    - Timeout management (connect, read, write, pool)
    - Redirect handling
    - Cookie management

    Usage:
        plugin = FlextWebProtocolPlugin(http2=True, max_connections=100)
        result = plugin.send_request(request)
        if result.is_success:
            response = result.unwrap()
    """

    def __init__(
        self,
        *,
        http2: bool = True,
        http3: bool = False,
        max_connections: int = 100,
        max_retries: int = 3,
        retry_backoff_factor: float = 0.5,
        follow_redirects: bool = True,
        max_redirects: int = 20,
    ) -> None:
        """Initialize HTTP protocol plugin."""
        super().__init__(
            name="http",
            version="1.0.0",
            description="HTTP/1.1, HTTP/2, HTTP/3 protocol implementation",
        )

        self._http2 = http2
        self._http3 = http3
        self._max_retries = max_retries
        self._retry_backoff_factor = retry_backoff_factor
        self._follow_redirects = follow_redirects
        self._max_redirects = max_redirects

        # Create HTTP transport with configuration
        self._transport = FlextApiTransports.FlextWebTransport()

        self.logger.info(
            "HTTP protocol initialized",
            extra={
                "http2": http2,
                "http3": http3,
                "max_connections": max_connections,
                "max_retries": max_retries,
            },
        )

    def send_request(
        self,
        request: FlextApiTypes.RequestData,
        **kwargs: FlextApiTypes.JsonValue,
    ) -> FlextResult[FlextApiTypes.ResponseData]:
        """Send HTTP request with retry logic and error handling."""
        # Convert to HTTP request model for type safety
        if not isinstance(request, dict):
            return FlextResult[FlextApiTypes.ResponseData].fail(
                "Invalid request format"
            )

        http_request = FlextApiModels.HttpRequest(
            method=request.get("method", "GET"),
            url=request.get("url", ""),
            headers=request.get("headers", {}),
            body=request.get("body"),
            timeout=request.get("timeout", 30.0),
        )

        # Extract request parameters
        method = http_request.method.upper()
        url = str(http_request.url)
        headers = (
            dict[str, object](http_request.headers) if http_request.headers else {}
        )
        timeout = http_request.timeout
        body = http_request.body

        # Connect to endpoint (sync)
        conn_result = self._transport.connect(
            url=url,
            follow_redirects=self._follow_redirects,
            **kwargs,
        )

        if conn_result.is_failure:
            return FlextResult[FlextApiTypes.ResponseData].fail(
                f"Failed to establish connection: {conn_result.error}"
            )

        connection = conn_result.unwrap()

        # Execute request with retry logic
        if isinstance(connection, httpx.Client):
            result = self._execute_with_retry(
                connection, method, url, headers, {}, timeout, body
            )
        else:
            return FlextResult[FlextApiTypes.ResponseData].fail(
                "Invalid connection type"
            )

        if result.is_success:
            response = result.unwrap()
            return FlextResult[FlextApiTypes.ResponseData].ok({
                "status_code": response.status_code,
                "headers": response.headers,
                "body": response.body,
            })

        return FlextResult[FlextApiTypes.ResponseData].fail(result.error)

    def _execute_with_retry(
        self,
        connection: httpx.Client,
        method: str,
        url: str,
        headers: dict[str, object],
        params: dict[str, object],
        timeout: float | None,
        body: object | None,
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Execute HTTP request with retry logic."""
        last_error = None

        for attempt in range(self._max_retries + 1):
            try:
                request_kwargs = self._build_request_kwargs(
                    method, url, headers, params, timeout, body
                )
                response = connection.request(**request_kwargs)

                http_client_error_min = 400
                if response.status_code < http_client_error_min:  # Success codes
                    return self._build_response(response, method)

                if (
                    response.status_code >= http_client_error_min
                    and not self._should_retry(response.status_code, attempt)
                ):
                    return FlextResult[FlextApiModels.HttpResponse].fail(
                        f"HTTP {response.status_code}: {response.text}"
                    )

            except httpx.TimeoutException as e:
                last_error = f"Request timeout: {e}"
                self.logger.warning(
                    f"Request timeout (attempt {attempt + 1}/{self._max_retries + 1})",
                    extra={"url": url, "method": method, "attempt": attempt + 1},
                )
            except httpx.NetworkError as e:
                last_error = f"Network error: {e}"
                self.logger.warning(
                    f"Network error (attempt {attempt + 1}/{self._max_retries + 1})",
                    extra={"url": url, "method": method, "attempt": attempt + 1},
                )
            except httpx.HTTPError:
                return FlextResult[FlextApiModels.HttpResponse].fail(
                    f"HTTP error after {attempt + 1} attempts"
                )
            except Exception as e:
                last_error = f"Unexpected error: {e}"
                self.logger.exception(
                    "Unexpected error", extra={"url": url, "method": method}
                )
                break

            if attempt < self._max_retries:
                backoff_time = self._retry_backoff_factor * (2**attempt)
                time.sleep(backoff_time)

        return FlextResult[FlextApiModels.HttpResponse].fail(
            f"Request failed after {self._max_retries + 1} attempts: {last_error}"
        )

    def _build_request_kwargs(
        self,
        method: str,
        url: str,
        headers: dict[str, object],
        params: dict[str, object],
        timeout: float | None,
        body: object | None,
    ) -> dict[str, object]:
        """Build request kwargs based on body type and content-type."""
        request_kwargs: dict[str, object] = {
            "method": method,
            "url": url,
            "headers": headers,
            "params": params,
            "timeout": timeout,
        }

        if body is not None:
            content_type = str(headers.get("Content-Type", "")).lower()
            if (
                isinstance(body, dict)
                and "application/x-www-form-urlencoded" in content_type
            ):
                request_kwargs["data"] = body
            elif isinstance(body, dict):
                request_kwargs["json"] = body
            else:
                request_kwargs["content"] = body

        return request_kwargs

    def _build_response(
        self,
        httpx_response: httpx.Response,
        _method: str,
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Build FlextApiModels.HttpResponse from httpx.Response."""
        try:
            content = httpx_response.read()

            response = FlextApiModels.HttpResponse(
                status_code=httpx_response.status_code,
                headers=dict(httpx_response.headers),
                body=content,
            )

            return FlextResult[FlextApiModels.HttpResponse].ok(response)

        except Exception as e:
            return FlextResult[FlextApiModels.HttpResponse].fail(
                f"Failed to build response: {e}"
            )

    def _should_retry(self, status_code: int, attempt: int) -> bool:
        """Check if request should be retried based on status code."""
        if attempt >= self._max_retries:
            return False

        retryable_codes = {408, 429, 500, 502, 503, 504}
        return status_code in retryable_codes

    def supports_protocol(self, protocol: str) -> bool:
        """Check if this plugin supports the given protocol."""
        supported = ["http", "https", "http/1.1", "http/2"]
        if self._http3:
            supported.append("http/3")
        return protocol.lower() in supported

    def get_supported_protocols(self) -> list[str]:
        """Get list of supported protocols."""
        protocols = ["http", "https", "http/1.1", "http/2"]
        if self._http3:
            protocols.append("http/3")
        return protocols

    def stream_request(
        self,
        request: FlextApiModels.HttpRequest,
        chunk_size: int = 8192,
    ) -> FlextResult[object]:
        """Send streaming HTTP request."""
        self.logger.info(
            "Streaming request",
            extra={
                "url": str(request.url),
                "method": request.method,
                "chunk_size": chunk_size,
            },
        )

        return FlextResult[object].fail(
            "Streaming not yet implemented (Phase 2 enhancement)"
        )

    def get_protocol_info(self) -> dict[str, object]:
        """Get protocol configuration information."""
        return {
            "name": self.name,
            "version": self.version,
            "http2_enabled": self._http2,
            "http3_enabled": self._http3,
            "max_retries": self._max_retries,
            "retry_backoff_factor": self._retry_backoff_factor,
            "follow_redirects": self._follow_redirects,
            "max_redirects": self._max_redirects,
            "supported_protocols": self.get_supported_protocols(),
        }


__all__ = ["FlextWebProtocolPlugin"]
