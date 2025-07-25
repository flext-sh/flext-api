"""Common model base classes for FLEXT API.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextResult
from pydantic import field_validator

from flext_api.base import FlextApiBaseRequest
from flext_api.common.validation import validate_entity_name


class FlextValidatedRequest(FlextApiBaseRequest):
    """FLEXT base request class with default validation to eliminate duplication."""

    def validate_business_rules(self) -> FlextResult[None]:
        """Default business rules validation - can be overridden by subclasses."""
        return FlextResult.ok(None)


class FlextNamedRequest(FlextValidatedRequest):
    """FLEXT base class for requests that include entity names."""

    name: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate entity name using common validation logic."""
        return validate_entity_name(v)
