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
from collections.abc import Iterator, Mapping
from typing import override

import httpx
from flext_core import r
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from flext_api import c, m, t, u
from flext_api.protocol_impls.rfc import RFCProtocolImplementation
from flext_api.transports import FlextApiTransports


class _HttpRequestCallArgs(BaseModel):
    """Internal model for validating HTTP request call arguments.

    Used to validate and structure kwargs passed to httpx client methods.
    Ensures all required fields are present and properly typed.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    method: str = Field(..., description="HTTP method")
    url: str = Field(..., description="Request URL")
    headers: Mapping[str, str] = Field(default_factory=dict, description="HTTP headers")
    params: Mapping[str, str] = Field(
        default_factory=dict, description="Query parameters"
    )
    json_body: t.JsonValue | None = Field(default=None, description="JSON request body")
    content: bytes | None = Field(default=None, description="Raw content body")
    timeout: float | None = Field(default=None, description="Request timeout")


class _MappingBodyModel(BaseModel):
    """Internal model for wrapping mapping body data.

    Used to validate and structure dict-based request bodies.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    body: dict[str, object] = Field(..., description="Request body as mapping")


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
    response = result.value
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
            max_retries if max_retries is not None else int(c.Api.DEFAULT_MAX_RETRIES)
        )
        self._retry_backoff_factor = (
            retry_backoff_factor
            if retry_backoff_factor is not None
            else c.Api.BACKOFF_FACTOR
        )
        self._follow_redirects = follow_redirects
        self._max_redirects = max_redirects
        self._transport = FlextApiTransports.FlextWebTransport()
        self.initialize().tap_error(
            lambda e: self.logger.error(f"Failed to initialize HTTP protocol: {e}")
        )
        self.logger.info(
            "HTTP protocol initialized",
            http2=http2,
            http3=http3,
            max_connections=max_connections,
            max_retries=self._max_retries,
        )

    @override
    def get_protocol_info(self) -> t.JsonObject:
        """Get protocol configuration information."""
        base_info = super().get_protocol_info()
        updated_info: t.JsonObject = {
            **base_info,
            "http2_enabled": self._http2,
            "http3_enabled": self._http3,
            "max_retries": self._max_retries,
            "retry_backoff_factor": self._retry_backoff_factor,
            "follow_redirects": self._follow_redirects,
            "max_redirects": self._max_redirects,
        }
        return updated_info

    @override
    def get_supported_protocols(self) -> list[str]:
        """Get list of supported protocols."""
        if self._http3:
            return list(c.Api.HTTP.SUPPORTED_PROTOCOLS_WITH_HTTP3)
        return list(c.Api.HTTP.SUPPORTED_PROTOCOLS)

    @override
    def send_request(
        self, request: Mapping[str, object], **_kwargs: object
    ) -> r[Mapping[str, object]]:
        """Send HTTP request with retry logic and error handling."""
        request_general: dict[str, object] = {}
        for key, value in request.items():
            request_general[key] = self._to_general_value(value)
        request_result = self._build_http_request_from_dict(request_general)
        if request_result.is_failure:
            return r[Mapping[str, object]].fail(
                request_result.error or "Request building failed"
            )
        http_request = request_result.value
        method = http_request.method.upper()
        url = str(http_request.url)
        headers_result = self._extract_headers_from_model(http_request)
        if headers_result.is_failure:
            return r[Mapping[str, object]].fail(
                headers_result.error or "Headers extraction failed"
            )
        headers_dict = headers_result.value
        timeout = http_request.timeout
        body = http_request.body
        conn_result = self._transport.connect(
            url=url, follow_redirects=self._follow_redirects
        )
        if conn_result.is_failure:
            return r[Mapping[str, t.ApiJsonValue]].fail(
                f"Failed to establish connection: {conn_result.error}"
            )
        connection = conn_result.value
        result = self._execute_with_retry(
            connection, method, url, headers_dict, {}, timeout, body
        )
        return result.fold(
            on_failure=lambda e: r[Mapping[str, t.ApiJsonValue]].fail(
                e or "Request execution failed"
            ),
            on_success=lambda response: r[Mapping[str, t.ApiJsonValue]].ok({
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": str(getattr(response, "text", response.body)),
            }),
        )

    def stream_request(
        self, request: m.HttpRequest, chunk_size: int = 8192
    ) -> r[object]:
        """Send streaming HTTP request."""
        self.logger.info(
            "Streaming request",
            url=str(request.url),
            method=request.method,
            chunk_size=chunk_size,
        )
        if chunk_size <= 0:
            return r[object].fail("chunk_size must be greater than 0")
        headers_result = self._extract_headers_from_model(request)
        if headers_result.is_failure:
            return r[object].fail(headers_result.error or "Headers extraction failed")
        method = request.method.upper()
        url = str(request.url)
        request_kwargs = self._build_request_kwargs(
            method, url, headers_result.value, {}, request.timeout, request.body
        )
        try:
            call_args = _HttpRequestCallArgs.model_validate(request_kwargs)
        except ValidationError as e:
            return r[object].fail(f"Invalid streaming request arguments: {e}")

        def _iter_stream_chunks() -> Iterator[bytes]:
            timeout_config = (
                call_args.timeout
                if call_args.timeout is not None
                else float(c.Api.DEFAULT_TIMEOUT)
            )
            with (
                httpx.Client(
                    follow_redirects=self._follow_redirects,
                    max_redirects=self._max_redirects,
                    timeout=timeout_config,
                    http2=self._http2,
                ) as client,
                client.stream(
                    method=call_args.method,
                    url=call_args.url,
                    headers=call_args.headers,
                    params=call_args.params,
                    json=call_args.json_body,
                    content=call_args.content,
                    timeout=call_args.timeout,
                ) as response,
            ):
                response.raise_for_status()
                for chunk in response.iter_bytes(chunk_size=chunk_size):
                    if chunk:
                        yield chunk

        return r[object].ok(_iter_stream_chunks())

    @override
    def supports_protocol(self, protocol: str) -> bool:
        """Check if this plugin supports the given protocol."""
        if self._http3:
            supported = c.Api.HTTP.SUPPORTED_PROTOCOLS_WITH_HTTP3
        else:
            supported = c.Api.HTTP.SUPPORTED_PROTOCOLS
        return protocol.lower() in supported

    def _build_http_request_from_dict(
        self, request: Mapping[str, object]
    ) -> r[m.HttpRequest]:
        """Build HttpRequest from dictionary using RFC methods."""
        validation_result = self._validate_request(request)
        if validation_result.is_failure:
            return r[m.HttpRequest].fail(
                validation_result.error or "Request validation failed"
            )
        method_result = self._extract_method(request)
        if method_result.is_failure:
            return r[m.HttpRequest].fail(
                method_result.error or "Method extraction failed"
            )
        url_result = self._extract_url(request)
        if url_result.is_failure:
            return r[m.HttpRequest].fail(url_result.error or "URL extraction failed")
        headers = self._extract_headers(request)
        body_value = self._extract_body(request)
        body = u.Api.RequestUtils.to_request_body(body_value)
        http_request = m.HttpRequest(
            method=method_result.value,
            url=url_result.value,
            headers=dict(headers),
            body=body,
            timeout=self._extract_timeout(request),
        )
        return r[m.HttpRequest].ok(http_request)

    def _build_request_kwargs(
        self,
        method: str,
        url: str,
        headers: Mapping[str, str],
        params: Mapping[str, str],
        timeout: float | None,
        body: t.Api.RequestBody | None,
    ) -> Mapping[str, object]:
        """Build request kwargs based on body type."""
        kwargs: dict[str, object] = {
            "method": method,
            "url": url,
            "headers": headers,
            "params": params,
            "timeout": timeout,
        }
        if body is None:
            return kwargs
        content_type = self._get_content_type(headers)
        if isinstance(body, dict):
            try:
                parsed_mapping = _MappingBodyModel(body=body)
                if c.Api.ContentType.FORM in content_type:
                    kwargs["data"] = str(parsed_mapping.body)
                else:
                    kwargs["data"] = str(parsed_mapping.body)
                return kwargs
            except ValidationError:
                pass
        if isinstance(body, bytes):
            kwargs["content"] = body
        else:
            kwargs["content"] = str(body)
        return kwargs

    def _build_response(
        self, httpx_response: httpx.Response, _method: str
    ) -> r[m.HttpResponse]:
        """Build FlextApiModels.HttpResponse from httpx.Response."""
        try:
            content = httpx_response.read()
            response = m.HttpResponse(
                status_code=httpx_response.status_code,
                headers=dict(httpx_response.headers),
                body=content,
            )
            return r[m.HttpResponse].ok(response)
        except (ValueError, TypeError, KeyError, httpx.HTTPError, ConnectionError) as e:
            return r[m.HttpResponse].fail(f"Failed to build response: {e}")

    def _execute_with_retry(
        self,
        _connection_url: str,
        method: str,
        url: str,
        headers: Mapping[str, str],
        params: Mapping[str, str],
        timeout: float | None,
        body: t.Api.RequestBody | None,
    ) -> r[m.HttpResponse]:
        """Execute HTTP request with retry logic."""
        last_error = "Unknown error"
        for attempt in range(self._max_retries + 1):
            try:
                request_kwargs = self._build_request_kwargs(
                    method, url, headers, params, timeout, body
                )
                call_args = _HttpRequestCallArgs.model_validate(request_kwargs)
                client = self._transport.client
                if client is None:
                    return r[m.HttpResponse].fail("HTTP client is not connected")
                response = client.request(
                    method=call_args.method,
                    url=call_args.url,
                    headers=call_args.headers,
                    params=call_args.params,
                    json=call_args.json_body,
                    content=call_args.content,
                    timeout=call_args.timeout,
                )
                if self._is_success_status(response.status_code):
                    return self._build_response(response, method)
                if not self._should_retry(
                    response.status_code, attempt, self._max_retries
                ):
                    return r[m.HttpResponse].fail(
                        f"HTTP {response.status_code}: {response.text}"
                    )
            except httpx.TimeoutException as e:
                last_error = f"Request timeout: {e}"
                self.logger.warning(
                    f"Request timeout (attempt {attempt + 1}/{self._max_retries + 1})",
                    url=url,
                    method=method,
                    attempt=attempt + 1,
                )
            except httpx.NetworkError as e:
                last_error = f"Network error: {e}"
                self.logger.warning(
                    f"Network error (attempt {attempt + 1}/{self._max_retries + 1})",
                    url=url,
                    method=method,
                    attempt=attempt + 1,
                )
            except httpx.HTTPError as e:
                last_error = f"HTTP error: {e}"
                self.logger.warning(
                    f"HTTP error (attempt {attempt + 1}/{self._max_retries + 1})",
                    url=url,
                    method=method,
                    attempt=attempt + 1,
                )
            except ValidationError as e:
                last_error = f"Invalid request argument type: {e}"
            except (ValueError, TypeError, KeyError, ConnectionError) as e:
                last_error = self._handle_request_exception(
                    e, url, method, attempt, self._max_retries
                )
            if attempt < self._max_retries:
                backoff_time = self._retry_backoff_factor * 2**attempt
                time.sleep(backoff_time)
        return r[m.HttpResponse].fail(
            f"Request failed after {self._max_retries + 1} attempts: {last_error}"
        )

    def _extract_headers_from_model(
        self, request: m.HttpRequest
    ) -> r[Mapping[str, str]]:
        """Extract headers from HttpRequest model without fallback."""
        return r[Mapping[str, str]].ok(dict(request.headers))

    def _handle_request_exception(
        self, e: Exception, url: str, method: str, _attempt: int, _max_retries: int
    ) -> str:
        """Handle request exceptions and return error message."""
        error_msg = f"Unexpected error: {e}"
        self.logger.error("Unexpected error", url=url, method=method, error=str(e))
        return error_msg

    def _to_general_value(self, value: object) -> object:
        if value is None:
            return None
        if isinstance(value, list):
            normalized_items: list[object] = [
                self._to_general_value(item) for item in value
            ]
            return normalized_items
        if isinstance(value, Mapping):
            normalized_mapping: dict[str, object] = {}
            for key, item in value.items():
                normalized_mapping[str(key)] = self._to_general_value(item)
            return normalized_mapping
        if isinstance(value, (str, int, float, bool)):
            return value
        return str(value)


__all__ = ["FlextWebProtocolPlugin"]
