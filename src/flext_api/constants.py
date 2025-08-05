"""API-specific constants and enumerations.

Constants extending flext-core FlextConstants with HTTP status codes,
API endpoints, field types, operation status values, and configuration
defaults. Provides organized constant groups for consistent API behavior.

Main constant classes:
    - FlextApiConstants: HTTP status groups and response templates
    - FlextApiFieldType: API field type definitions
    - FlextApiStatus: Operation and service status constants
    - FlextApiEndpoints: RESTful API endpoint paths

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import http
from typing import ClassVar

from flext_core.constants import FlextSemanticConstants

# ==============================================================================
# API-SPECIFIC SEMANTIC CONSTANTS - Extending flext-core
# ==============================================================================


class FlextApiSemanticConstants(FlextSemanticConstants):
    """API-specific semantic constants extending FlextSemanticConstants.

    Modern Python 3.13 constants following semantic grouping patterns.
    Extends the FLEXT ecosystem constants with HTTP API specific values
    while maintaining full backward compatibility.
    """

    class Http:
        """HTTP protocol constants."""

        # Status code groups
        SUCCESS_CODES: ClassVar[list[int]] = [
            http.HTTPStatus.OK.value,
            http.HTTPStatus.CREATED.value,
            http.HTTPStatus.ACCEPTED.value,
            http.HTTPStatus.NO_CONTENT.value,
        ]
        CLIENT_ERROR_CODES: ClassVar[list[int]] = [
            http.HTTPStatus.BAD_REQUEST.value,
            http.HTTPStatus.UNAUTHORIZED.value,
            http.HTTPStatus.FORBIDDEN.value,
            http.HTTPStatus.NOT_FOUND.value,
            http.HTTPStatus.UNPROCESSABLE_ENTITY.value,
        ]
        SERVER_ERROR_CODES: ClassVar[list[int]] = [
            http.HTTPStatus.INTERNAL_SERVER_ERROR.value,
            http.HTTPStatus.BAD_GATEWAY.value,
            http.HTTPStatus.SERVICE_UNAVAILABLE.value,
            http.HTTPStatus.GATEWAY_TIMEOUT.value,
        ]

    class Responses:
        """API response format constants."""

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

    class Fields:
        """API-specific field type constants."""

        API_KEY = "api_key"
        BEARER_TOKEN = "bearer_token"  # noqa: S105
        PIPELINE_CONFIG = "pipeline_config"
        PLUGIN_CONFIG = "plugin_config"
        USER_ROLE = "user_role"
        ENDPOINT_PATH = "endpoint_path"
        HTTP_METHOD = "http_method"
        RESPONSE_FORMAT = "response_format"

    class Status:
        """API operation status constants."""

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

    class Endpoints:
        """API endpoint path constants."""

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

    class RateLimit:
        """Rate limiting constants."""

        REQUESTS = 1000
        WINDOW = 3600

    class Validation:
        """API-specific validation patterns."""

        USERNAME_PATTERN = r"^[a-zA-Z0-9_]{3,50}$"
        PIPELINE_NAME_PATTERN = r"^[a-zA-Z0-9_-]{1,100}$"

    class Config:
        """API configuration constants."""

        VERSION = "0.9.0"
        TIMEOUT = 30
        MAX_RETRIES = 3
        CACHE_TTL = 300


class FlextApiConstants(FlextApiSemanticConstants):
    """API-specific constants with backward compatibility.

    Legacy compatibility layer providing both modern semantic access
    and traditional flat constant access patterns for smooth migration.
    """

    # Modern semantic access (Primary API) - direct references
    Http = FlextApiSemanticConstants.Http
    Responses = FlextApiSemanticConstants.Responses
    Fields = FlextApiSemanticConstants.Fields
    Status = FlextApiSemanticConstants.Status
    Endpoints = FlextApiSemanticConstants.Endpoints
    RateLimit = FlextApiSemanticConstants.RateLimit
    Validation = FlextApiSemanticConstants.Validation
    Config = FlextApiSemanticConstants.Config

    # Legacy compatibility - flat access patterns (DEPRECATED - use semantic access)
    SUCCESS_CODES = FlextApiSemanticConstants.Http.SUCCESS_CODES
    CLIENT_ERROR_CODES = FlextApiSemanticConstants.Http.CLIENT_ERROR_CODES
    SERVER_ERROR_CODES = FlextApiSemanticConstants.Http.SERVER_ERROR_CODES
    SUCCESS_RESPONSE = FlextApiSemanticConstants.Responses.SUCCESS_RESPONSE
    ERROR_RESPONSE = FlextApiSemanticConstants.Responses.ERROR_RESPONSE
    USERNAME_PATTERN = FlextApiSemanticConstants.Validation.USERNAME_PATTERN
    PIPELINE_NAME_PATTERN = FlextApiSemanticConstants.Validation.PIPELINE_NAME_PATTERN
    RATE_LIMIT_REQUESTS = FlextApiSemanticConstants.RateLimit.REQUESTS
    RATE_LIMIT_WINDOW = FlextApiSemanticConstants.RateLimit.WINDOW


class FlextApiFieldType:
    """API-specific field types (DEPRECATED - use FlextApiConstants.Fields.*)."""

    API_KEY = FlextApiSemanticConstants.Fields.API_KEY
    BEARER_TOKEN = FlextApiSemanticConstants.Fields.BEARER_TOKEN
    PIPELINE_CONFIG = FlextApiSemanticConstants.Fields.PIPELINE_CONFIG
    PLUGIN_CONFIG = FlextApiSemanticConstants.Fields.PLUGIN_CONFIG
    USER_ROLE = FlextApiSemanticConstants.Fields.USER_ROLE
    ENDPOINT_PATH = FlextApiSemanticConstants.Fields.ENDPOINT_PATH
    HTTP_METHOD = FlextApiSemanticConstants.Fields.HTTP_METHOD
    RESPONSE_FORMAT = FlextApiSemanticConstants.Fields.RESPONSE_FORMAT


class FlextApiStatus:
    """API operation status constants (DEPRECATED - use FlextApiConstants.Status.*)."""

    PENDING = FlextApiSemanticConstants.Status.PENDING
    PROCESSING = FlextApiSemanticConstants.Status.PROCESSING
    COMPLETED = FlextApiSemanticConstants.Status.COMPLETED
    FAILED = FlextApiSemanticConstants.Status.FAILED
    CANCELLED = FlextApiSemanticConstants.Status.CANCELLED
    HEALTHY = FlextApiSemanticConstants.Status.HEALTHY
    DEGRADED = FlextApiSemanticConstants.Status.DEGRADED
    UNHEALTHY = FlextApiSemanticConstants.Status.UNHEALTHY
    MAINTENANCE = FlextApiSemanticConstants.Status.MAINTENANCE
    PIPELINE_IDLE = FlextApiSemanticConstants.Status.PIPELINE_IDLE
    PIPELINE_RUNNING = FlextApiSemanticConstants.Status.PIPELINE_RUNNING
    PIPELINE_SUCCESS = FlextApiSemanticConstants.Status.PIPELINE_SUCCESS
    PIPELINE_ERROR = FlextApiSemanticConstants.Status.PIPELINE_ERROR
    PIPELINE_TIMEOUT = FlextApiSemanticConstants.Status.PIPELINE_TIMEOUT
    PLUGIN_LOADED = FlextApiSemanticConstants.Status.PLUGIN_LOADED
    PLUGIN_ACTIVE = FlextApiSemanticConstants.Status.PLUGIN_ACTIVE
    PLUGIN_INACTIVE = FlextApiSemanticConstants.Status.PLUGIN_INACTIVE
    PLUGIN_ERROR = FlextApiSemanticConstants.Status.PLUGIN_ERROR


class FlextApiEndpoints:
    """API endpoint constants (DEPRECATED - use FlextApiConstants.Endpoints.*)."""

    API_V1 = FlextApiSemanticConstants.Endpoints.API_V1
    HEALTH = FlextApiSemanticConstants.Endpoints.HEALTH
    METRICS = FlextApiSemanticConstants.Endpoints.METRICS
    DOCS = FlextApiSemanticConstants.Endpoints.DOCS
    AUTH_LOGIN = FlextApiSemanticConstants.Endpoints.AUTH_LOGIN
    AUTH_LOGOUT = FlextApiSemanticConstants.Endpoints.AUTH_LOGOUT
    AUTH_REFRESH = FlextApiSemanticConstants.Endpoints.AUTH_REFRESH
    AUTH_VERIFY = FlextApiSemanticConstants.Endpoints.AUTH_VERIFY
    PIPELINES = FlextApiSemanticConstants.Endpoints.PIPELINES
    PIPELINE_RUN = FlextApiSemanticConstants.Endpoints.PIPELINE_RUN
    PIPELINE_STATUS = FlextApiSemanticConstants.Endpoints.PIPELINE_STATUS
    PIPELINE_LOGS = FlextApiSemanticConstants.Endpoints.PIPELINE_LOGS
    PLUGINS = FlextApiSemanticConstants.Endpoints.PLUGINS
    PLUGIN_INSTALL = FlextApiSemanticConstants.Endpoints.PLUGIN_INSTALL
    PLUGIN_UNINSTALL = FlextApiSemanticConstants.Endpoints.PLUGIN_UNINSTALL
    PLUGIN_CONFIG = FlextApiSemanticConstants.Endpoints.PLUGIN_CONFIG


# ==============================================================================
# MODULE-LEVEL CONSTANTS
# ==============================================================================

# API Configuration Constants
FLEXT_API_VERSION = "0.9.0"
FLEXT_API_TIMEOUT = 30
FLEXT_API_MAX_RETRIES = 3
FLEXT_API_CACHE_TTL = 300

# ==============================================================================
# EXPORTS - API-SPECIFIC CONSTANTS
# ==============================================================================

__all__: list[str] = [
    # Module-level constants (Legacy)
    "FLEXT_API_CACHE_TTL",
    "FLEXT_API_MAX_RETRIES",
    "FLEXT_API_TIMEOUT",
    "FLEXT_API_VERSION",
    # Legacy Compatibility (Backward Compatibility)
    "FlextApiConstants",
    "FlextApiEndpoints",
    "FlextApiFieldType",
    # Modern Semantic Constants (Primary API)
    "FlextApiSemanticConstants",
    "FlextApiStatus",
]
