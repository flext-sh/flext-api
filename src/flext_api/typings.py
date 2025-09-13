"""FLEXT API Types - Type definitions for API operations following Python 3.13+ syntax.

Strict hierarchical organization and flext-core foundation patterns for type-safe HTTP operations.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Literal

from flext_core import FlextTypes


class FlextApiTypes:
    """Unified API types using flext-core extensively - ZERO DUPLICATION."""

    # =============================================================================
    # Direct re-export of flext-core types - NO DUPLICATION
    # =============================================================================

    # Core types from flext-core
    Core = FlextTypes.Core

    # =============================================================================
    # HTTP-specific type aliases - Only what's not in flext-core
    # =============================================================================

    # HTTP-specific type aliases with Python 3.13+ advanced features
    HttpMethod = Literal["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
    # Python 3.13+ advanced type constraints for HTTP status codes
    HttpStatus = int  # Range[100, 599] when available
    HttpHeaders = Core.Headers  # Use flext-core headers type
    HttpUrl = str  # Annotated[str, Url] pattern ready
    HttpBody = str | bytes | Core.Dict | None

    # Request/Response types using flext-core - more specific
    RequestData = Core.Dict | str | bytes | None
    ResponseData = Core.Dict | str | bytes | None  # More specific than object

    # Client configuration using flext-core with Python 3.13+ type optimizations
    ClientConfig = Core.Dict
    # Python 3.13+ optimized timeout type with constrained values
    TimeoutConfig = float | tuple[float, float] | None  # Positive[float] when available

    # Authentication using flext-core
    AuthToken = str
    ApiKey = str

    # Validation using flext-core - use FlextResult directly
    # ValidationResult = FlextResult  # Use FlextResult directly for type safety

    # Cache types using flext-core - more specific
    CacheKey = str
    CacheValue = Core.Dict | str | bytes | None  # More specific than object

    # Error types using flext-core
    ErrorContext = Core.Dict
    ErrorCode = str


__all__: FlextTypes.Core.StringList = [
    "FlextApiTypes",
]
