"""RFC Protocol Implementation for flext-api.

Implements RFC-compliant protocol patterns that extend BaseProtocolImplementation.
All standard protocol implementations (HTTP, WebSocket, etc.) should extend this class
to inherit RFC-compliant behavior.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_api import FlextApiBaseProtocolImplementation, c, m, p, r, t


class FlextApiRfcProtocolImplementation(FlextApiBaseProtocolImplementation):
    """RFC-compliant protocol implementation base class.

    Extends FlextApiBaseProtocolImplementation with RFC-compliant patterns and utilities.
    All standard protocol implementations should extend this class to inherit
    RFC-compliant behavior.

    RFC Patterns Implemented:
    - RFC 7230: HTTP/1.1 Message Syntax and Routing
    - RFC 7231: HTTP/1.1 Semantics and Content
    - RFC 7232: HTTP/1.1 Conditional Requests
    - RFC 7233: HTTP/1.1 Range Requests
    - RFC 7234: HTTP/1.1 Caching
    - RFC 7235: HTTP/1.1 Authentication
    - RFC 6455: WebSocket Protocol
    - RFC 7540: HTTP/2
    - RFC 8441: Bootstrapping WebSockets with HTTP/2

    Responsibilities:
    - RFC-compliant request/response handling
    - Standard header processing
    - Status code validation
    - Content-Type handling
    - Authentication patterns
    - Error response formatting

    """

    def __init__(
        self,
        name: str,
        version: str = "1.0.0",
        description: str = "",
        **kwargs: t.Scalar,
    ) -> None:
        """Initialize RFC protocol implementation.

        Args:
        name: Protocol name
        version: Protocol version
        description: Protocol description
        **kwargs: Additional configuration parameters

        """
        super().__init__(name=name, version=version, description=description, **kwargs)

    def _build_rfc_error_response(
        self,
        error: str,
        status_code: int = 500,
        error_code: str | None = None,
    ) -> t.ContainerValueMapping:
        """Build RFC-compliant error response (RFC 7231).

        Args:
        error: Error message
        status_code: HTTP status code
        error_code: Optional error code

        Returns:
        RFC-compliant error response dictionary

        """
        error_response: t.MutableContainerValueMapping = {
            "error": error,
            "status_code": status_code,
        }
        if error_code:
            error_response["error_code"] = error_code
        return error_response

    def _build_rfc_success_response(
        self,
        data: t.ContainerValueMapping | None = None,
        status_code: int = 200,
        headers: t.StrMapping | None = None,
    ) -> p.Result[t.ContainerValueMapping]:
        """Build RFC-compliant success response (RFC 7231).

        Args:
        data: Response data
        status_code: HTTP status code
        headers: Response headers

        Returns:
        r with RFC-compliant success response

        """
        json_data: t.MutableContainerValueMapping = {}
        if data is not None:
            for key, value in data.items():
                json_data[key] = value
        web_headers: t.AttributeMapping | None = None
        if headers is not None:
            web_headers = headers
        success_response: t.MutableContainerValueMapping = {
            "status_code": status_code,
        }
        if data is not None:
            success_response["data"] = json_data
        if web_headers is not None:
            success_response["headers"] = web_headers
        return r[t.ContainerValueMapping].ok(success_response)

    def _extract_body(
        self,
        request: t.ContainerValueMapping,
    ) -> t.ContainerValue | None:
        """Extract body from request (RFC 7231 compliant).

        Args:
        request: Request dictionary

        Returns:
        Request body or None

        """
        if "body" not in request:
            return None
        return request["body"]

    def _extract_headers(
        self,
        request: t.ContainerValueMapping,
    ) -> t.StrMapping:
        """Extract headers from request (RFC 7230 compliant).

        Args:
        request: Request dictionary

        Returns:
        Dictionary of headers (normalized to lowercase keys per RFC 7230)

        """
        if "headers" not in request:
            return {}
        try:
            parsed = m.Api.HeadersRequest.model_validate(request)
        except c.ValidationError:
            return {}
        normalized_headers: t.MutableStrMapping = {}
        for key, value in parsed.headers.items():
            normalized_headers[key.lower()] = value
        return normalized_headers

    def _extract_method(self, request: t.ContainerValueMapping) -> p.Result[str]:
        """Extract and validate HTTP method from request (RFC 7231 compliant).

        Args:
        request: Request dictionary

        Returns:
        r with validated method or error

        """
        try:
            parsed = m.Api.MethodRequest.model_validate(request)
        except c.ValidationError as exc:
            details = exc.errors()[0]["msg"] if exc.errors() else "Invalid HTTP method"
            return r[str].fail(details)
        except (ValueError, TypeError, KeyError, ConnectionError):
            return r[str].fail("Method must be a string (RFC 7231)")
        return r[str].ok(parsed.method)

    def _extract_timeout(self, request: t.ContainerValueMapping) -> float:
        """Extract timeout from request with defaults.

        Args:
        request: Request dictionary

        Returns:
        Timeout value in seconds

        """
        if "timeout" in request:
            try:
                parsed = m.Api.TimeoutRequest.model_validate(request)
                return parsed.timeout
            except c.ValidationError:
                return float(c.Api.DEFAULT_TIMEOUT)
        return float(c.Api.DEFAULT_TIMEOUT)

    def _extract_url(self, request: t.ContainerValueMapping) -> p.Result[str]:
        """Extract and validate URL from request (RFC 7230 compliant).

        Args:
        request: Request dictionary

        Returns:
        r with validated URL or error

        """
        if "url" not in request:
            return r[str].fail("URL is required in request (RFC 7230)")
        try:
            parsed = m.Api.UrlRequest.model_validate(request)
        except c.ValidationError as exc:
            details = exc.errors()[0]["msg"] if exc.errors() else "Invalid URL"
            return r[str].fail(details)
        except (ValueError, TypeError, KeyError, ConnectionError):
            return r[str].fail("URL must be a string (RFC 7230)")
        return r[str].ok(parsed.url)

    def _content_type(self, headers: t.StrMapping) -> str:
        """Extract Content-Type from headers (RFC 7231).

        Args:
        headers: Response headers

        Returns:
        Content-Type value or default

        """
        content_type_key = "content-type"
        if content_type_key in headers:
            return headers[content_type_key]
        return c.Api.ContentType.JSON

    def _client_error(self, status_code: int) -> bool:
        """Check if status code indicates client error (RFC 7231).

        Args:
        status_code: HTTP status code

        Returns:
        True if status code indicates client error (4xx range)

        """
        return (
            status_code >= c.Api.HTTP_CLIENT_ERROR_MIN
            and status_code < c.Api.HTTP_CLIENT_ERROR_MAX
        )

    def _server_error(self, status_code: int) -> bool:
        """Check if status code indicates server error (RFC 7231).

        Args:
        status_code: HTTP status code

        Returns:
        True if status code indicates server error (5xx range)

        """
        return status_code >= c.Api.HTTP_SERVER_ERROR_MIN

    def _success_status(self, status_code: int) -> bool:
        """Check if status code indicates success (RFC 7231).

        Args:
        status_code: HTTP status code

        Returns:
        True if status code indicates success (2xx range)

        """
        return (
            status_code >= c.Api.HTTP_SUCCESS_MIN
            and status_code < c.Api.HTTP_SUCCESS_MAX
        )

    def _normalize_header_name(self, header_name: str) -> str:
        """Normalize header name to lowercase (RFC 7230).

        Args:
        header_name: Header name to normalize

        Returns:
        Normalized header name

        """
        return header_name.lower()

    def _should_retry(self, status_code: int, attempt: int, max_retries: int) -> bool:
        """Determine if request should be retried (RFC 7231).

        Args:
        status_code: HTTP status code
        attempt: Current attempt number
        max_retries: Maximum number of retries

        Returns:
        True if request should be retried

        """
        if attempt >= max_retries:
            return False
        return status_code in c.Api.HTTPRetry.RETRYABLE_STATUS_CODES

    def _validate_status_code(self, status_code: int) -> p.Result[int]:
        """Validate HTTP status code (RFC 7231).

        Args:
        status_code: HTTP status code to validate

        Returns:
        r with validated status code or error

        """
        try:
            parsed = m.Api.StatusCodeValue(status_code=status_code)
        except c.ValidationError:
            return r[int].fail(
                f"Status code must be between 100 and 599 (RFC 7231): {status_code}",
            )
        return r[int].ok(parsed.status_code)


__all__: list[str] = ["FlextApiRfcProtocolImplementation"]
