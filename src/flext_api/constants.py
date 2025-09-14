"""FLEXT API Constants - Streamlined HTTP constants using flext-core foundation.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from enum import StrEnum

from flext_core import FlextConstants


class FlextApiConstants:
    """Streamlined HTTP constants - maximum flext-core reuse, minimum duplication."""

    # Use flext-core constants directly - NO DUPLICATION
    HTTP_OK = FlextConstants.Web.HTTP_OK  # 200
    MIN_HTTP_STATUS = 100
    MAX_HTTP_STATUS = 599

    # HTTP status ranges - simplified
    SUCCESS_START = 200
    SUCCESS_END = 300
    SUCCESS_STATUS_START = 200  # Alias for compatibility
    SUCCESS_STATUS_END = 300  # Alias for compatibility
    CLIENT_ERROR_START = 400
    SERVER_ERROR_START = 500
    SERVER_ERROR_END = 600

    # Defaults - consolidated single values
    DEFAULT_TIMEOUT = 30.0
    DEFAULT_RETRIES = 3
    DEFAULT_BASE_URL = "http://127.0.0.1:8000"
    DEFAULT_USER_AGENT = "FlextAPI/0.9.0"
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 1000
    MAX_PORT = 65535

    class Limits:
        """Pagination and request limits."""

        MAX_PAGE_SIZE = 1000
        MIN_PAGE_SIZE = 1
        DEFAULT_PAGE_SIZE = 20

    class HttpStatus:
        """HTTP status code constants."""

        MIN_HTTP_STATUS = 100
        MAX_HTTP_STATUS = 599


class HttpMethods(StrEnum):
    """HTTP methods - using Python 3.13+ StrEnum."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


# HTTP status codes - flattened, no nested classes
BAD_REQUEST = 400
UNAUTHORIZED = 401
FORBIDDEN = 403
NOT_FOUND = 404
INTERNAL_SERVER_ERROR = 500
SERVICE_UNAVAILABLE = 503

# Content types - flattened
JSON_TYPE = "application/json"
TEXT_TYPE = "text/plain"

# Headers - flattened
CONTENT_TYPE_HEADER = "Content-Type"
AUTHORIZATION_HEADER = "Authorization"
USER_AGENT_HEADER = "User-Agent"

# HTTP Status Code Ranges
HTTP_SUCCESS_MIN = 200
HTTP_SUCCESS_MAX = 299
HTTP_CLIENT_ERROR_MIN = 400
HTTP_CLIENT_ERROR_MAX = 499
HTTP_SERVER_ERROR_MIN = 500
HTTP_SERVER_ERROR_MAX = 599
HTTP_STATUS_MIN = 100
HTTP_STATUS_MAX = 599

# Configuration Validation Constants
MIN_TIMEOUT = 0.1
MAX_TIMEOUT = 300.0
MIN_RETRIES = 0
MAX_RETRIES = 10


# Utility functions for HTTP status checking
def is_success_status(status_code: int) -> bool:
    """Check if status code indicates success."""
    return HTTP_SUCCESS_MIN <= status_code <= HTTP_SUCCESS_MAX


def is_client_error_status(status_code: int) -> bool:
    """Check if status code indicates client error."""
    return HTTP_CLIENT_ERROR_MIN <= status_code <= HTTP_CLIENT_ERROR_MAX


def is_server_error_status(status_code: int) -> bool:
    """Check if status code indicates server error."""
    return HTTP_SERVER_ERROR_MIN <= status_code <= HTTP_SERVER_ERROR_MAX


def is_valid_http_status(status_code: int) -> bool:
    """Check if HTTP status code is valid."""
    return HTTP_STATUS_MIN <= status_code <= HTTP_STATUS_MAX


def get_default_headers() -> dict[str, str]:
    """Get default HTTP headers."""
    return {
        USER_AGENT_HEADER: "FlextAPI/0.9.0",
        CONTENT_TYPE_HEADER: JSON_TYPE,
        "Accept": JSON_TYPE,
    }


def validate_configuration(**config: object) -> list[str]:
    """Validate configuration parameters and return error messages."""
    errors = []

    if "timeout" in config:
        timeout = config["timeout"]
        if isinstance(timeout, (int, float)) and not (
            MIN_TIMEOUT <= float(timeout) <= MAX_TIMEOUT
        ):
            errors.append(f"Invalid timeout: {timeout}")

    if "max_retries" in config:
        retries = config["max_retries"]
        if isinstance(retries, int) and not (MIN_RETRIES <= retries <= MAX_RETRIES):
            errors.append(f"Invalid max_retries: {retries}")

    return errors


__all__ = [
    "AUTHORIZATION_HEADER",
    "BAD_REQUEST",
    "CONTENT_TYPE_HEADER",
    "FORBIDDEN",
    "INTERNAL_SERVER_ERROR",
    "JSON_TYPE",
    "NOT_FOUND",
    "SERVICE_UNAVAILABLE",
    "TEXT_TYPE",
    "UNAUTHORIZED",
    "USER_AGENT_HEADER",
    "FlextApiConstants",
    "HttpMethods",
    "get_default_headers",
    "is_client_error_status",
    "is_server_error_status",
    "is_success_status",
    "is_valid_http_status",
    "validate_configuration",
]
