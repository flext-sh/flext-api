"""FLEXT-API Helper Classes and Utilities.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Powerful helper classes designed for massive code reduction in projects.
"""

from __future__ import annotations

# Legacy compatibility imports (with deprecation warnings)
from flext_api.helpers.api_builder import FlextAPIBuilder  # Legacy name
from flext_api.helpers.decorators import (
    authenticated,  # Legacy name
    authorize_roles,  # Legacy name
    cache_response,  # Legacy name
    flext_api_authenticated,
    flext_api_authorize_roles,
    flext_api_cache_response,
    flext_api_handle_errors,
    flext_api_log_execution,
    flext_api_rate_limit,
    flext_api_require_json,
    flext_api_validate_request,
    handle_errors,  # Legacy name
    log_execution,  # Legacy name
    rate_limit,  # Legacy name
    require_json,  # Legacy name
    validate_request,  # Legacy name
)

# Import FlextApi prefixed classes and functions
from flext_api.helpers.flext_api_builder import FlextApiBuilder
from flext_api.helpers.query_builder import (
    FlextApiQueryBuilder,
    FlextQueryBuilder,  # Legacy name
)
from flext_api.helpers.response_builder import (
    FlextApiResponseBuilder,
    FlextResponseBuilder,  # Legacy name
)
from flext_api.helpers.validation import (
    FlextApiValidator,
    FlextValidator,  # Legacy name
    flext_api_normalize_phone,
    flext_api_sanitize_email,
    flext_api_sanitize_string,
    flext_api_validate_email,
    flext_api_validate_ip_address,
    flext_api_validate_password,
    flext_api_validate_phone,
    flext_api_validate_url,
    flext_api_validate_uuid,
    validate_email,  # Legacy name
    validate_password,  # Legacy name
    validate_uuid,  # Legacy name
)

__all__ = [
    # ===== LEGACY COMPATIBILITY =====
    "FlextAPIBuilder",   # Use FlextApiBuilder instead
    # ===== FLEXT-API PREFIXED CLASSES =====
    "FlextApiBuilder",
    "FlextApiQueryBuilder",
    "FlextApiResponseBuilder",
    "FlextApiValidator",
    "FlextQueryBuilder", # Use FlextApiQueryBuilder instead
    "FlextResponseBuilder", # Use FlextApiResponseBuilder instead
    "FlextValidator",    # Use FlextApiValidator instead
    "authenticated",     # Use flext_api_authenticated instead
    "authorize_roles",   # Use flext_api_authorize_roles instead
    "cache_response",    # Use flext_api_cache_response instead
    # ===== FLEXT-API PREFIXED DECORATORS =====
    "flext_api_authenticated",
    "flext_api_authorize_roles",
    "flext_api_cache_response",
    "flext_api_handle_errors",
    "flext_api_log_execution",
    "flext_api_normalize_phone",
    "flext_api_rate_limit",
    "flext_api_require_json",
    "flext_api_sanitize_email",
    "flext_api_sanitize_string",
    # ===== FLEXT-API PREFIXED VALIDATION FUNCTIONS =====
    "flext_api_validate_email",
    "flext_api_validate_ip_address",
    "flext_api_validate_password",
    "flext_api_validate_phone",
    "flext_api_validate_request",
    "flext_api_validate_url",
    "flext_api_validate_uuid",
    # ===== LEGACY COMPATIBILITY =====
    "handle_errors",     # Use flext_api_handle_errors instead
    "log_execution",     # Use flext_api_log_execution instead
    "rate_limit",        # Use flext_api_rate_limit instead
    "require_json",      # Use flext_api_require_json instead
    "validate_email",    # Use flext_api_validate_email instead
    "validate_password", # Use flext_api_validate_password instead
    "validate_request",  # Use flext_api_validate_request instead
    "validate_uuid",     # Use flext_api_validate_uuid instead
]
