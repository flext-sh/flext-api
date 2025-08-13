"""Constants for FLEXT API module.

This module defines centralized constants following the FlextConstants pattern
from flext-core, extending it with API-specific constants.
"""

from __future__ import annotations

from flext_core.constants import FlextConstants


class FlextApiConstants(FlextConstants):
    """Central container for API-specific constants.

    Follows the same pattern as FlextConstants from flext-core,
    organizing constants into logical categories with type safety.
    """

    class HTTP:
        """HTTP protocol constants."""

        # Status Code Ranges
        SUCCESS_MIN = 200
        SUCCESS_MAX = 300
        CLIENT_ERROR_MIN = 400
        CLIENT_ERROR_MAX = 500
        SERVER_ERROR_MIN = 500
        SERVER_ERROR_MAX = 600

        # Common Status Codes
        OK = 200
        CREATED = 201
        NO_CONTENT = 204
        BAD_REQUEST = 400
        UNAUTHORIZED = 401
        FORBIDDEN = 403
        NOT_FOUND = 404
        INTERNAL_SERVER_ERROR = 500
        SERVICE_UNAVAILABLE = 503

        # Headers
        CONTENT_TYPE = "Content-Type"
        AUTHORIZATION = "Authorization"
        USER_AGENT = "User-Agent"
        ACCEPT = "Accept"

    class ContentTypes:
        """Standard HTTP content types."""

        JSON = "application/json"
        HTML = "text/html"

    class Config:
        """API configuration defaults."""

        # Timeouts
        DEFAULT_TIMEOUT = FlextConstants.Defaults.TIMEOUT
        CONNECTION_TIMEOUT = FlextConstants.Defaults.CONNECTION_TIMEOUT
        READ_TIMEOUT = FlextConstants.Platform.HTTP_READ_TIMEOUT

        # Retries
        DEFAULT_MAX_RETRIES = 3
        RETRY_BACKOFF_FACTOR = 2.0
        RETRY_MAX_WAIT = 60

        # Pagination
        DEFAULT_PAGE_SIZE = 50
        MAX_PAGE_SIZE = 1000
        DEFAULT_BATCH_SIZE = 100

    class RateLimit:
        """Rate limiting configuration."""

        DEFAULT_RATE_LIMIT = 100  # requests per minute
        RATE_LIMIT_WINDOW = 60  # seconds
        BURST_SIZE = 10  # additional requests allowed in burst

    class Cache:
        """Cache configuration."""

        DEFAULT_TTL = 300  # 5 minutes
        MAX_SIZE = 1000
        CLEANUP_INTERVAL = 600  # 10 minutes

    class Validation:
        """Validation limits and constraints."""

        MAX_REQUEST_SIZE = 10485760  # 10MB
        MAX_RESPONSE_SIZE = 52428800  # 50MB
        MIN_PORT = 1
        MAX_PORT = 65535
        MAX_URL_LENGTH = 2048
        MAX_HEADER_SIZE = 8192
        MAX_ERROR_VALUE_LENGTH = 100  # Truncate error values for security

    class Auth:
        """Authentication and token constants."""

        JWT_PARTS_COUNT = 3  # JWT has 3 parts: header.payload.signature
        JWT_SEPARATOR_COUNT = 2  # JWT has 2 dots separating 3 parts
        MIN_TOKEN_LENGTH = 16  # Minimum viable token length

    class Connection:
        """Connection pool settings."""

        POOL_SIZE = 10
        MAX_CONNECTIONS = 100
        KEEP_ALIVE_TIMEOUT = 120  # seconds
        IDLE_TIMEOUT = 300  # seconds

    class Performance:
        """Performance monitoring thresholds."""

        SLOW_REQUEST_THRESHOLD = 3.0  # seconds
        CRITICAL_LATENCY_THRESHOLD = 10.0  # seconds
        MONITORING_SAMPLE_RATE = 0.1  # 10% sampling
