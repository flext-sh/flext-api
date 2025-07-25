"""Common constants for FLEXT API.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations


class FlextErrorMessages:
    """FLEXT centralized error messages to eliminate duplication."""

    SERVICE_UNAVAILABLE = "Service not available - register implementation"
    NOT_IMPLEMENTED = "Feature not yet implemented"
    INVALID_FORMAT = "Invalid format"
    NOT_FOUND = "Resource not found"
    PLUGIN_MANAGER_UNAVAILABLE = (
        "Plugin manager not available - register a PluginManagerProvider implementation"
    )
    PIPELINE_SERVICE_UNAVAILABLE = "Pipeline service not available"
    NAME_REQUIRED = "Name is required"
    NAME_INVALID_FORMAT = (
        "Name must contain only alphanumeric characters, hyphens, and underscores"
    )


class FlextStatusCodes:
    """FLEXT HTTP status codes used throughout the API."""

    OK = 200
    CREATED = 201
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422
    INTERNAL_ERROR = 500
    SERVICE_UNAVAILABLE = 503


class FlextDefaultValues:
    """FLEXT default values used across the application."""

    PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    DEFAULT_TIMEOUT = 30
    MAX_NAME_LENGTH = 100
    MIN_NAME_LENGTH = 3
