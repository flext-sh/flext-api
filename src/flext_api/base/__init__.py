"""FLEXT API Base Patterns - Built on flext-core foundation.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

This module provides the API patterns built correctly on flext-core components.
NO fake imports, NO fallbacks, NO duplications.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Generic, TypeVar
from uuid import uuid4

from flext_core import (
    FlextEntity,
    FlextError,
    FlextResult,
    FlextValueObject,
)
from pydantic import BaseModel, Field

# ==============================================================================
# FLEXT API BASE - EXPORTS
# ==============================================================================


# Constants
class FlextApiConstants:
    """API Constants."""

    DEFAULT_TIMEOUT = 30
    MAX_RETRIES = 3
    API_VERSION = "1.0.0"


# Error classes
class FlextApiError(FlextError):
    """Base API error."""


class FlextApiServiceError(FlextApiError):
    """Service error."""


class FlextApiValidationError(FlextApiError):
    """Validation error."""


__all__ = [
    "FlextApiConstants",
    "FlextApiError",
    "FlextApiServiceError",
    "FlextApiValidationError",
]

T = TypeVar("T")


class APIStatus:
    """API Status constants."""

    SUCCESS = "success"
    ERROR = "error"
    PENDING = "pending"
    PROCESSING = "processing"


class FlextApiBaseRequest(FlextValueObject):
    """Base API request using flext-core patterns."""

    request_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    def validate_domain_rules(self) -> None:
        """Validate domain rules for API request."""
        # Validation logic can raise exceptions if needed


# Alias for backward compatibility - but prefer FlextApiBaseRequest
FlextAPIRequest = FlextApiBaseRequest


class FlextAPIResponse[T](BaseModel):
    """Base API response using flext-core patterns."""

    status: str = Field(default=APIStatus.SUCCESS)
    data: T | None = Field(default=None)
    message: str | None = Field(default=None)
    errors: list[str] = Field(default_factory=list)
    response_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    @classmethod
    def success(cls, data: T, message: str | None = None) -> FlextAPIResponse[T]:
        """Create success response."""
        return cls(status=APIStatus.SUCCESS, data=data, message=message)

    @classmethod
    def error(
        cls,
        message: str,
        errors: list[str] | None = None,
    ) -> FlextAPIResponse[T]:
        """Create error response."""
        return cls(status=APIStatus.ERROR, message=message, errors=errors or [])

    @classmethod
    def from_result(cls, result: FlextResult[T]) -> FlextAPIResponse[T]:
        """Create response from FlextResult."""
        if result.is_success:
            # Handle case where data might be None but result is successful
            return (
                cls.success(result.data)
                if result.data is not None
                else cls(status=APIStatus.SUCCESS)
            )
        return cls.error(result.error or "Unknown error")
