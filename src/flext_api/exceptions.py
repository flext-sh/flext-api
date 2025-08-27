"""FLEXT API exception hierarchy - CONSOLIDATED ARCHITECTURE.

Este módulo implementa o padrão CONSOLIDATED seguindo FLEXT_REFACTORING_PROMPT.md.
Todas as exceções da API estão centralizadas na classe FlextApiExceptions,
eliminando a violação de "múltiplas classes por módulo" e garantindo
consistência arquitetural.

Padrões FLEXT aplicados:
- Classe CONSOLIDADA FlextApiExceptions contendo todas as exceções
- Herança de flext-core base exceptions
- FlextResult para operações que podem falhar
- Imports diretos sem TYPE_CHECKING
- Tipos centralizados do flext-core

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import traceback
from collections.abc import Mapping
from enum import StrEnum
from typing import Any, cast

from flext_core import (
    FlextExceptions,
    FlextLogger,
    FlextProcessingError,
)

from flext_api.constants import FlextApiConstants
from flext_api.typings import FlextTypes

logger: FlextLogger = FlextLogger(__name__)


# ==============================================================================
# ERROR CODES
# ==============================================================================


class FlextApiErrorCodes(StrEnum):
    """Error codes specific to FLEXT API operations."""

    GENERIC_API_ERROR = "FLEXT_API_ERROR"
    API_VALIDATION_ERROR = "API_VALIDATION_ERROR"
    API_AUTHENTICATION_ERROR = "API_AUTHENTICATION_ERROR"
    API_AUTHORIZATION_ERROR = "API_AUTHORIZATION_ERROR"
    API_CONFIGURATION_ERROR = "API_CONFIGURATION_ERROR"
    API_CONNECTION_ERROR = "API_CONNECTION_ERROR"
    API_PROCESSING_ERROR = "API_PROCESSING_ERROR"
    API_TIMEOUT_ERROR = "API_TIMEOUT_ERROR"
    API_REQUEST_ERROR = "API_REQUEST_ERROR"
    API_RESPONSE_ERROR = "API_RESPONSE_ERROR"
    API_STORAGE_ERROR = "API_STORAGE_ERROR"
    API_BUILDER_ERROR = "API_BUILDER_ERROR"
    API_RATE_LIMIT_ERROR = "API_RATE_LIMIT_ERROR"
    API_NOT_FOUND_ERROR = "API_NOT_FOUND_ERROR"


# ==============================================================================
# CONSOLIDATED FLEXT API EXCEPTIONS CLASS
# ==============================================================================


class FlextApiExceptions(FlextExceptions):  # noqa: N818
    """Single consolidated class containing all API exceptions following FLEXT patterns.

    This class follows the CONSOLIDATED class pattern from FLEXT_REFACTORING_PROMPT.md,
    centralizing all exception definitions into a single class structure to eliminate
    the "multiple classes per module" violation while maintaining clean
    architecture principles.

    All exception classes are defined as nested classes within this consolidated
    structure, providing namespace organization and proper inheritance.
    """

    # ==============================================================================
    # ERROR MIXIN FOR MYPY COMPATIBILITY
    # ==============================================================================

    class FlextApiErrorMixin:
        """Mixin to provide MyPy-compatible access to flext-core error attributes."""

        def get_error_code(self) -> str:
            """Get error code - implemented by flext-core."""
            return getattr(self, "code", "UNKNOWN")

        def get_context(self) -> dict[str, object]:
            """Get error context - implemented by flext-core."""
            return getattr(self, "context", {})

    # ==============================================================================
    # BASE API ERROR
    # ==============================================================================

    class FlextApiError(FlextApiErrorMixin, FlextExceptions.FlextExceptionBaseError):
        """Base API error with HTTP status code support using FlextExceptionsMixin pattern."""

        def __init__(
            self,
            message: str = "flext_api error",
            *,
            status_code: int = 500,
            code: FlextApiErrorCodes | None = None,
            context: Mapping[str, object] | None = None,
            **extra_context: object,
        ) -> None:
            """Initialize with message, status code, and context."""
            self.status_code = status_code

            # Merge contexts
            merged_context: dict[str, object] = dict(context or {})
            merged_context.update(extra_context)
            merged_context["status_code"] = status_code

            super().__init__(
                message,
                code=code or FlextApiErrorCodes.GENERIC_API_ERROR,
                context=merged_context,
            )

        def to_http_response(self) -> FlextTypes.Core.JsonDict:
            """Convert exception to HTTP response format."""
            return {
                "success": False,
                "error": {
                    "code": self.code,
                    "message": str(self),
                    "status_code": self.status_code,
                    "context": self.get_context(),
                },
                "data": None,
            }

    # ==============================================================================
    # SPECIFIC API ERRORS - INHERIT FROM FLEXT-CORE BASE CLASSES
    # ==============================================================================

    class FlextApiValidationError(FlextApiErrorMixin, FlextExceptions):
        """Validation error in API with field-specific context."""

        def __init__(
            self,
            message: str = "API validation failed",
            *,
            field: str | None = None,
            value: object = None,
            endpoint: str | None = None,
            status_code: int = 400,
            context: Mapping[str, object] | None = None,
            **extra_context: object,
        ) -> None:
            """Initialize validation error with field and value context."""
            self.status_code = status_code

            # Merge contexts
            merged_context: dict[str, object] = dict(context or {})
            merged_context.update(extra_context)

            # Add API-specific context
            if endpoint is not None:
                merged_context["endpoint"] = endpoint
            merged_context["status_code"] = status_code

            # Truncate long values for security
            truncated_value = value
            if value is not None:
                str_value = str(value)
                max_len = FlextApiConstants.ApiValidation.MAX_ERROR_VALUE_LENGTH
                truncated_value = (
                    str_value[:max_len] if len(str_value) > max_len else str_value
                )

            # Store validation details for test compatibility
            self.validation_details: dict[str, object] = {}
            if field is not None:
                self.validation_details["field"] = field
            if truncated_value is not None:
                self.validation_details["value"] = str(truncated_value)

            super().__init__(
                message,
                code="FLEXT_3001",
                context=merged_context,
            )

        def to_http_response(self) -> FlextTypes.Core.JsonDict:
            """Convert to HTTP validation error response."""
            return {
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": str(self),
                    "status_code": self.status_code,
                    "validation_details": getattr(self, "validation_details", {}),
                    "context": self.get_context(),
                },
                "data": None,
            }

    class FlextApiAuthenticationError(FlextApiErrorMixin, FlextExceptions):
        """Authentication error in API with auth method context."""

        def __init__(
            self,
            message: str = "flext_api authentication failed",
            *,
            auth_method: str | None = None,
            endpoint: str | None = None,
            token_type: str | None = None,
            status_code: int = 401,
            context: Mapping[str, object] | None = None,
            **extra_context: object,
        ) -> None:
            """Initialize authentication error with auth method context."""
            self.status_code = status_code

            # Merge contexts
            merged_context: dict[str, object] = dict(context or {})
            merged_context.update(extra_context)

            # Add API-specific context
            if auth_method is not None:
                merged_context["auth_method"] = auth_method
            if endpoint is not None:
                merged_context["endpoint"] = endpoint
            if token_type is not None:
                merged_context["token_type"] = token_type
            merged_context["status_code"] = status_code

            # Format message to include flext_api prefix for test compatibility
            formatted_message = (
                f"flext_api: {message}"
                if not message.startswith("flext_api:")
                else message
            )
            super().__init__(
                formatted_message,
                code="AUTH_ERROR",
                context=merged_context,
            )

        def to_http_response(self) -> FlextTypes.Core.JsonDict:
            """Convert to HTTP authentication error response."""
            return {
                "success": False,
                "error": {
                    "code": "AUTHENTICATION_ERROR",
                    "message": str(self),
                    "status_code": self.status_code,
                    "context": self.get_context(),
                },
                "data": None,
            }

    class FlextApiAuthorizationError(FlextApiError):
        """Authorization error for insufficient permissions."""

        def __init__(
            self,
            message: str = "Insufficient permissions",
            *,
            required_permission: str | None = None,
            user_permissions: list[str] | None = None,
            endpoint: str | None = None,
            context: Mapping[str, object] | None = None,
            **extra_context: object,
        ) -> None:
            """Initialize authorization error with permission context."""
            # Merge contexts
            merged_context: dict[str, object] = dict(context or {})
            merged_context.update(extra_context)

            # Add authorization-specific context
            if required_permission is not None:
                merged_context["required_permission"] = required_permission
            if user_permissions is not None:
                merged_context["user_permissions"] = user_permissions
            if endpoint is not None:
                merged_context["endpoint"] = endpoint

            super().__init__(
                f"Authorization: {message}",
                status_code=403,
                code=FlextApiErrorCodes.GENERIC_API_ERROR,
                context=merged_context,
            )

    class FlextApiConfigurationError(FlextApiErrorMixin, FlextExceptions.FlextConfigurationError):
        """Configuration error in API with config key context."""

        def __init__(
            self,
            message: str = "API configuration error",
            *,
            config_key: str | None = None,
            expected_type: str | None = None,
            actual_value: object = None,
            status_code: int = 500,
            context: Mapping[str, object] | None = None,
            **extra_context: object,
        ) -> None:
            """Initialize configuration error with config context."""
            self.status_code = status_code

            # Merge contexts
            merged_context: dict[str, object] = dict(context or {})
            merged_context.update(extra_context)

            # Add configuration-specific context
            if config_key is not None:
                merged_context["config_key"] = config_key
            if expected_type is not None:
                merged_context["expected_type"] = expected_type
            if actual_value is not None:
                merged_context["actual_value"] = str(actual_value)
            merged_context["status_code"] = status_code

            super().__init__(
                message,
                code="CONFIG_ERROR",
                context=merged_context,
            )

        def to_http_response(self) -> FlextTypes.Core.JsonDict:
            """Convert to HTTP configuration error response."""
            return {
                "success": False,
                "error": {
                    "code": "CONFIGURATION_ERROR",
                    "message": str(self),
                    "status_code": self.status_code,
                    "context": self.get_context(),
                },
                "data": None,
            }

    class FlextApiConnectionError(FlextApiErrorMixin, FlextExceptions):
        """Connection error in API with network context."""

        def __init__(
            self,
            message: str = "API connection error",
            *,
            host: str | None = None,
            port: int | None = None,
            ssl_error: str | None = None,
            connection_timeout: float | None = None,
            status_code: int = 503,
            context: Mapping[str, object] | None = None,
            **extra_context: object,
        ) -> None:
            """Initialize connection error with network context."""
            self.status_code = status_code

            # Merge contexts
            merged_context: dict[str, object] = dict(context or {})
            merged_context.update(extra_context)

            # Add connection-specific context
            if host is not None:
                merged_context["host"] = host
            if port is not None:
                merged_context["port"] = port
            if ssl_error is not None:
                merged_context["ssl_error"] = ssl_error
            if connection_timeout is not None:
                merged_context["connection_timeout"] = connection_timeout
            merged_context["status_code"] = status_code

            super().__init__(
                message,
                code="FLEXT_2001",
                context=merged_context,
            )

        def to_http_response(self) -> FlextTypes.Core.JsonDict:
            """Convert to HTTP connection error response."""
            return {
                "success": False,
                "error": {
                    "code": "CONNECTION_ERROR",
                    "message": str(self),
                    "status_code": self.status_code,
                    "context": self.get_context(),
                },
                "data": None,
            }

    class FlextApiProcessingError(FlextApiErrorMixin, FlextProcessingError):
        """Processing error in API with operation context."""

        def __init__(
            self,
            message: str = "API processing error",
            *,
            operation: str | None = None,
            endpoint: str | None = None,
            processing_stage: str | None = None,
            status_code: int = 500,
            context: Mapping[str, object] | None = None,
            **extra_context: object,
        ) -> None:
            """Initialize processing error with operation context."""
            self.status_code = status_code

            # Merge contexts
            merged_context: dict[str, object] = dict(context or {})
            merged_context.update(extra_context)

            # Add processing-specific context
            if operation is not None:
                merged_context["operation"] = operation
            if endpoint is not None:
                merged_context["endpoint"] = endpoint
            if processing_stage is not None:
                merged_context["processing_stage"] = processing_stage
            merged_context["status_code"] = status_code

            super().__init__(
                message,
                code="PROCESSING_ERROR",
                context=merged_context,
            )

        def to_http_response(self) -> FlextTypes.Core.JsonDict:
            """Convert to HTTP processing error response."""
            return {
                "success": False,
                "error": {
                    "code": "PROCESSING_ERROR",
                    "message": str(self),
                    "status_code": self.status_code,
                    "context": self.get_context(),
                },
                "data": None,
            }

    class FlextApiTimeoutError(FlextApiErrorMixin, FlextExceptions):
        """Timeout error in API with timeout context."""

        def __init__(
            self,
            message: str = "API timeout error",
            *,
            endpoint: str | None = None,
            timeout_seconds: float | None = None,
            query_type: str | None = None,
            operation: str | None = None,
            status_code: int = 504,
            context: Mapping[str, object] | None = None,
            **extra_context: object,
        ) -> None:
            """Initialize timeout error with timeout context."""
            self.status_code = status_code

            # Merge contexts
            merged_context: dict[str, object] = dict(context or {})
            merged_context.update(extra_context)

            # Add timeout-specific context
            if endpoint is not None:
                merged_context["endpoint"] = endpoint
            if query_type is not None:
                merged_context["query_type"] = query_type
            if operation is not None:
                merged_context["operation"] = operation
            merged_context["status_code"] = status_code

            # Include timeout_seconds in context for test expectations with precision
            if timeout_seconds is not None:
                merged_context["timeout_seconds"] = float(timeout_seconds)

            super().__init__(
                message,
                code="FLEXT_2002",
                context=merged_context,
            )

        def to_http_response(self) -> FlextTypes.Core.JsonDict:
            """Convert to HTTP timeout error response."""
            return {
                "success": False,
                "error": {
                    "code": "TIMEOUT_ERROR",
                    "message": str(self),
                    "status_code": self.status_code,
                    "context": self.get_context(),
                },
                "data": None,
            }

    # ==============================================================================
    # API-SPECIFIC ERRORS - INHERIT FROM BASE FlextApiError
    # ==============================================================================

    class FlextApiRequestError(FlextApiError):
        """API request errors with HTTP method and endpoint context."""

        def __init__(
            self,
            message: str = "API request error",
            *,
            method: str | None = None,
            endpoint: str | None = None,
            status_code: int = 400,
            request_id: str | None = None,
            context: Mapping[str, object] | None = None,
            **extra_context: object,
        ) -> None:
            """Initialize with API request context."""
            # Merge contexts
            merged_context: dict[str, object] = dict(context or {})
            merged_context.update(extra_context)

            # Add request-specific context
            if method is not None:
                merged_context["method"] = method
            if endpoint is not None:
                merged_context["endpoint"] = endpoint
            if request_id is not None:
                merged_context["request_id"] = request_id

            super().__init__(
                f"API request: {message}",
                status_code=status_code,
                code=FlextApiErrorCodes.GENERIC_API_ERROR,
                context=merged_context,
            )

    class FlextApiResponseError(FlextApiError):
        """API response errors with response context."""

        def __init__(
            self,
            message: str = "API response error",
            *,
            status_code: int = 502,
            response_body: str | None = None,
            content_type: str | None = None,
            context: Mapping[str, object] | None = None,
            **extra_context: object,
        ) -> None:
            """Initialize with API response context."""
            # Merge contexts
            merged_context: dict[str, object] = dict(context or {})
            merged_context.update(extra_context)

            # Add response-specific context
            if response_body is not None:
                # Limit response body size for security and readability
                merged_context["response_body"] = str(response_body)[:200]
            if content_type is not None:
                merged_context["content_type"] = content_type

            super().__init__(
                f"API response: {message}",
                status_code=status_code,
                code=FlextApiErrorCodes.GENERIC_API_ERROR,
                context=merged_context,
            )

    class FlextApiStorageError(FlextApiError):
        """API storage errors with storage context."""

        def __init__(
            self,
            message: str = "API storage error",
            *,
            storage_type: str | None = None,
            operation: str | None = None,
            pool_size: int | None = None,
            active_connections: int | None = None,
            status_code: int = 500,
            context: Mapping[str, object] | None = None,
            **extra_context: object,
        ) -> None:
            """Initialize with API storage context."""
            # Merge contexts
            merged_context: dict[str, object] = dict(context or {})
            merged_context.update(extra_context)

            # Add storage-specific context
            if storage_type is not None:
                merged_context["storage_type"] = storage_type
            if operation is not None:
                merged_context["operation"] = operation
            if pool_size is not None:
                merged_context["pool_size"] = pool_size
            if active_connections is not None:
                merged_context["active_connections"] = active_connections

            super().__init__(
                f"API storage: {message}",
                status_code=status_code,
                code=FlextApiErrorCodes.GENERIC_API_ERROR,
                context=merged_context,
            )

    class FlextApiBuilderError(FlextApiError):
        """API builder errors with builder context."""

        def __init__(
            self,
            message: str = "API builder error",
            *,
            builder_step: str | None = None,
            expected_type: str | None = None,
            actual_value: str | None = None,
            builder_type: str | None = None,
            status_code: int = 400,
            context: Mapping[str, object] | None = None,
            **extra_context: object,
        ) -> None:
            """Initialize with API builder context."""
            # Merge contexts
            merged_context: dict[str, object] = dict(context or {})
            merged_context.update(extra_context)

            # Add builder-specific context
            if builder_step is not None:
                merged_context["builder_step"] = builder_step
            if expected_type is not None:
                merged_context["expected_type"] = expected_type
            if actual_value is not None:
                merged_context["actual_value"] = actual_value
            if builder_type is not None:
                merged_context["builder_type"] = builder_type

            super().__init__(
                f"API builder: {message}",
                status_code=status_code,
                code=FlextApiErrorCodes.GENERIC_API_ERROR,
                context=merged_context,
            )

    class FlextApiRateLimitError(FlextApiError):
        """API rate limiting errors."""

        def __init__(
            self,
            message: str = "Rate limit exceeded",
            *,
            limit: int | None = None,
            window_seconds: int | None = None,
            retry_after: int | None = None,
            endpoint: str | None = None,
            context: Mapping[str, object] | None = None,
            **extra_context: object,
        ) -> None:
            """Initialize with rate limiting context."""
            # Merge contexts
            merged_context: dict[str, object] = dict(context or {})
            merged_context.update(extra_context)

            # Add rate limit-specific context
            if limit is not None:
                merged_context["limit"] = limit
            if window_seconds is not None:
                merged_context["window_seconds"] = window_seconds
            if retry_after is not None:
                merged_context["retry_after"] = retry_after
            if endpoint is not None:
                merged_context["endpoint"] = endpoint

            super().__init__(
                f"Rate limit: {message}",
                status_code=429,
                code=FlextApiErrorCodes.GENERIC_API_ERROR,
                context=merged_context,
            )

    class FlextApiNotFoundError(FlextApiError):
        """API resource not found errors."""

        def __init__(
            self,
            message: str = "Resource not found",
            *,
            resource_type: str | None = None,
            resource_id: str | None = None,
            endpoint: str | None = None,
            context: Mapping[str, object] | None = None,
            **extra_context: object,
        ) -> None:
            """Initialize with resource context."""
            # Merge contexts
            merged_context: dict[str, object] = dict(context or {})
            merged_context.update(extra_context)

            # Add not found-specific context
            if resource_type is not None:
                merged_context["resource_type"] = resource_type
            if resource_id is not None:
                merged_context["resource_id"] = resource_id
            if endpoint is not None:
                merged_context["endpoint"] = endpoint

            super().__init__(
                f"Not found: {message}",
                status_code=404,
                code=FlextApiErrorCodes.GENERIC_API_ERROR,
                context=merged_context,
            )

    # ==============================================================================
    # UTILITY METHODS
    # ==============================================================================

    @staticmethod
    def create_error_response(
        exception: FlextApiExceptions.FlextApiError,
        *,
        include_traceback: bool = False,
    ) -> FlextTypes.Core.JsonDict:
        """Create standardized error response from exception."""
        response = exception.to_http_response()

        if include_traceback:
            error_dict = response["error"]
            if isinstance(error_dict, dict):
                error_dict["traceback"] = traceback.format_exc()

        return response

    @staticmethod
    def _get_specific_exception(
        status_code: int,
        message: str,
    ) -> FlextApiExceptions.FlextApiError | None:
        """Get specific exception for known status codes."""
        # Use Any type for simplicity - exceptions have different inheritance
        specific_exceptions: dict[int, Any] = {  # type: ignore[explicit-any]
            400: FlextApiExceptions.FlextApiRequestError,
            401: FlextApiExceptions.FlextApiAuthenticationError,
            403: FlextApiExceptions.FlextApiAuthorizationError,
            404: FlextApiExceptions.FlextApiNotFoundError,
            429: FlextApiExceptions.FlextApiRateLimitError,
            500: FlextApiExceptions.FlextApiProcessingError,
            502: FlextApiExceptions.FlextApiResponseError,
            503: FlextApiExceptions.FlextApiConnectionError,
            504: FlextApiExceptions.FlextApiTimeoutError,
        }

        exception_class = specific_exceptions.get(status_code)
        if exception_class:
            try:
                result = exception_class(message or "Error", status_code=status_code)
                return cast("FlextApiExceptions.FlextApiError", result)
            except TypeError:
                # Handle exceptions that don't accept status_code parameter
                result = exception_class(message or "Error")
                return cast("FlextApiExceptions.FlextApiError", result)
        return None

    @staticmethod
    def map_http_status_to_exception(
        status_code: int,
        message: str = "",
        **context: object,
    ) -> FlextApiExceptions.FlextApiError:
        """Map HTTP status code to appropriate exception type."""
        # Try specific exception first
        specific_exception = FlextApiExceptions._get_specific_exception(
            status_code, message
        )
        if specific_exception is not None:
            return specific_exception

        # Range-based fallbacks
        if (
            FlextApiConstants.HTTP.CLIENT_ERROR_MIN
            <= status_code
            < FlextApiConstants.HTTP.CLIENT_ERROR_MAX
        ):
            return FlextApiExceptions.FlextApiRequestError(
                message or "Client error",
                status_code=status_code,
                context=context,
            )

        if (
            FlextApiConstants.HTTP.SERVER_ERROR_MIN
            <= status_code
            < FlextApiConstants.HTTP.SERVER_ERROR_MAX
        ):
            return FlextApiExceptions.FlextApiError(
                message or "Server error",
                status_code=status_code,
                code=FlextApiErrorCodes.GENERIC_API_ERROR,
                context=context,
            )

        # Default fallback
        return FlextApiExceptions.FlextApiError(
            message or "Unknown error",
            status_code=status_code,
            code=FlextApiErrorCodes.GENERIC_API_ERROR,
            context=context,
        )

    @classmethod
    def get_all_exception_classes(cls) -> dict[str, type]:
        """Get all nested exception classes for external access."""
        return {
            # Error Mixin
            "FlextApiErrorMixin": cls.FlextApiErrorMixin,
            # Base Error
            "FlextApiError": cls.FlextApiError,
            # Core API Errors - inherit from flext-core
            "FlextApiValidationError": cls.FlextApiValidationError,
            "FlextApiAuthenticationError": cls.FlextApiAuthenticationError,
            "FlextApiConfigurationError": cls.FlextApiConfigurationError,
            "FlextApiConnectionError": cls.FlextApiConnectionError,
            "FlextApiProcessingError": cls.FlextApiProcessingError,
            "FlextApiTimeoutError": cls.FlextApiTimeoutError,
            # Specific API Errors - inherit from FlextApiError
            "FlextApiAuthorizationError": cls.FlextApiAuthorizationError,
            "FlextApiRequestError": cls.FlextApiRequestError,
            "FlextApiResponseError": cls.FlextApiResponseError,
            "FlextApiStorageError": cls.FlextApiStorageError,
            "FlextApiBuilderError": cls.FlextApiBuilderError,
            "FlextApiRateLimitError": cls.FlextApiRateLimitError,
            "FlextApiNotFoundError": cls.FlextApiNotFoundError,
        }


# ==============================================================================
# CONVENIENCE ALIASES FOR BACKWARD COMPATIBILITY
# ==============================================================================

# Export consolidated class types for direct access
FlextApiErrorMixin = FlextApiExceptions.FlextApiErrorMixin

# Base Error
FlextApiError = FlextApiExceptions.FlextApiError

# Core API Errors - inherit from flext-core
FlextApiValidationError = FlextApiExceptions.FlextApiValidationError
FlextApiAuthenticationError = FlextApiExceptions.FlextApiAuthenticationError
FlextApiConfigurationError = FlextApiExceptions.FlextApiConfigurationError
FlextApiConnectionError = FlextApiExceptions.FlextApiConnectionError
FlextApiProcessingError = FlextApiExceptions.FlextApiProcessingError
FlextApiTimeoutError = FlextApiExceptions.FlextApiTimeoutError

# Specific API Errors - inherit from FlextApiError
FlextApiAuthorizationError = FlextApiExceptions.FlextApiAuthorizationError
FlextApiRequestError = FlextApiExceptions.FlextApiRequestError
FlextApiResponseError = FlextApiExceptions.FlextApiResponseError
FlextApiStorageError = FlextApiExceptions.FlextApiStorageError
FlextApiBuilderError = FlextApiExceptions.FlextApiBuilderError
FlextApiRateLimitError = FlextApiExceptions.FlextApiRateLimitError
FlextApiNotFoundError = FlextApiExceptions.FlextApiNotFoundError

# Utility Functions
create_error_response = FlextApiExceptions.create_error_response
map_http_status_to_exception = FlextApiExceptions.map_http_status_to_exception


# ==============================================================================
# EXPORTS
# ==============================================================================

__all__ = [
    # Core API Errors - inherit from flext-core
    "FlextApiAuthenticationError",
    # Specific API Errors - inherit from FlextApiError
    "FlextApiAuthorizationError",
    "FlextApiBuilderError",
    "FlextApiConfigurationError",
    "FlextApiConnectionError",
    # Base Error and Mixin
    "FlextApiError",
    "FlextApiErrorCodes",
    "FlextApiErrorMixin",
    "FlextApiExceptions",
    "FlextApiNotFoundError",
    "FlextApiProcessingError",
    "FlextApiRateLimitError",
    "FlextApiRequestError",
    "FlextApiResponseError",
    "FlextApiStorageError",
    "FlextApiTimeoutError",
    "FlextApiValidationError",
    # Utility Functions
    "create_error_response",
    "map_http_status_to_exception",
]
