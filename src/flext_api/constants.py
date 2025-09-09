"""FLEXT API Constants - Consolidated HTTP API constants following flext-core patterns.

Single FlextApiConstants class extending FlextConstants with hierarchical HTTP-specific
constants organized by domain following Python 3.13+ type annotations and immutable
Final values for type-safe constant access throughout the API system.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from enum import StrEnum
from typing import Final

from flext_core import FlextConstants

from flext_api.typings import FlextApiTypes


class FlextApiConstants(FlextConstants):
    """Single hierarchical constants class for all FLEXT API constants.

    Organized by domain with type-safe Final annotations and comprehensive
    HTTP API constants for client configuration, status codes, and validation limits.
    """

    class Http:
        """HTTP protocol constants and defaults.

        Retains simple string constants for backward compatibility while
        StrEnum variants (UrlScheme / HttpMethods) provide type-safe usage.
        """

        DEFAULT_TIMEOUT: Final[int] = 30
        MAX_REDIRECTS: Final[int] = 5
        USER_AGENT: Final[str] = "FlextApi/0.9.0"
        CONTENT_TYPE_JSON: Final[str] = "application/json"
        CONTENT_TYPE_FORM: Final[str] = "application/x-www-form-urlencoded"
        CONTENT_TYPE_TEXT: Final[str] = "text/plain"
        DEFAULT_CHARSET: Final[str] = "utf-8"

    class UrlScheme(StrEnum):
        """StrEnum for URL schemes (Python 3.11+)."""

        HTTP = "http"
        HTTPS = "https"

    class HttpMethods(StrEnum):
        """StrEnum for HTTP methods (type-safe, still str-compatible)."""

        GET = "GET"
        POST = "POST"
        PUT = "PUT"
        DELETE = "DELETE"
        PATCH = "PATCH"
        HEAD = "HEAD"
        OPTIONS = "OPTIONS"
        TRACE = "TRACE"
        CONNECT = "CONNECT"

        @classmethod
        def all(cls) -> tuple[FlextApiConstants.HttpMethods, ...]:
            """Return all enum members as a tuple (used in runtime contexts)."""
            return tuple(cls)

    class HttpStatus:
        """HTTP status code constants."""

        # Informational codes
        CONTINUE: Final[int] = 100

        # Success codes
        OK: Final[int] = 200
        CREATED: Final[int] = 201
        ACCEPTED: Final[int] = 202
        NO_CONTENT: Final[int] = 204

        # Redirect codes
        MULTIPLE_CHOICES: Final[int] = 300
        MOVED_PERMANENTLY: Final[int] = 301
        FOUND: Final[int] = 302
        NOT_MODIFIED: Final[int] = 304

        # Client error codes
        BAD_REQUEST: Final[int] = 400
        UNAUTHORIZED: Final[int] = 401
        FORBIDDEN: Final[int] = 403
        NOT_FOUND: Final[int] = 404
        METHOD_NOT_ALLOWED: Final[int] = 405
        CONFLICT: Final[int] = 409
        TOO_MANY_REQUESTS: Final[int] = 429

        # Server error codes
        INTERNAL_SERVER_ERROR: Final[int] = 500
        NOT_IMPLEMENTED: Final[int] = 501
        BAD_GATEWAY: Final[int] = 502
        SERVICE_UNAVAILABLE: Final[int] = 503
        GATEWAY_TIMEOUT: Final[int] = 504

        # Network timeout error (custom)
        NETWORK_CONNECT_TIMEOUT_ERROR: Final[int] = 599

        # Maximum valid HTTP status code
        MAX_STATUS_CODE: Final[int] = 600

        # Status code ranges (RFC 7231)
        INFORMATIONAL_MIN: Final[int] = 100
        INFORMATIONAL_MAX: Final[int] = 199
        SUCCESS_MIN: Final[int] = 200
        SUCCESS_MAX: Final[int] = 299
        REDIRECTION_MIN: Final[int] = 300
        REDIRECTION_MAX: Final[int] = 399
        CLIENT_ERROR_MIN: Final[int] = 400
        CLIENT_ERROR_MAX: Final[int] = 499
        SERVER_ERROR_MIN: Final[int] = 500
        SERVER_ERROR_MAX: Final[int] = 599

    class ApiValidation:
        """Validation and limit constants."""

        # HTTP status ranges
        CLIENT_ERROR_MIN: Final[int] = 400
        SERVER_ERROR_MIN: Final[int] = 500

        # Timeout limits
        MAX_TIMEOUT: Final[float] = 3600.0
        MIN_TIMEOUT: Final[float] = 0.1

        # Retry limits
        MAX_RETRIES: Final[int] = 10

        # Name length limits
        MAX_NAME_LENGTH: Final[int] = 50
        MIN_NAME_LENGTH: Final[int] = 1

    class Client:
        """HTTP client configuration constants."""

        DEFAULT_MAX_RETRIES: Final[int] = 3
        MAX_RETRIES: Final[int] = 3  # Alias expected by tests
        RETRY_BACKOFF: Final[float] = 2.0
        RETRY_BACKOFF_FACTOR: Final[float] = 2.0  # Alias expected by tests
        CONNECTION_POOL_SIZE: Final[int] = 100
        DEFAULT_TIMEOUT: Final[int] = 30  # Expected by tests
        DEFAULT_USER_AGENT: Final[str] = "FlextAPI/0.9.0"  # Expected by tests
        DEFAULT_HEADERS: Final[FlextApiTypes.HttpHeaders] = {
            "User-Agent": "FlextAPI/0.9.0",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    class HttpValidation:
        """Request/response validation constants."""

        MAX_URL_LENGTH: Final[int] = 2048
        MAX_HOSTNAME_LENGTH: Final[int] = 253  # RFC 1035 limit
        MAX_PORT_NUMBER: Final[int] = 65535
        MIN_PORT_NUMBER: Final[int] = 1
        MAX_HEADER_SIZE: Final[int] = 8192
        MAX_BODY_SIZE: Final[int] = 10485760  # 10MB
        MIN_TIMEOUT: Final[float] = 0.1
        MAX_TIMEOUT: Final[float] = 300.0

    class HttpCache:
        """HTTP caching constants."""

        DEFAULT_TTL: Final[int] = 300  # 5 minutes
        MAX_CACHE_SIZE: Final[int] = 1000
        CACHE_CONTROL_NO_CACHE: Final[str] = "no-cache"
        CACHE_CONTROL_MAX_AGE: Final[str] = "max-age"

    class Security:
        """HTTP security and CORS constants."""

        CORS_MAX_AGE: Final[int] = 3600  # 1 hour
        HSTS_MAX_AGE: Final[int] = 31536000  # 1 year
        CSP_DEFAULT: Final[str] = "default-src 'self'"

    class Server:
        """HTTP server configuration constants."""

        MAX_WORKERS: Final[int] = 32
        DEFAULT_HOST: Final[str] = "127.0.0.1"
        DEFAULT_PORT: Final[int] = 8000

    class Pagination:
        """Pagination constants."""

        DEFAULT_PAGE_SIZE: Final[int] = 50
        MAX_PAGE_SIZE: Final[int] = 1000

    class HttpErrors:
        """HTTP error code constants."""

        NETWORK_ERROR: Final[str] = "NETWORK_ERROR"
        TIMEOUT_ERROR: Final[str] = "TIMEOUT_ERROR"
        CONNECTION_ERROR: Final[str] = "CONNECTION_ERROR"
        HTTP_ERROR: Final[str] = "HTTP_ERROR"
        VALIDATION_ERROR: Final[str] = "VALIDATION_ERROR"
        AUTHENTICATION_ERROR: Final[str] = "AUTHENTICATION_ERROR"
        AUTHORIZATION_ERROR: Final[str] = "AUTHORIZATION_ERROR"
        RATE_LIMIT_ERROR: Final[str] = "RATE_LIMIT_ERROR"

    class FieldTypes:
        """API-specific field type constants."""

        API_KEY: Final[str] = "api_key"
        BEARER_TOKEN: Final[str] = "bearer_token"
        PIPELINE_CONFIG: Final[str] = "pipeline_config"
        PLUGIN_CONFIG: Final[str] = "plugin_config"
        USER_ROLE: Final[str] = "user_role"
        ENDPOINT_PATH: Final[str] = "endpoint_path"
        HTTP_METHOD: Final[str] = "http_method"
        RESPONSE_FORMAT: Final[str] = "response_format"
        REQUEST_ID: Final[str] = "request_id"

    class RequestStatus:
        """API request status constants."""

        PENDING: Final[str] = "pending"
        PROCESSING: Final[str] = "processing"
        COMPLETED: Final[str] = "completed"

    class ApiEndpoints:
        """API endpoint path constants."""

        # Base paths
        API_V1: Final[str] = "/api/v1"
        HEALTH: Final[str] = "/health"
        METRICS: Final[str] = "/metrics"
        DOCS: Final[str] = "/docs"

        # Authentication endpoints
        AUTH_LOGIN: Final[str] = "/api/v1/auth/login"
        AUTH_LOGOUT: Final[str] = "/api/v1/auth/logout"
        AUTH_REFRESH: Final[str] = "/api/v1/auth/refresh"
        AUTH_VERIFY: Final[str] = "/api/v1/auth/verify"

        # Pipeline endpoints
        PIPELINES: Final[str] = "/api/v1/pipelines"
        PIPELINE_RUN: Final[str] = "/api/v1/pipelines/{pipeline_id}/run"
        PIPELINE_STATUS: Final[str] = "/api/v1/pipelines/{pipeline_id}/status"
        PIPELINE_LOGS: Final[str] = "/api/v1/pipelines/{pipeline_id}/logs"

        # Plugin endpoints
        PLUGINS: Final[str] = "/api/v1/plugins"
        PLUGIN_INSTALL: Final[str] = "/api/v1/plugins/install"
        PLUGIN_UNINSTALL: Final[str] = "/api/v1/plugins/{plugin_id}/uninstall"
        PLUGIN_CONFIG: Final[str] = "/api/v1/plugins/{plugin_id}/config"

    class ApiStatus:
        """API operation status constants (distinct from HTTP status codes)."""

        # Request lifecycle statuses
        PENDING: Final[str] = "pending"
        PROCESSING: Final[str] = "processing"
        COMPLETED: Final[str] = "completed"
        FAILED: Final[str] = "failed"
        CANCELLED: Final[str] = "cancelled"

        # Service health statuses
        HEALTHY: Final[str] = "healthy"
        DEGRADED: Final[str] = "degraded"
        UNHEALTHY: Final[str] = "unhealthy"
        MAINTENANCE: Final[str] = "maintenance"

        # Pipeline statuses
        PIPELINE_IDLE: Final[str] = "idle"
        PIPELINE_RUNNING: Final[str] = "running"
        PIPELINE_SUCCESS: Final[str] = "success"
        PIPELINE_ERROR: Final[str] = "error"
        PIPELINE_TIMEOUT: Final[str] = "timeout"

        # Plugin statuses
        PLUGIN_LOADED: Final[str] = "loaded"
        PLUGIN_ACTIVE: Final[str] = "active"
        PLUGIN_INACTIVE: Final[str] = "inactive"
        PLUGIN_ERROR: Final[str] = "error"

    class RateLimit:
        """Rate limiting constants."""

        DEFAULT_LIMIT: Final[int] = 100
        DEFAULT_WINDOW: Final[int] = 60
        BURST_LIMIT: Final[int] = 150

    class ResponseTemplates:
        """Standard response templates."""

        SUCCESS_RESPONSE: Final[FlextApiTypes.Core.Dict] = {
            "status": "success",
            "message": "Request completed successfully",
        }
        ERROR_RESPONSE: Final[FlextApiTypes.Core.Dict] = {
            "status": "error",
            "message": "Request failed",
        }

    class HttpStatusRanges:
        """HTTP status code ranges for easy checking."""

        SUCCESS_MIN: Final[int] = 200
        SUCCESS_MAX: Final[int] = 300
        CLIENT_ERROR_MIN: Final[int] = 400
        CLIENT_ERROR_MAX: Final[int] = 500
        SERVER_ERROR_MIN: Final[int] = 500
        SERVER_ERROR_MAX: Final[int] = 600

    # Top-level constants for tests
    RATE_LIMIT_DEFAULT: Final[int] = 100
    RATE_LIMIT_REQUESTS: Final[int] = 1000  # Expected by tests
    RATE_LIMIT_WINDOW: Final[int] = 3600  # Expected by tests
    CLIENT_ERROR_CODES: Final[list[int]] = [400, 401, 403, 404, 405, 409, 429]
    SERVER_ERROR_CODES: Final[list[int]] = [500, 501, 502, 503, 504]
    SUCCESS_RESPONSE: Final[
        dict[str, str | None]
    ] = {  # Expected by tests with data and error fields
        "status": "success",
        "message": "Request completed successfully",
        "data": None,
        "error": None,
    }
    ERROR_RESPONSE: Final[dict[str, str | None]] = {  # Expected by tests
        "status": "error",
        "message": "Request failed",
        "data": None,
        "error": None,  # Test expects error field to be None
    }
    SUCCESS_RESPONSE_TEMPLATE: Final[FlextApiTypes.Core.Dict] = {
        "status": "success",
        "message": "Request completed successfully",
    }


__all__ = [
    "FlextApiConstants",
]
