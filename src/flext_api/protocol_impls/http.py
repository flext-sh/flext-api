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
from collections.abc import (
    Iterator,
    Mapping,
    MutableMapping,
)
from typing import override

import httpx

from flext_api import (
    FlextApiProtocolsTransports,
    FlextApiRfcProtocolImplementation,
    c,
    m,
    p,
    r,
    t,
)


class FlextWebProtocolPlugin(FlextApiRfcProtocolImplementation):
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
    plugin = FlextWebProtocolPlugin(http2=True)
    result = plugin.send_request(request)
    if result.success:
    response = result.value
    """

    def __init__(
        self,
        *,
        http2: bool = True,
        http3: bool = False,
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
            max_retries if max_retries is not None else int(c.MAX_RETRY_ATTEMPTS)
        )
        self._retry_backoff_factor = (
            retry_backoff_factor
            if retry_backoff_factor is not None
            else c.Api.BACKOFF_FACTOR
        )
        self._follow_redirects = follow_redirects
        self._max_redirects = max_redirects
        self._transport = FlextApiProtocolsTransports.FlextWebTransport()

        def _log_initialize_error(error: str) -> None:
            self.logger.error("Failed to initialize HTTP protocol: %s", error)

        self.initialize().tap_error(_log_initialize_error)
        self.logger.info(
            "HTTP protocol initialized",
            http2=http2,
            http3=http3,
            max_retries=self._max_retries,
        )

    @override
    def protocol_info(self) -> Mapping[str, t.JsonValue | t.StrSequence]:
        """Get protocol configuration information."""
        return {
            **super().protocol_info(),
            "http2_enabled": self._http2,
            "http3_enabled": self._http3,
            "max_retries": self._max_retries,
            "retry_backoff_factor": self._retry_backoff_factor,
            "follow_redirects": self._follow_redirects,
            "max_redirects": self._max_redirects,
        }

    @override
    def supported_protocols(self) -> t.StrSequence:
        """Get list of supported protocols."""
        return list(
            c.Api.HTTP_PROTOCOL_SUPPORTED_WITH_HTTP3
            if self._http3
            else c.Api.HTTP_PROTOCOL_SUPPORTED
        )

    @override
    def send_request(
        self,
        request: t.JsonMapping,
        **kwargs: t.Scalar,
    ) -> p.Result[t.Api.HttpResponseDict]:
        """Send HTTP request with retry logic and error handling."""
        request_general: t.MutableJsonMapping = dict(request)
        request_result = self._build_http_request_from_dict(request_general)
        if request_result.failure:
            return r[t.Api.HttpResponseDict].fail(
                request_result.error or "Request building failed",
            )
        http_request = request_result.value
        method = http_request.method.upper()
        url = http_request.url
        headers_dict = dict(http_request.headers)
        timeout = http_request.timeout
        body = http_request.body
        conn_result = self._transport.connect(
            url=url,
            follow_redirects=self._follow_redirects,
        )
        if conn_result.failure:
            return r[t.Api.HttpResponseDict].fail(
                f"Failed to establish connection: {conn_result.error}",
            )
        last_error = "Unknown error"
        result: p.Result[m.Api.HttpResponse] = r[m.Api.HttpResponse].fail(last_error)
        for attempt in range(self._max_retries + 1):
            try:
                request_model = m.Api.HttpRequest.model_validate(
                    {
                        "method": method,
                        "url": url,
                        "headers": headers_dict,
                        "query_params": {},
                        "body": {} if body is None else body,
                        **({"timeout": timeout} if timeout is not None else {}),
                    },
                )
                response_result = self._transport.request_model(request_model)
                if response_result.failure:
                    last_error = response_result.error or "HTTP request failed"
                    if attempt < self._max_retries:
                        backoff_time = self._retry_backoff_factor * 2**attempt
                        time.sleep(backoff_time)
                        continue
                    result = r[m.Api.HttpResponse].fail(last_error)
                    break
                response = response_result.value
                if self._success_status(response.status_code):
                    result = r[m.Api.HttpResponse].ok(response)
                    break
                if not self._should_retry(
                    response.status_code,
                    attempt,
                    self._max_retries,
                ):
                    result = r[m.Api.HttpResponse].fail(
                        f"HTTP {response.status_code}: {response.body}",
                    )
                    break
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
            except c.ValidationError as e:
                last_error = f"Invalid request argument type: {e}"
            except (ValueError, TypeError, KeyError, ConnectionError) as e:
                last_error = self._handle_request_exception(
                    e,
                    url,
                    method,
                )
            if attempt < self._max_retries:
                backoff_time = self._retry_backoff_factor * 2**attempt
                time.sleep(backoff_time)
        else:
            result = r[m.Api.HttpResponse].fail(
                f"Request failed after {self._max_retries + 1} attempts: {last_error}",
            )
        return result.fold(
            on_failure=lambda e: r[t.Api.HttpResponseDict].fail(
                e or "Request execution failed",
            ),
            on_success=lambda response: r[t.Api.HttpResponseDict].ok(
                self._response_to_dict(response),
            ),
        )

    def stream_request(
        self,
        request: m.Api.HttpRequest,
        chunk_size: int = 8192,
    ) -> p.Result[Iterator[bytes]]:
        """Send streaming HTTP request."""
        self.logger.info(
            "Streaming request",
            url=request.url,
            method=request.method,
            chunk_size=chunk_size,
        )
        if chunk_size <= 0:
            return r[Iterator[bytes]].fail("chunk_size must be greater than 0")
        request_kwargs = self._build_request_kwargs(
            request,
            {},
        )
        call_args = request_kwargs

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
                    data=call_args.data,
                    json=call_args.json_body,
                    content=call_args.content,
                    timeout=call_args.timeout,
                ) as response,
            ):
                response.raise_for_status()
                for chunk in response.iter_bytes(chunk_size=chunk_size):
                    if chunk:
                        yield chunk

        return r[Iterator[bytes]].ok(_iter_stream_chunks())

    @override
    def supports_protocol(self, protocol: str) -> bool:
        """Check if this plugin supports the given protocol."""
        if self._http3:
            supported = c.Api.HTTP_PROTOCOL_SUPPORTED_WITH_HTTP3
        else:
            supported = c.Api.HTTP_PROTOCOL_SUPPORTED
        return protocol.lower() in supported

    def _build_http_request_from_dict(
        self,
        request: t.JsonMapping,
    ) -> p.Result[m.Api.HttpRequest]:
        """Build HttpRequest from dictionary using RFC methods."""
        validation_result = self._validate_request(request)
        if validation_result.failure:
            return r[m.Api.HttpRequest].fail(
                validation_result.error or "Request validation failed",
            )
        method_result = self._extract_method(request)
        if method_result.failure:
            return r[m.Api.HttpRequest].fail(
                method_result.error or "Method extraction failed",
            )
        url_result = self._extract_url(request)
        if url_result.failure:
            return r[m.Api.HttpRequest].fail(
                url_result.error or "URL extraction failed"
            )
        headers = self._extract_headers(request)
        body_value = self._extract_body(request)
        body = (
            t.Api.REQUEST_BODY_ADAPTER.validate_python(body_value)
            if body_value is not None
            else ""
        )
        http_request = m.Api.HttpRequest(
            method=method_result.value,
            url=url_result.value,
            headers=dict(headers),
            body=body,
            query_params={},
            timeout=self._extract_timeout(request),
        )
        return r[m.Api.HttpRequest].ok(http_request)

    def _build_request_kwargs(
        self,
        request: m.Api.HttpRequest,
        params: t.StrMapping,
    ) -> m.Api.HttpRequestCallArgs:
        """Build typed request call arguments based on body type."""
        method = request.method.upper()
        url = request.url
        headers = request.headers
        timeout = request.timeout
        body = request.body
        request_fields: MutableMapping[
            str, t.JsonMapping | t.StrMapping | t.JsonValue
        ] = {
            "method": method,
            "url": url,
            "headers": headers,
            "params": params,
            "data": None,
            "json_body": None,
            "content": None,
        }
        if timeout is not None:
            request_fields["timeout"] = timeout
        if body is None:
            return m.Api.HttpRequestCallArgs.model_validate(request_fields)
        content_type = self._content_type(headers)
        if isinstance(body, Mapping):
            parsed_mapping = m.Api.MappingBodyModel(body=body)
            if c.Api.ContentType.FORM in content_type:
                request_fields["data"] = parsed_mapping.body
                return m.Api.HttpRequestCallArgs.model_validate(request_fields)
            request_fields["json_body"] = parsed_mapping.body
            return m.Api.HttpRequestCallArgs.model_validate(request_fields)
        if isinstance(body, bytes):
            return m.Api.HttpRequestCallArgs(
                method=method,
                url=url,
                headers=headers,
                params=params,
                data=None,
                json_body=None,
                content=body,
                timeout=timeout,
            )
        if isinstance(body, str):
            return m.Api.HttpRequestCallArgs(
                method=method,
                url=url,
                headers=headers,
                params=params,
                data=None,
                json_body=None,
                content=body.encode("utf-8"),
                timeout=timeout,
            )
        msg = f"Unsupported body type: {type(body).__name__}"
        raise TypeError(msg)

    def _response_to_dict(
        self,
        response: m.Api.HttpResponse,
    ) -> t.Api.HttpResponseDict:
        """Convert HTTP response model to protocol response mapping."""
        body_value = self._response_body_to_value(response.body)
        return {
            "status_code": response.status_code,
            "headers": response.headers,
            "body": body_value,
        }

    def _response_body_to_value(
        self,
        body: t.Api.ResponseBody,
    ) -> t.Api.ResponseBody:
        """Normalize response body to the protocol response-body contract."""
        match body:
            case None:
                return None
            case str() as body_text:
                return body_text
            case bytes() as body_bytes:
                return body_bytes
            case Mapping() as body_mapping:
                return t.Api.RESPONSE_BODY_ADAPTER.validate_python(body_mapping)
            case _:
                return t.Api.RESPONSE_BODY_ADAPTER.validate_python(body)

    def _handle_request_exception(
        self,
        e: Exception,
        url: str,
        method: str,
    ) -> str:
        """Handle request exceptions and return error message."""
        error_msg = f"Unexpected error: {e}"
        self.logger.error("Unexpected error", url=url, method=method, error=error_msg)
        return error_msg


__all__: t.MutableSequenceOf[str] = ["FlextWebProtocolPlugin"]
