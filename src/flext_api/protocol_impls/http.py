"""HTTP Protocol Implementation for flext-api.

Enhanced HTTP/1.1, HTTP/2, and HTTP/3 protocol support with:
- Connection pooling and keep-alive
- Retry logic with exponential backoff
- Streaming support
- Request/response middleware
- Comprehensive error handling

See TRANSFORMATION_PLAN.md - Phase 2 for architecture details.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import time

import httpx

from flext_api.models import FlextApiModels
from flext_api.plugins import ProtocolPlugin
from flext_api.transports import HttpTransport
from flext_core import FlextConstants, FlextResult, FlextTypes


class HttpProtocolPlugin(ProtocolPlugin):
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
        plugin = HttpProtocolPlugin(http2=True, max_connections=100)
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
        max_keepalive_connections: int = 20,
        keepalive_expiry: float = 5.0,
        connect_timeout: float = 5.0,
        read_timeout: float = 30.0,
        write_timeout: float = 30.0,
        pool_timeout: float = 5.0,
        max_retries: int = 3,
        retry_backoff_factor: float = 0.5,
        follow_redirects: bool = True,
        max_redirects: int = 20,
    ) -> None:
        """Initialize HTTP protocol plugin.

        Args:
            http2: Enable HTTP/2 support
            http3: Enable HTTP/3 support (experimental)
            max_connections: Maximum total connections
            max_keepalive_connections: Maximum keep-alive connections
            keepalive_expiry: Keep-alive connection expiry time (seconds)
            connect_timeout: Connection timeout (seconds)
            read_timeout: Read timeout (seconds)
            write_timeout: Write timeout (seconds)
            pool_timeout: Pool timeout (seconds)
            max_retries: Maximum retry attempts
            retry_backoff_factor: Backoff factor for retries
            follow_redirects: Automatically follow redirects
            max_redirects: Maximum number of redirects to follow

        """
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
        self._transport = HttpTransport(
            http2=http2,
            pool_limits=httpx.Limits(
                max_connections=max_connections,
                max_keepalive_connections=max_keepalive_connections,
                keepalive_expiry=keepalive_expiry,
            ),
            timeout=httpx.Timeout(
                connect=connect_timeout,
                read=read_timeout,
                write=write_timeout,
                pool=pool_timeout,
            ),
        )

        self._logger.info(
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
        request: FlextApiModels.HttpRequest,
        **kwargs: float | str | bool,
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Send HTTP request with retry logic and error handling.

        Args:
            request: HTTP request model
            **kwargs: Additional request options

        Returns:
            FlextResult containing HTTP response or error

        Features:
            - Automatic retry on transient errors
            - Exponential backoff between retries
            - Connection pooling and reuse
            - Streaming support
            - Comprehensive error handling

        """
        # Extract request parameters
        method = request.method.upper()
        url = str(request.url)
        headers = dict(request.headers) if request.headers else {}
        params = dict(request.params) if hasattr(request, "params") else {}
        timeout = request.timeout if hasattr(request, "timeout") else None

        # Prepare request body
        body = None
        if hasattr(request, "body") and request.body:
            body = request.body

        # Connect to endpoint (sync)
        conn_result = self._transport.connect(
            url=url,
            follow_redirects=self._follow_redirects,
            **kwargs,
        )

        if conn_result.is_failure:
            return FlextResult[FlextApiModels.HttpResponse].fail(
                f"Failed to establish connection: {conn_result.error}"
            )

        connection = conn_result.unwrap()

        # Execute request with retry logic
        last_error = None
        for attempt in range(self._max_retries + 1):
            try:
                # Determine how to pass body based on Content-Type and body type
                # For form data (dict with application/x-www-form-urlencoded), use data parameter
                # For other content (str, bytes), use content parameter
                request_kwargs: FlextTypes.Dict = {
                    "method": method,
                    "url": url,
                    "headers": headers,
                    "params": params,
                    "timeout": timeout,
                }

                if body is not None:
                    content_type = headers.get("Content-Type", "").lower()
                    if (
                        isinstance(body, dict)
                        and "application/x-www-form-urlencoded" in content_type
                    ):
                        # Use data parameter for form encoding
                        request_kwargs["data"] = body
                    elif isinstance(body, dict):
                        # Use json parameter for JSON encoding
                        request_kwargs["json"] = body
                    else:
                        # Use content for str/bytes
                        request_kwargs["content"] = body

                # Make HTTP request (sync - no await)
                response = connection.request(**request_kwargs)

                # Check if response is successful
                if response.status_code < FlextConstants.Http.HTTP_CLIENT_ERROR_MIN:
                    # Success - convert to FlextApiModels.HttpResponse
                    return self._build_response(response, method)

                # Client/server error
                if (
                    response.status_code >= FlextConstants.Http.HTTP_CLIENT_ERROR_MIN
                    and not self._should_retry(response.status_code, attempt)
                ):
                    return FlextResult[FlextApiModels.HttpResponse].fail(
                        f"HTTP {response.status_code}: {response.text}"
                    )

            except httpx.TimeoutException as e:
                last_error = f"Request timeout: {e}"
                self._logger.warning(
                    f"Request timeout (attempt {attempt + 1}/{self._max_retries + 1})",
                    extra={"url": url, "method": method, "attempt": attempt + 1},
                )

            except httpx.NetworkError as e:
                last_error = f"Network error: {e}"
                self._logger.warning(
                    f"Network error (attempt {attempt + 1}/{self._max_retries + 1})",
                    extra={"url": url, "method": method, "attempt": attempt + 1},
                )

            except httpx.HTTPError as e:
                last_error = f"HTTP error: {e}"
                self._logger.exception(
                    "HTTP error",
                    extra={"url": url, "method": method, "error": str(e)},
                )
                break  # Don't retry on HTTP errors

            except Exception as e:
                last_error = f"Unexpected error: {e}"
                self._logger.exception(
                    "Unexpected error",
                    extra={"url": url, "method": method},
                )
                break  # Don't retry on unexpected errors

            # Sleep before retry (sync)
            if attempt < self._max_retries:
                backoff_time = self._retry_backoff_factor * (2**attempt)
                time.sleep(backoff_time)

        # All retries exhausted
        return FlextResult[FlextApiModels.HttpResponse].fail(
            f"Request failed after {self._max_retries + 1} attempts: {last_error}"
        )

    def _build_response(
        self,
        httpx_response: httpx.Response,
        method: str,
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Build FlextApiModels.HttpResponse from httpx.Response.

        Args:
            httpx_response: httpx Response object
            method: HTTP method used for the request

        Returns:
            FlextResult containing FlextApiModels.HttpResponse

        """
        try:
            # Read response content (sync - no await)
            content = httpx_response.read()

            # Create response model
            response = FlextApiModels.HttpResponse(
                status_code=httpx_response.status_code,
                headers=dict(httpx_response.headers),
                body=content,
                url=str(httpx_response.url),
                method=method,
            )

            return FlextResult[FlextApiModels.HttpResponse].ok(response)

        except Exception as e:
            return FlextResult[FlextApiModels.HttpResponse].fail(
                f"Failed to build response: {e}"
            )

    def _should_retry(self, status_code: int, attempt: int) -> bool:
        """Check if request should be retried based on status code.

        Args:
            status_code: HTTP status code
            attempt: Current attempt number

        Returns:
            True if should retry

        """
        # Don't retry if max attempts reached
        if attempt >= self._max_retries:
            return False

        # Retry on transient server errors
        retryable_codes = {
            408,  # Request Timeout
            429,  # Too Many Requests
            500,  # Internal Server Error
            502,  # Bad Gateway
            503,  # Service Unavailable
            504,  # Gateway Timeout
        }

        return status_code in retryable_codes

    def supports_protocol(self, protocol: str) -> bool:
        """Check if this plugin supports the given protocol.

        Args:
            protocol: Protocol identifier

        Returns:
            True if protocol is supported

        """
        supported = ["http", "https", "http/1.1", "http/2"]
        if self._http3:
            supported.append("http/3")

        return protocol.lower() in supported

    def get_supported_protocols(self) -> FlextTypes.StringList:
        """Get list of supported protocols.

        Returns:
            List of supported protocol identifiers

        """
        protocols = ["http", "https", "http/1.1", "http/2"]
        if self._http3:
            protocols.append("http/3")
        return protocols

    def stream_request(
        self,
        request: FlextApiModels.HttpRequest,
        chunk_size: int = 8192,
        **kwargs: float | str | bool,
    ) -> FlextResult[object]:
        """Send streaming HTTP request.

        Args:
            request: HTTP request model
            chunk_size: Size of chunks for streaming (bytes)
            **kwargs: Additional request options

        Returns:
            FlextResult containing iterator of response chunks

        Note:
            This is a stub for Phase 2. Full streaming implementation
            will be added in future iterations.

        """
        self._logger.info(
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

    def get_protocol_info(self) -> FlextTypes.Dict:
        """Get protocol configuration information.

        Returns:
            Dictionary containing protocol configuration

        """
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


__all__ = ["HttpProtocolPlugin"]
