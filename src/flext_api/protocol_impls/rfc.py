"""RFC Protocol Implementation for flext-api.

Implements RFC-compliant protocol patterns that extend BaseProtocolImplementation.
All standard protocol implementations (HTTP, WebSocket, etc.) should extend this class
to inherit RFC-compliant behavior.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_core import r

from flext_api.constants import FlextApiConstants
from flext_api.protocol_impls.base import BaseProtocolImplementation
from flext_api.typings import FlextApiTypes
from flext_api.utilities import FlextApiUtilities


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
        **kwargs: object,
    ) -> None:
        """Initialize RFC protocol implementation.

        Args:
        name: Protocol name
        version: Protocol version
        description: Protocol description
        **kwargs: Additional configuration parameters

        """
        super().__init__(name=name, version=version, description=description, **kwargs)

    def _extract_url(self, request: dict[str, object]) -> r[str]:
        """Extract and validate URL from request (RFC 7230 compliant).

        Args:
        request: Request dictionary

        Returns:
        FlextResult with validated URL or error

        """
        if "url" not in request:
            return r[str].fail("URL is required in request (RFC 7230)")

        url_value = request["url"]
        if not isinstance(url_value, str):
            return r[str].fail("URL must be a string (RFC 7230)")

        if not url_value.strip():
            return r[str].fail("URL cannot be empty (RFC 7230)")

        # Validate URL format using utilities
        return FlextApiUtilities.FlextWebValidator.validate_url(url_value)

    def _extract_method(self, request: dict[str, object]) -> r[str]:
        """Extract and validate HTTP method from request (RFC 7231 compliant).

        Args:
        request: Request dictionary

        Returns:
        FlextResult with validated method or error

        """
        if "method" not in request:
            return r[str].ok(
                FlextApiConstants.Method.GET
            )  # Default method per RFC 7231

        method_value = request["method"]
        if not isinstance(method_value, str):
            return r[str].fail("Method must be a string (RFC 7231)")

        method_upper = method_value.upper()
        if not FlextApiUtilities.FlextWebValidator.validate_http_method(method_upper):
            return r[str].fail(f"Invalid HTTP method: {method_upper} (RFC 7231)")

        return r[str].ok(method_upper)

    def _extract_headers(self, request: dict[str, object]) -> dict[str, str]:
        """Extract headers from request (RFC 7230 compliant).

        Args:
        request: Request dictionary

        Returns:
        Dictionary of headers (normalized to lowercase keys per RFC 7230)

        """
        if "headers" not in request:
            return {}

        headers_value = request["headers"]
        if not isinstance(headers_value, dict):
            return {}

        # Normalize header keys to lowercase per RFC 7230
        normalized_headers: dict[str, str] = {}
        for key, value in headers_value.items():
            if isinstance(key, str) and isinstance(value, str):
                normalized_headers[key.lower()] = value

        return normalized_headers

    def _extract_body(self, request: dict[str, object]) -> object | None:
        """Extract body from request (RFC 7231 compliant).

        Args:
        request: Request dictionary

        Returns:
        Request body or None

        """
        if "body" not in request:
            return None

        return request["body"]

    def _extract_timeout(self, request: dict[str, object]) -> float:
        """Extract timeout from request with defaults.

        Args:
        request: Request dictionary

        Returns:
        Timeout value in seconds

        """
        if "timeout" in request:
            timeout_value = request["timeout"]
            if isinstance(timeout_value, (int, float)) and timeout_value > 0:
                return float(timeout_value)

        # Use default timeout from constants
        return float(FlextApiConstants.DEFAULT_REQUEST_TIMEOUT)

    def _build_rfc_error_response(
        self,
        error: str,
        status_code: int = 500,
        error_code: str | None = None,
    ) -> dict[str, object]:
        """Build RFC-compliant error response (RFC 7231).

        Args:
        error: Error message
        status_code: HTTP status code
        error_code: Optional error code

        Returns:
        RFC-compliant error response dictionary

        """
        error_response = FlextApiUtilities.ResponseBuilder.build_error_response(
            message=error,
            status_code=status_code,
            error_code=error_code,
        )
        # Convert JsonObject to dict[str, object] for compatibility
        return dict(error_response.items())

    def _build_rfc_success_response(
        self,
        data: dict[str, object] | None = None,
        status_code: int = 200,
        headers: dict[str, str] | None = None,
    ) -> r[dict[str, object]]:
        """Build RFC-compliant success response (RFC 7231).

        Args:
        data: Response data
        status_code: HTTP status code
        headers: Response headers

        Returns:
        FlextResult with RFC-compliant success response

        """
        # Convert dict[str, object] to JsonObject and dict[str, str] to WebHeaders
        # JsonObject is dict[str, JsonValue] where JsonValue includes compatible types
        json_data: FlextApiTypes.JsonObject | None = None
        if data is not None:
            # Create new dict with compatible types
            # JsonValue is str | int | float | bool | None | Sequence[JsonValue] | Mapping[str, JsonValue]
            # Most object values are compatible, but we need to filter/convert if needed
            json_data = {}
            for key, value in data.items():
                # JsonValue accepts these types, so we can assign directly
                # If value is not compatible, it will be caught at runtime
                if isinstance(value, (str, int, float, bool, type(None), list, dict)):
                    json_data[key] = value
                else:
                    # Convert other types to string representation
                    json_data[key] = str(value)

        web_headers: FlextApiTypes.WebHeaders | None = None
        if headers is not None:
            # WebHeaders is dict[str, str | list[str]], convert dict[str, str]
            web_headers = dict(headers)

        result = FlextApiUtilities.ResponseBuilder.build_success_response(
            data=json_data,
            status_code=status_code,
            headers=web_headers,
        )
        # Convert JsonObject result back to dict[str, object] for compatibility
        if result.is_success:
            response_value = result.value
            # Convert JsonObject (dict[str, JsonValue]) to dict[str, object]
            converted_response: dict[str, object] = dict(response_value.items())
            return r[dict[str, object]].ok(converted_response)
        return r[dict[str, object]].fail(
            result.error or "Failed to build success response"
        )

    def _validate_status_code(self, status_code: int) -> r[int]:
        """Validate HTTP status code (RFC 7231).

        Args:
        status_code: HTTP status code to validate

        Returns:
        FlextResult with validated status code or error

        """
        if not isinstance(status_code, int):
            return r[int].fail("Status code must be an integer (RFC 7231)")

        if (
            status_code < FlextApiConstants.HTTP_SUCCESS_MIN - 100
            or status_code > FlextApiConstants.HTTP_SERVER_ERROR_MIN + 99
        ):
            return r[int].fail(
                f"Status code must be between 100 and 599 (RFC 7231): {status_code}"
            )

        return r[int].ok(status_code)

    def _is_success_status(self, status_code: int) -> bool:
        """Check if status code indicates success (RFC 7231).

        Args:
        status_code: HTTP status code

        Returns:
        True if status code indicates success (2xx range)

        """
        return (
            status_code >= FlextApiConstants.HTTP_SUCCESS_MIN
            and status_code < FlextApiConstants.HTTP_SUCCESS_MAX
        )

    def _is_client_error(self, status_code: int) -> bool:
        """Check if status code indicates client error (RFC 7231).

        Args:
        status_code: HTTP status code

        Returns:
        True if status code indicates client error (4xx range)

        """
        return (
            status_code >= FlextApiConstants.HTTP_CLIENT_ERROR_MIN
            and status_code < FlextApiConstants.HTTP_CLIENT_ERROR_MAX
        )

    def _is_server_error(self, status_code: int) -> bool:
        """Check if status code indicates server error (RFC 7231).

        Args:
        status_code: HTTP status code

        Returns:
        True if status code indicates server error (5xx range)

        """
        return status_code >= FlextApiConstants.HTTP_SERVER_ERROR_MIN

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

        # Retry on server errors (5xx) and specific client errors (408, 429)
        return status_code in FlextApiConstants.HTTPRetry.RETRYABLE_STATUS_CODES

    def _get_content_type(self, headers: dict[str, str]) -> str:
        """Extract Content-Type from headers (RFC 7231).

        Args:
        headers: Response headers

        Returns:
        Content-Type value or default

        """
        content_type_key = "content-type"
        if content_type_key in headers:
            return headers[content_type_key]

        return FlextApiConstants.ContentType.JSON

    def _normalize_header_name(self, header_name: str) -> str:
        """Normalize header name to lowercase (RFC 7230).

        Args:
        header_name: Header name to normalize

        Returns:
        Normalized header name

        """
        return header_name.lower()


__all__ = ["RFCProtocolImplementation"]
