"""RFC Protocol Implementation for flext-api.

Implements RFC-compliant protocol patterns that extend BaseProtocolImplementation.
All standard protocol implementations (HTTP, WebSocket, etc.) should extend this class
to inherit RFC-compliant behavior.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping

from flext_core import r
from pydantic import ValidationError

from flext_api import BaseProtocolImplementation, c, m, t


class RFCProtocolImplementation(BaseProtocolImplementation):
    """RFC-compliant protocol implementation base class.

    Extends BaseProtocolImplementation with RFC-compliant patterns and utilities.
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
    ) -> Mapping[str, t.ContainerValue]:
        """Build RFC-compliant error response (RFC 7231).

        Args:
        error: Error message
        status_code: HTTP status code
        error_code: Optional error code

        Returns:
        RFC-compliant error response dictionary

        """
        error_response: dict[str, t.ContainerValue] = {
            "error": error,
            "status_code": status_code,
        }
        if error_code:
            error_response["error_code"] = error_code
        return error_response

    def _build_rfc_success_response(
        self,
        data: Mapping[str, t.ContainerValue] | None = None,
        status_code: int = 200,
        headers: Mapping[str, str] | None = None,
    ) -> r[Mapping[str, t.ContainerValue]]:
        """Build RFC-compliant success response (RFC 7231).

        Args:
        data: Response data
        status_code: HTTP status code
        headers: Response headers

        Returns:
        r with RFC-compliant success response

        """
        json_data: dict[str, t.ContainerValue] | None = None
        if data is not None:
            json_data = {}
            for key, value in data.items():
                json_data[key] = value
        web_headers: dict[str, str | list[str]] | None = None
        if headers is not None:
            web_headers = dict(headers)
        success_response: dict[str, t.ContainerValue] = {"status_code": status_code}
        if json_data is not None:
            success_response["data"] = json_data
        if web_headers is not None:
            success_response["headers"] = web_headers
        return r.ok(success_response)

    def _extract_body(
        self,
        request: Mapping[str, t.ContainerValue],
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
        request: Mapping[str, t.ContainerValue],
    ) -> Mapping[str, str]:
        """Extract headers from request (RFC 7230 compliant).

        Args:
        request: Request dictionary

        Returns:
        Dictionary of headers (normalized to lowercase keys per RFC 7230)

        """
        if "headers" not in request:
            return {}
        try:
            parsed = m.Api._HeadersRequest.model_validate(request)
        except ValidationError:
            return {}
        normalized_headers: dict[str, str] = {}
        for key, value in parsed.headers.items():
            normalized_headers[key.lower()] = value
        return normalized_headers

    def _extract_method(self, request: Mapping[str, t.ContainerValue]) -> r[str]:
        """Extract and validate HTTP method from request (RFC 7231 compliant).

        Args:
        request: Request dictionary

        Returns:
        r with validated method or error

        """
        try:
            parsed = m.Api._MethodRequest.model_validate(request)
        except ValidationError as exc:
            details = exc.errors()[0]["msg"] if exc.errors() else "Invalid HTTP method"
            return r[str].fail(str(details))
        except (ValueError, TypeError, KeyError, ConnectionError):
            return r[str].fail("Method must be a string (RFC 7231)")
        return r[str].ok(parsed.method)

    def _extract_timeout(self, request: Mapping[str, t.ContainerValue]) -> float:
        """Extract timeout from request with defaults.

        Args:
        request: Request dictionary

        Returns:
        Timeout value in seconds

        """
        if "timeout" in request:
            try:
                parsed = m.Api._TimeoutRequest.model_validate(request)
                return parsed.timeout
            except ValidationError:
                return float(c.Api.DEFAULT_TIMEOUT)
        return float(c.Api.DEFAULT_TIMEOUT)

    def _extract_url(self, request: Mapping[str, t.ContainerValue]) -> r[str]:
        """Extract and validate URL from request (RFC 7230 compliant).

        Args:
        request: Request dictionary

        Returns:
        r with validated URL or error

        """
        if "url" not in request:
            return r[str].fail("URL is required in request (RFC 7230)")
        try:
            parsed = m.Api._UrlRequest.model_validate(request)
        except ValidationError as exc:
            details = exc.errors()[0]["msg"] if exc.errors() else "Invalid URL"
            return r[str].fail(str(details))
        except (ValueError, TypeError, KeyError, ConnectionError):
            return r[str].fail("URL must be a string (RFC 7230)")
        return r[str].ok(parsed.url)

    def _get_content_type(self, headers: Mapping[str, str]) -> str:
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

    def _is_client_error(self, status_code: int) -> bool:
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

    def _is_server_error(self, status_code: int) -> bool:
        """Check if status code indicates server error (RFC 7231).

        Args:
        status_code: HTTP status code

        Returns:
        True if status code indicates server error (5xx range)

        """
        return status_code >= c.Api.HTTP_SERVER_ERROR_MIN

    def _is_success_status(self, status_code: int) -> bool:
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

    def _validate_status_code(self, status_code: int) -> r[int]:
        """Validate HTTP status code (RFC 7231).

        Args:
        status_code: HTTP status code to validate

        Returns:
        r with validated status code or error

        """
        try:
            parsed = m.Api._StatusCodeValue(status_code=status_code)
        except ValidationError:
            return r[int].fail(
                f"Status code must be between 100 and 599 (RFC 7231): {status_code}",
            )
        return r[int].ok(parsed.status_code)


__all__ = ["RFCProtocolImplementation"]
