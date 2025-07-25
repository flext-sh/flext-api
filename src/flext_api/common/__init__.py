"""Common utilities for FLEXT API.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

Shared utilities and helpers used across all layers of the FLEXT API.
Uses semantic organization for maintainable and discoverable code.
"""

from __future__ import annotations

# ==============================================================================
# CONSTANTS AND CONFIGURATION - Application-wide constants
# ==============================================================================
from flext_api.common.constants import (
    FlextDefaultValues,
    FlextErrorMessages,
    FlextStatusCodes,
)

# ==============================================================================
# EXCEPTION HANDLING - Error processing and service availability
# ==============================================================================
from flext_api.common.exceptions import ensure_service_available, handle_api_exceptions

# ==============================================================================
# RESPONSE MODELS - Standardized response formats
# ==============================================================================
from flext_api.common.responses import PaginatedResponse, create_health_check_response

# ==============================================================================
# VALIDATION UTILITIES - Input validation and sanitization
# ==============================================================================
from flext_api.common.validation import validate_entity_name, validate_uuid

# ==============================================================================
# ALIASES FOR BACKWARD COMPATIBILITY
# ==============================================================================
FlextApiConstants = FlextDefaultValues
FlextApiError = FlextErrorMessages
FlextApiException = FlextErrorMessages
FlextApiResponse = PaginatedResponse
FlextApiValidationError = FlextErrorMessages

# ==============================================================================
# PUBLIC COMMON API - Organized by semantic category
# ==============================================================================
__all__ = [
    # ================== ALIASES ==================
    "FlextApiConstants",
    "FlextApiError",
    "FlextApiException",
    "FlextApiResponse",
    "FlextApiValidationError",
    # ================== CONSTANTS ==================
    "FlextDefaultValues",
    "FlextErrorMessages",
    "FlextStatusCodes",
    # ================== RESPONSE MODELS ==================
    "PaginatedResponse",
    "create_health_check_response",
    # ================== EXCEPTION HANDLING ==================
    "ensure_service_available",
    "handle_api_exceptions",
    # ================== VALIDATION UTILITIES ==================
    "validate_entity_name",
    "validate_uuid",
]
