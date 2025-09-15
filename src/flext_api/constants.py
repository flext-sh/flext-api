"""FLEXT API Constants - Streamlined HTTP constants using flext-core foundation.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from enum import StrEnum
from typing import ClassVar

from flext_core import FlextConstants


class FlextApiConstants:
    """Streamlined HTTP constants - maximum flext-core reuse, minimum duplication."""

    # Use flext-core constants directly - NO DUPLICATION
    HTTP_OK = FlextConstants.Web.HTTP_OK  # 200
    MIN_HTTP_STATUS = 100
    MAX_HTTP_STATUS = 599

    # HttpMethods reference - defined properly as class variable
    HttpMethods: type[HttpMethods]

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
    MIN_PORT = 1
    MAX_PORT = 65535

    # Rate limiting constants
    RATE_LIMIT_REQUESTS = 1000
    RATE_LIMIT_WINDOW = 3600

    # Response templates
    SUCCESS_RESPONSE: ClassVar[dict[str, object]] = {
        "status": "success",
        "data": None,
        "error": None,
    }
    ERROR_RESPONSE: ClassVar[dict[str, object]] = {
        "status": "error",
        "data": None,
        "error": None,
    }

    class ResponseTemplates:
        """Response template constants."""

        SUCCESS: ClassVar[dict[str, object]] = {
            "status": "success",
            "data": None,
            "error": None,
        }
        ERROR: ClassVar[dict[str, object]] = {
            "status": "error",
            "data": None,
            "error": None,
        }

    # Client error codes
    CLIENT_ERROR_CODES: ClassVar[set[int]] = {
        400,
        401,
        403,
        404,
        405,
        406,
        407,
        408,
        409,
        410,
        411,
        412,
        413,
        414,
        415,
        416,
        417,
        418,
        421,
        422,
        423,
        424,
        425,
        426,
        428,
        429,
        431,
        451,
    }

    # Server error codes
    SERVER_ERROR_CODES: ClassVar[set[int]] = {
        500,
        501,
        502,
        503,
        504,
        505,
        506,
        507,
        508,
        510,
        511,
    }

    class Client:
        """Client configuration constants."""

        DEFAULT_USER_AGENT = "FlextAPI/0.9.0"
        DEFAULT_TIMEOUT = 30.0
        MAX_RETRIES = 3
        RETRY_BACKOFF_FACTOR = 2.0

    class HttpStatusRanges:
        """HTTP status code ranges."""

        SUCCESS_MIN = 200
        SUCCESS_MAX = 299

    class Limits:
        """Pagination and request limits."""

        MAX_PAGE_SIZE = 1000
        MIN_PAGE_SIZE = 1
        DEFAULT_PAGE_SIZE = 20

    class HttpStatus:
        """HTTP status code constants."""

        MIN_HTTP_STATUS = 100
        MAX_HTTP_STATUS = 599

        # Common HTTP status codes
        OK = 200
        CREATED = 201
        NO_CONTENT = 204
        BAD_REQUEST = 400
        UNAUTHORIZED = 401
        FORBIDDEN = 403
        NOT_FOUND = 404
        INTERNAL_SERVER_ERROR = 500

    class HttpValidation:
        """HTTP validation constants."""

        MAX_HOSTNAME_LENGTH = 253
        MAX_URL_LENGTH = 2048
        MIN_PORT = 1
        MAX_PORT = 65535

    class Pagination:
        """Pagination constants."""

        DEFAULT_PAGE_SIZE = 20
        MAX_PAGE_SIZE = 1000
        MIN_PAGE_SIZE = 1


class HttpMethods(StrEnum):
    """HTTP methods - using Python 3.13+ StrEnum."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"
    TRACE = "TRACE"
    CONNECT = "CONNECT"
    # WebDAV methods
    PROPFIND = "PROPFIND"
    COPY = "COPY"
    MOVE = "MOVE"
    LOCK = "LOCK"


class ClientStatus(StrEnum):
    """Client status enum."""

    IDLE = "idle"
    ACTIVE = "active"
    DISCONNECTED = "disconnected"


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


class FlextApiEndpoints:
    """API endpoint constants following FLEXT patterns."""

    # Base paths
    API_V1 = "/api/v1"
    HEALTH = "/health"
    METRICS = "/metrics"
    DOCS = "/docs"

    # Authentication endpoints
    AUTH_LOGIN = "/api/v1/auth/login"
    AUTH_LOGOUT = "/api/v1/auth/logout"
    AUTH_REFRESH = "/api/v1/auth/refresh"
    AUTH_VERIFY = "/api/v1/auth/verify"

    # Pipeline endpoints
    PIPELINES = "/api/v1/pipelines"
    PIPELINE_RUN = "/api/v1/pipelines/{pipeline_id}/run"
    PIPELINE_STATUS = "/api/v1/pipelines/{pipeline_id}/status"
    PIPELINE_LOGS = "/api/v1/pipelines/{pipeline_id}/logs"

    # Plugin endpoints
    PLUGINS = "/api/v1/plugins"
    PLUGIN_INSTALL = "/api/v1/plugins/install"
    PLUGIN_UNINSTALL = "/api/v1/plugins/{plugin_id}/uninstall"
    PLUGIN_CONFIG = "/api/v1/plugins/{plugin_id}/config"


class FlextApiFieldType:
    """API field type constants following FLEXT patterns."""

    # Authentication fields
    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"

    # Configuration fields
    PIPELINE_CONFIG = "pipeline_config"
    PLUGIN_CONFIG = "plugin_config"

    # User fields
    USER_ROLE = "user_role"

    # Request/Response fields
    ENDPOINT_PATH = "endpoint_path"
    HTTP_METHOD = "http_method"
    RESPONSE_FORMAT = "response_format"
    REQUEST_ID = "request_id"


class FlextApiStatus:
    """API status constants following FLEXT patterns."""

    # Request status
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

    # Service status
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    MAINTENANCE = "maintenance"

    # Pipeline status
    PIPELINE_IDLE = "idle"
    PIPELINE_RUNNING = "running"
    PIPELINE_SUCCESS = "success"
    PIPELINE_ERROR = "error"
    PIPELINE_TIMEOUT = "timeout"

    # Plugin status
    PLUGIN_LOADED = "loaded"
    PLUGIN_ACTIVE = "active"
    PLUGIN_INACTIVE = "inactive"
    PLUGIN_ERROR = "error"


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
    "ClientStatus",
    "FlextApiConstants",
    "FlextApiEndpoints",
    "FlextApiFieldType",
    "FlextApiStatus",
    "HttpMethods",
    "get_default_headers",
    "is_client_error_status",
    "is_server_error_status",
    "is_success_status",
    "is_valid_http_status",
    "validate_configuration",
]

# Set HttpMethods reference after class definition
FlextApiConstants.HttpMethods = HttpMethods
