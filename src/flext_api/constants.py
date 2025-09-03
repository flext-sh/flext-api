"""FLEXT API Constants - Consolidated HTTP API constants following flext-core patterns.

Single FlextApiConstants class extending FlextConstants with hierarchical HTTP-specific
constants organized by domain following Python 3.13+ type annotations and immutable
Final values for type-safe constant access throughout the API system.

Architecture Hierarchy:
    FlextApiConstants(FlextConstants) - Single consolidated class containing:
        - HTTP Protocol Constants: Timeouts, headers, user agents, content types
        - Status Code Constants: Complete HTTP status code definitions
        - Client Configuration: Retry policies, connection pools, default values
        - Validation Constants: Size limits, format constraints, security settings
        - Cache Configuration: TTL values, size limits, storage settings
        - Plugin System Constants: Priority levels, timeout values, thresholds
        - API Response Constants: Standard response formats and structures
        - Error Code Constants: HTTP error codes and diagnostic information

Python 3.13+ Features:
    - Final type annotations for immutable constants
    - Type-safe constant access with compile-time checking
    - Hierarchical nested class organization
    - Integration with discriminated union patterns
    - Enhanced enum support with StrEnum base classes

Integration with flext-core:
    - Extends FlextConstants for unified constant system
    - Uses FlextConstants base patterns and organization
    - Follows hierarchical domain organization principles
    - Maintains consistency with flext-core constant naming
    - Supports flext-core configuration and validation patterns

Design Principles:
    - Single Point of Truth: All HTTP constants in one location
    - Type Safety: Final annotations prevent modification
    - Hierarchical Organization: Domain-based constant grouping
    - No Magic Numbers: All values explicitly defined and documented
    - Immutable Values: Constants cannot be changed at runtime
    - Clear Naming: Self-documenting constant names and structure

Usage Examples:
    HTTP protocol constants:
    >>> timeout = FlextApiConstants.Http.DEFAULT_TIMEOUT  # 30 seconds
    >>> user_agent = FlextApiConstants.Http.USER_AGENT  # "FlextAPI/1.0"
    >>> max_redirects = FlextApiConstants.Http.MAX_REDIRECTS  # 5

    Status code constants:
    >>> success = FlextApiConstants.HttpStatus.OK  # 200
    >>> not_found = FlextApiConstants.HttpStatus.NOT_FOUND  # 404
    >>> server_error = FlextApiConstants.HttpStatus.INTERNAL_SERVER_ERROR  # 500

    Client configuration constants:
    >>> max_retries = FlextApiConstants.Client.DEFAULT_MAX_RETRIES  # 3
    >>> backoff = FlextApiConstants.Client.RETRY_BACKOFF  # 2.0
    >>> pool_size = FlextApiConstants.Client.CONNECTION_POOL_SIZE  # 100

    Validation constants:
    >>> max_url_len = FlextApiConstants.HttpValidation.MAX_URL_LENGTH  # 2048
    >>> max_body_size = FlextApiConstants.HttpValidation.MAX_BODY_SIZE  # 10MB
    >>> timeout_limit = FlextApiConstants.HttpValidation.MAX_TIMEOUT  # 300 seconds

Integration:
    Seamlessly integrates with flext-core foundation:
    - Uses FlextConstants as base class for consistency
    - Follows flext-core hierarchical organization patterns
    - Maintains compatibility with flext-core configuration system
    - Supports flext-core validation and type checking
    - Extends flext-core constants without conflicts or duplication

Note:
    This is the ONLY constants class in this module following strict
    single-class-per-module pattern. All HTTP-specific constants are
    organized hierarchically within this unified class structure.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import Final

from flext_core import FlextConstants


class FlextApiConstants(FlextConstants):
    """Single hierarchical constants class for all FLEXT API constants.

    Organized by domain with type-safe Final annotations and comprehensive
    HTTP API constants for client configuration, status codes, and validation limits.
    """

    class Http:
        """HTTP protocol constants and defaults."""

        DEFAULT_TIMEOUT: Final[int] = 30
        MAX_REDIRECTS: Final[int] = 5
        USER_AGENT: Final[str] = "FlextApi/0.9.0"
        CONTENT_TYPE_JSON: Final[str] = "application/json"
        CONTENT_TYPE_FORM: Final[str] = "application/x-www-form-urlencoded"
        CONTENT_TYPE_TEXT: Final[str] = "text/plain"
        DEFAULT_CHARSET: Final[str] = "utf-8"

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

    class Validation:
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
        RETRY_BACKOFF: Final[float] = 2.0
        CONNECTION_POOL_SIZE: Final[int] = 100
        DEFAULT_HEADERS: Final[dict[str, str]] = {
            "User-Agent": "FlextApi/0.9.0",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    class HttpValidation:
        """Request/response validation constants."""

        MAX_URL_LENGTH: Final[int] = 2048
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

    class Endpoints:
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


__all__ = [
    "FlextApiConstants",
]
