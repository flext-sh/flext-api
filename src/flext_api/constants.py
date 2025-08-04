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

from flext_core.constants import FlextConstants

# ==============================================================================
# API-SPECIFIC CONSTANTS - Extending flext-core
# ==============================================================================


class FlextApiConstants(FlextConstants):
    """API-specific constants extending flext-core platform constants."""

    # HTTP status groups using standard library constants
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

    # API response formats
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

    # API-specific validation patterns (extend core patterns)
    USERNAME_PATTERN = r"^[a-zA-Z0-9_]{3,50}$"
    PIPELINE_NAME_PATTERN = r"^[a-zA-Z0-9_-]{1,100}$"

    # Rate limiting constants
    RATE_LIMIT_REQUESTS: ClassVar[int] = 1000
    RATE_LIMIT_WINDOW: ClassVar[int] = 3600


class FlextApiFieldType:
    """API-specific field types that don't exist in flext-core."""

    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"  # noqa: S105
    PIPELINE_CONFIG = "pipeline_config"
    PLUGIN_CONFIG = "plugin_config"
    USER_ROLE = "user_role"
    ENDPOINT_PATH = "endpoint_path"
    HTTP_METHOD = "http_method"
    RESPONSE_FORMAT = "response_format"


class FlextApiStatus:
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


class FlextApiEndpoints:
    """API endpoint constants."""

    # Base paths
    API_V1 = "/api/v1"
    HEALTH = "/health"
    METRICS = "/metrics"
    DOCS = "/docs"

    # Authentication endpoints
    AUTH_LOGIN = f"{API_V1}/auth/login"
    AUTH_LOGOUT = f"{API_V1}/auth/logout"
    AUTH_REFRESH = f"{API_V1}/auth/refresh"
    AUTH_VERIFY = f"{API_V1}/auth/verify"

    # Pipeline endpoints
    PIPELINES = f"{API_V1}/pipelines"
    PIPELINE_RUN = f"{API_V1}/pipelines/{{pipeline_id}}/run"
    PIPELINE_STATUS = f"{API_V1}/pipelines/{{pipeline_id}}/status"
    PIPELINE_LOGS = f"{API_V1}/pipelines/{{pipeline_id}}/logs"

    # Plugin endpoints
    PLUGINS = f"{API_V1}/plugins"
    PLUGIN_INSTALL = f"{API_V1}/plugins/install"
    PLUGIN_UNINSTALL = f"{API_V1}/plugins/{{plugin_id}}/uninstall"
    PLUGIN_CONFIG = f"{API_V1}/plugins/{{plugin_id}}/config"


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
    # Module-level constants
    "FLEXT_API_CACHE_TTL",
    "FLEXT_API_MAX_RETRIES",
    "FLEXT_API_TIMEOUT",
    "FLEXT_API_VERSION",
    # Classes
    "FlextApiConstants",
    "FlextApiEndpoints",
    "FlextApiFieldType",
    "FlextApiStatus",
]
