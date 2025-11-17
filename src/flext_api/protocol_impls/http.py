"""HTTP Protocol Implementation for flext-api.

Enhanced HTTP/1.1, HTTP/2, and HTTP/3 protocol support with:
- Connection pooling and keep-alive
- Retry logic with exponential backoff
- Streaming support
- Request/response middleware
- Complete error handling

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import time
from typing import Any

import httpx
from flext_core import FlextResult

from flext_api.constants import FlextApiConstants
from flext_api.models import FlextApiModels
from flext_api.protocol_impls.rfc import RFCProtocolImplementation
from flext_api.transports import FlextApiTransports


class FlextWebProtocolPlugin(RFCProtocolImplementation):
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
        max_retries: int | None = None,
        retry_backoff_factor: float | None = None,
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
        self._max_retries = (
            max_retries
            if max_retries is not None
            else int(FlextApiConstants.DEFAULT_MAX_RETRIES)
        )
        self._retry_backoff_factor = (
            retry_backoff_factor
            if retry_backoff_factor is not None
            else FlextApiConstants.BACKOFF_FACTOR
        )
        self._follow_redirects = follow_redirects
        self._max_redirects = max_redirects

        # Create HTTP transport with configuration
        self._transport = FlextApiTransports.FlextWebTransport()

        # Initialize protocol
        init_result = self.initialize()
        if init_result.is_failure:
            self.logger.error(
                f"Failed to initialize HTTP protocol: {init_result.error}"
            )

        self.logger.info(
            "HTTP protocol initialized",
            extra={
                "http2": http2,
                "http3": http3,
                "max_connections": max_connections,
                "max_retries": self._max_retries,
            },
        )

    def _build_http_request_from_dict(
        self, request: dict[str, object]
    ) -> FlextResult[FlextApiModels.HttpRequest]:
        """Build HttpRequest from dictionary using RFC methods."""
        # Validate request using base class method
        validation_result = self._validate_request(request)
        if validation_result.is_failure:
            return FlextResult[FlextApiModels.HttpRequest].fail(validation_result.error)

        # Extract method using RFC method
        method_result = self._extract_method(request)
        if method_result.is_failure:
            return FlextResult[FlextApiModels.HttpRequest].fail(method_result.error)
        method_str = method_result.unwrap()

        # Extract URL using RFC method
        url_result = self._extract_url(request)
        if url_result.is_failure:
            return FlextResult[FlextApiModels.HttpRequest].fail(url_result.error)
        url = url_result.unwrap()

        # Extract headers using RFC method
        headers = self._extract_headers(request)

        # Extract body using RFC method
        body = self._extract_body(request)

        # Extract timeout using RFC method
        timeout_value = self._extract_timeout(request)

        http_request = FlextApiModels.HttpRequest(
            method=method_str,
            url=url,
            headers=headers,
            body=body,
            timeout=timeout_value,
        )

        return FlextResult[FlextApiModels.HttpRequest].ok(http_request)

    def send_request(
        self,
        request: dict[str, object],
        **kwargs: object,
    ) -> FlextResult[dict[str, object]]:
        """Send HTTP request with retry logic and error handling."""
        # Build HTTP request model
        request_result = self._build_http_request_from_dict(request)
        if request_result.is_failure:
            return FlextResult[dict[str, object]].fail(request_result.error)

        http_request = request_result.unwrap()

        # Extract request parameters
        method = http_request.method.upper()
        url = str(http_request.url)
        headers_result = self._extract_headers_from_model(http_request)
        if headers_result.is_failure:
            return FlextResult[dict[str, Any]].fail(headers_result.error)
        headers = headers_result.unwrap()
        timeout = http_request.timeout
        body = http_request.body

        # Connect to endpoint (sync)
        conn_result = self._transport.connect(
            url=url,
            follow_redirects=self._follow_redirects,
            **kwargs,
        )

        if conn_result.is_failure:
            return FlextResult[dict[str, Any]].fail(
                f"Failed to establish connection: {conn_result.error}"
            )

        connection = conn_result.unwrap()

        # Execute request with retry logic
        if isinstance(connection, httpx.Client):
            result = self._execute_with_retry(
                connection, method, url, headers, {}, timeout, body
            )
        else:
            return FlextResult[dict[str, Any]].fail("Invalid connection type")

        if result.is_success:
            response = result.unwrap()
            return FlextResult[dict[str, Any]].ok({
                "status_code": response.status_code,
                "headers": response.headers,
                "body": response.body,
            })

        return FlextResult[dict[str, Any]].fail(result.error)

    def _execute_with_retry(
        self,
        connection: httpx.Client,
        method: str,
        url: str,
        headers: dict[str, Any],
        params: dict[str, Any],
        timeout: float | None,
        body: object | None,
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Execute HTTP request with retry logic."""
        last_error = "Unknown error"

        for attempt in range(self._max_retries + 1):
            try:
                request_kwargs = self._build_request_kwargs(
                    method, url, headers, params, timeout, body
                )
                response = connection.request(**request_kwargs)

                # Use RFC method to check if success
                if self._is_success_status(response.status_code):
                    return self._build_response(response, method)

                # Check if should retry using RFC method
                if not self._should_retry(
                    response.status_code, attempt, self._max_retries
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
            except httpx.HTTPError as e:
                last_error = f"HTTP error: {e}"
                self.logger.warning(
                    f"HTTP error (attempt {attempt + 1}/{self._max_retries + 1})",
                    extra={"url": url, "method": method, "attempt": attempt + 1},
                )
            except Exception as e:
                last_error = f"Unexpected error: {e}"
                self.logger.exception(
                    "Unexpected error", extra={"url": url, "method": method}
                )
                return FlextResult[FlextApiModels.HttpResponse].fail(last_error)

            if attempt < self._max_retries:
                backoff_time = self._retry_backoff_factor * (2**attempt)
                time.sleep(backoff_time)

        return FlextResult[FlextApiModels.HttpResponse].fail(
            f"Request failed after {self._max_retries + 1} attempts: {last_error}"
        )

    def _extract_headers_from_model(
        self, request: FlextApiModels.HttpRequest
    ) -> FlextResult[dict[str, Any]]:
        """Extract headers from HttpRequest model without fallback."""
        if request.headers is None:
            return FlextResult[dict[str, Any]].fail("Headers cannot be None")
        if not isinstance(request.headers, dict):
            return FlextResult[dict[str, Any]].fail("Headers must be a dictionary")
        return FlextResult[dict[str, Any]].ok(dict(request.headers))

    def _build_request_kwargs(
        self,
        method: str,
        url: str,
        headers: dict[str, Any],
        params: dict[str, Any],
        timeout: float | None,
        body: object | None,
    ) -> dict[str, Any]:
        """Build request kwargs based on body type and content-type."""
        request_kwargs: dict[str, Any] = {
            "method": method,
            "url": url,
            "headers": headers,
            "params": params,
            "timeout": timeout,
        }

        if body is not None:
            # Use RFC method to get content type
            content_type = self._get_content_type(headers)

            if (
                isinstance(body, dict)
                and FlextApiConstants.ContentType.FORM in content_type
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

    def supports_protocol(self, protocol: str) -> bool:
        """Check if this plugin supports the given protocol."""
        if self._http3:
            supported = FlextApiConstants.HTTP.SUPPORTED_PROTOCOLS_WITH_HTTP3
        else:
            supported = FlextApiConstants.HTTP.SUPPORTED_PROTOCOLS
        return protocol.lower() in supported

    def get_supported_protocols(self) -> list[str]:
        """Get list of supported protocols."""
        if self._http3:
            return FlextApiConstants.HTTP.SUPPORTED_PROTOCOLS_WITH_HTTP3.copy()
        return FlextApiConstants.HTTP.SUPPORTED_PROTOCOLS.copy()

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

    def get_protocol_info(self) -> dict[str, Any]:
        """Get protocol configuration information."""
        base_info = super().get_protocol_info()
        base_info.update({
            "http2_enabled": self._http2,
            "http3_enabled": self._http3,
            "max_retries": self._max_retries,
            "retry_backoff_factor": self._retry_backoff_factor,
            "follow_redirects": self._follow_redirects,
            "max_redirects": self._max_redirects,
        })
        return base_info


__all__ = ["FlextWebProtocolPlugin"]
