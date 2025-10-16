"""FLEXT API Exceptions - Exception classes for flext-api.

This module provides exception classes for flext-api operations.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations


class FlextApiException(Exception):
    """Base exception for flext-api operations."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        """Initialize exception.

        Args:
            message: Error message
            status_code: Optional HTTP status code

        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class FlextApiConfigurationError(FlextApiException):
    """Exception raised for configuration errors."""


class FlextApiConnectionError(FlextApiException):
    """Exception raised for connection errors."""


class FlextApiTimeoutError(FlextApiException):
    """Exception raised for timeout errors."""


class FlextApiValidationError(FlextApiException):
    """Exception raised for validation errors."""


class FlextApiNotFoundError(FlextApiException):
    """Exception raised for resource not found errors."""


class FlextApiAuthenticationError(FlextApiException):
    """Exception raised for authentication errors."""


class FlextApiAuthorizationError(FlextApiException):
    """Exception raised for authorization errors."""


class FlextApiRateLimitError(FlextApiException):
    """Exception raised for rate limit errors."""


class FlextApiExceptions:
    """Container class for all flext-api exceptions."""

    # Base exception
    FlextApiException = FlextApiException

    # Specific exceptions
    ConfigurationError = FlextApiConfigurationError
    ConnectionError = FlextApiConnectionError
    TimeoutError = FlextApiTimeoutError
    ValidationError = FlextApiValidationError
    NotFoundError = FlextApiNotFoundError
    AuthenticationError = FlextApiAuthenticationError
    AuthorizationError = FlextApiAuthorizationError
    RateLimitError = FlextApiRateLimitError


__all__ = ["FlextApiExceptions"]
