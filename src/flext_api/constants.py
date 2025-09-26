"""Constants and enumerations for flext-api domain.

All constant values, literals, and enums are centralized here following FLEXT standards.
Only constants and enums - no functions or classes with behavior.
"""

from __future__ import annotations

from typing import ClassVar

from flext_core import FlextConstants


class FlextApiConstants(FlextConstants):
    """API-specific constants extending flext-core FlextConstants."""

    # Client configuration
    DEFAULT_TIMEOUT: ClassVar[int] = FlextConstants.Network.DEFAULT_TIMEOUT
    DEFAULT_MAX_RETRIES: ClassVar[int] = FlextConstants.Reliability.MAX_RETRY_ATTEMPTS
    DEFAULT_BASE_URL: ClassVar[str] = (
        f"http://{FlextConstants.Platform.DEFAULT_HOST}:{FlextConstants.Platform.FLEXT_API_PORT}"
    )
    API_VERSION: ClassVar[str] = "v1"

    # Environment-specific timeouts
    PRODUCTION_TIMEOUT: ClassVar[int] = FlextConstants.Network.DEFAULT_TIMEOUT
    DEVELOPMENT_TIMEOUT: ClassVar[int] = FlextConstants.Network.DEFAULT_TIMEOUT * 2
    TESTING_TIMEOUT: ClassVar[int] = FlextConstants.Network.DEFAULT_TIMEOUT // 3
    MONITORING_TIMEOUT: ClassVar[int] = FlextConstants.Network.DEFAULT_TIMEOUT // 6

    # Pagination constants
    DEFAULT_PAGE_SIZE: ClassVar[int] = 20
    MIN_PAGE_SIZE: ClassVar[int] = 1
    MAX_PAGE_SIZE: ClassVar[int] = 1000

    # HTTP status codes
    HTTP_STATUS_MIN: ClassVar[int] = 100
    HTTP_STATUS_MAX: ClassVar[int] = 599

    # HTTP status code ranges
    HTTP_INFORMATIONAL_MIN: ClassVar[int] = 100
    HTTP_INFORMATIONAL_MAX: ClassVar[int] = 199
    HTTP_SUCCESS_MIN: ClassVar[int] = 200
    HTTP_SUCCESS_MAX: ClassVar[int] = 299
    HTTP_REDIRECTION_MIN: ClassVar[int] = 300
    HTTP_REDIRECTION_MAX: ClassVar[int] = 399
    HTTP_CLIENT_ERROR_MIN: ClassVar[int] = 400
    HTTP_CLIENT_ERROR_MAX: ClassVar[int] = 499
    HTTP_SERVER_ERROR_MIN: ClassVar[int] = 500
    HTTP_SERVER_ERROR_MAX: ClassVar[int] = 599

    # Common HTTP status codes
    HTTP_OK: ClassVar[int] = 200
    HTTP_CREATED: ClassVar[int] = 201
    HTTP_BAD_REQUEST: ClassVar[int] = 400
    HTTP_NOT_FOUND: ClassVar[int] = 404
    HTTP_INTERNAL_SERVER_ERROR: ClassVar[int] = 500
    SUCCESS_RESPONSE_TEMPLATE: ClassVar[dict[str, str | dict[str, object]]] = {
        "status": "success",
        "data": {},
    }
    ERROR_RESPONSE_TEMPLATE: ClassVar[dict[str, str | dict[str, object]]] = {
        "status": "error",
        "data": {},
    }

    # Common HTTP headers
    AUTHORIZATION_HEADER: ClassVar[str] = "Authorization"
    USER_AGENT_HEADER: ClassVar[str] = "User-Agent"
    CONTENT_TYPE_HEADER: ClassVar[str] = "Content-Type"
    ACCEPT_HEADER: ClassVar[str] = "Accept"

    # Default header values
    DEFAULT_USER_AGENT: ClassVar[str] = "FlextAPI/0.9.0"
    DEFAULT_CONTENT_TYPE: ClassVar[str] = "application/json"
    DEFAULT_ACCEPT: ClassVar[str] = "application/json"

    # Timeout constants
    MIN_TIMEOUT: ClassVar[float] = 0.0
    MAX_TIMEOUT: ClassVar[float] = 300.0

    # Retry constants
    MIN_RETRIES: ClassVar[int] = 0
    MAX_RETRIES: ClassVar[int] = 10
    DEFAULT_RETRIES: ClassVar[int] = 3

    # URL validation
    MAX_URL_LENGTH: ClassVar[int] = 2048
    MAX_HOSTNAME_LENGTH: ClassVar[int] = 253  # RFC 1035 max hostname length
    MAX_PORT: ClassVar[int] = 65535


__all__ = ["FlextApiConstants"]
