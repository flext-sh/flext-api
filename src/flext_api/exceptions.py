"""FLEXT API Exception Hierarchy using flext-core patterns.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

This module provides a complete exception hierarchy following SOLID principles
and using flext-core exception patterns. NO fallbacks or suppression allowed.
"""

from __future__ import annotations

from typing import Any

from flext_core import FlextResult


class FlextAPIError(Exception):
    """Base exception for all FLEXT API errors.

    Follows flext-core exception patterns with proper error context.
    """

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        """Initialize API exception with context."""
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.context = context or {}

    def to_result(self) -> FlextResult[None]:
        """Convert exception to FlextResult for consistent error handling."""
        return FlextResult.fail(self.message)


# ==============================================================================
# DOMAIN LAYER EXCEPTIONS - Business Rule Violations
# ==============================================================================


class FlextAPIDomainError(FlextAPIError):
    """Base class for domain layer exceptions."""


class FlextAPIDomainValidationError(FlextAPIDomainError):
    """Domain validation rule violation."""


class FlextAPIEntityNotFoundError(FlextAPIDomainError):
    """Entity not found in domain."""


class FlextAPIEntityAlreadyExistsError(FlextAPIDomainError):
    """Entity already exists in domain."""


class FlextAPIInvariantViolationError(FlextAPIDomainError):
    """Domain invariant violation."""


# ==============================================================================
# APPLICATION LAYER EXCEPTIONS - Use Case Failures
# ==============================================================================


class FlextAPIApplicationError(FlextAPIError):
    """Base class for application layer exceptions."""


class FlextAPIServiceError(FlextAPIApplicationError):
    """Application service error."""


class FlextAPIUseCaseError(FlextAPIApplicationError):
    """Use case execution error."""


class FlextAPIAuthenticationError(FlextAPIApplicationError):
    """Authentication failure."""


class FlextAPIAuthorizationError(FlextAPIApplicationError):
    """Authorization failure."""


class FlextAPIBusinessRuleViolationError(FlextAPIApplicationError):
    """Business rule violation in application layer."""


# ==============================================================================
# INFRASTRUCTURE LAYER EXCEPTIONS - Technical Failures
# ==============================================================================


class FlextAPIInfrastructureError(FlextAPIError):
    """Base class for infrastructure layer exceptions."""


class FlextAPIRepositoryError(FlextAPIInfrastructureError):
    """Repository operation failure."""


class FlextAPIConnectionError(FlextAPIInfrastructureError):
    """Connection failure - NO MORE FAKE flext-core inheritance."""

    def __init__(
        self,
        message: str,
        connection_type: str = "api",
        context: dict[str, Any] | None = None,
    ) -> None:
        """Initialize connection exception with proper patterns."""
        enhanced_context = context or {}
        enhanced_context["connection_type"] = connection_type
        super().__init__(message, context=enhanced_context)


class FlextAPIDatabaseError(FlextAPIInfrastructureError):
    """Database operation failure."""


class FlextAPIExternalServiceError(FlextAPIInfrastructureError):
    """External service failure."""


class FlextAPIConfigurationError(FlextAPIInfrastructureError):
    """Configuration error."""


# ==============================================================================
# API LAYER EXCEPTIONS - HTTP and Request Handling
# ==============================================================================


class FlextAPIHttpError(FlextAPIError):
    """Base class for HTTP layer exceptions."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        """Initialize HTTP exception with status code."""
        super().__init__(message, error_code, context)
        self.status_code = status_code


class FlextAPIValidationError(FlextAPIHttpError):
    """HTTP request validation error."""

    def __init__(
        self, message: str, validation_errors: list[dict[str, Any]] | None = None
    ) -> None:
        """Initialize validation exception."""
        super().__init__(message, status_code=422, error_code="VALIDATION_ERROR")
        self.validation_errors = validation_errors or []


class FlextAPINotFoundError(FlextAPIHttpError):
    """HTTP 404 Not Found."""

    def __init__(self, resource: str, identifier: str | None = None) -> None:
        """Initialize not found error."""
        message = f"{resource} not found"
        if identifier:
            message += f" with identifier: {identifier}"
        super().__init__(message, status_code=404, error_code="NOT_FOUND")


class FlextAPIConflictError(FlextAPIHttpError):
    """HTTP 409 Conflict."""

    def __init__(self, message: str) -> None:
        """Initialize conflict error."""
        super().__init__(message, status_code=409, error_code="CONFLICT")


class FlextAPIUnprocessableEntityError(FlextAPIHttpError):
    """HTTP 422 Unprocessable Entity."""

    def __init__(self, message: str) -> None:
        """Initialize unprocessable entity error."""
        super().__init__(message, status_code=422, error_code="UNPROCESSABLE_ENTITY")


class FlextAPIRateLimitExceededError(FlextAPIHttpError):
    """HTTP 429 Too Many Requests."""

    def __init__(self, retry_after: int | None = None) -> None:
        """Initialize rate limit error."""
        message = "Rate limit exceeded"
        if retry_after:
            message += f". Retry after {retry_after} seconds"
        super().__init__(message, status_code=429, error_code="RATE_LIMITED")
        self.retry_after = retry_after


# ==============================================================================
# PLUGIN SYSTEM EXCEPTIONS - Plugin Management
# ==============================================================================


class FlextAPIPluginError(FlextAPIError):
    """Base class for plugin system exceptions."""


class FlextAPIPluginNotFoundError(FlextAPIPluginError):
    """Plugin not found."""


class FlextAPIPluginInstallationError(FlextAPIPluginError):
    """Plugin installation failure."""


class FlextAPIPluginConfigurationError(FlextAPIPluginError):
    """Plugin configuration error."""


class FlextAPIPluginDependencyError(FlextAPIPluginError):
    """Plugin dependency error."""


# ==============================================================================
# PIPELINE EXCEPTIONS - Pipeline System
# ==============================================================================


class FlextAPIPipelineError(FlextAPIError):
    """Base class for pipeline exceptions."""


class FlextAPIPipelineExecutionError(FlextAPIPipelineError):
    """Pipeline execution failure."""


class FlextAPIPipelineConfigurationError(FlextAPIPipelineError):
    """Pipeline configuration error."""


class FlextAPIPipelineValidationError(FlextAPIPipelineError):
    """Pipeline validation error."""


# ==============================================================================
# SYSTEM EXCEPTIONS - System Management
# ==============================================================================


class FlextAPISystemError(FlextAPIError):
    """Base class for system exceptions."""


class FlextAPIMaintenanceModeError(FlextAPISystemError):
    """Maintenance mode error."""


class FlextAPIHealthCheckError(FlextAPISystemError):
    """Health check failure."""


class FlextAPIBackupError(FlextAPISystemError):
    """Backup operation error."""


# ==============================================================================
# EXCEPTION FACTORY - Factory Pattern for Exception Creation
# ==============================================================================


class FlextAPIExceptionFactory:
    """Factory for creating appropriate exceptions based on context."""

    @staticmethod
    def create_domain_validation_error(
        message: str, field: str | None = None
    ) -> FlextAPIDomainValidationError:
        """Create domain validation error with field context."""
        context = {"field": field} if field else {}
        return FlextAPIDomainValidationError(message, context=context)

    @staticmethod
    def create_not_found_error(
        resource: str, identifier: str | None = None
    ) -> FlextAPINotFoundError:
        """Create not found error for HTTP responses."""
        return FlextAPINotFoundError(resource, identifier)

    @staticmethod
    def create_authentication_error(
        reason: str | None = None,
    ) -> FlextAPIAuthenticationError:
        """Create authentication error with reason."""
        message = "Authentication failed"
        if reason:
            message += f": {reason}"
        return FlextAPIAuthenticationError(message, error_code="AUTH_FAILED")

    @staticmethod
    def create_repository_error(
        operation: str, entity: str, cause: Exception | None = None
    ) -> FlextAPIRepositoryError:
        """Create repository error with operation context."""
        message = f"Repository {operation} failed for {entity}"
        context = {"operation": operation, "entity": entity}
        if cause:
            context["cause"] = str(cause)
        return FlextAPIRepositoryError(message, context=context)


# ==============================================================================
# EXCEPTION MAPPER - Maps internal exceptions to HTTP responses
# ==============================================================================


class FlextAPIExceptionMapper:
    """Maps internal exceptions to appropriate HTTP exceptions."""

    @staticmethod
    def map_to_http_exception(exception: Exception) -> FlextAPIHttpError:
        """Map any exception to appropriate HTTP exception."""
        if isinstance(exception, FlextAPIHttpError):
            return exception

        if isinstance(exception, FlextAPIEntityNotFoundError):
            return FlextAPINotFoundError("Resource", str(exception))

        if isinstance(exception, FlextAPIAuthenticationError):
            return FlextAPIHttpError(str(exception), status_code=401)

        if isinstance(exception, FlextAPIAuthorizationError):
            return FlextAPIHttpError(str(exception), status_code=403)

        if isinstance(exception, FlextAPIDomainValidationError):
            return FlextAPIValidationError(str(exception))

        if isinstance(exception, FlextAPIBusinessRuleViolationError):
            return FlextAPIUnprocessableEntityError(str(exception))

        # Default to internal server error for unhandled exceptions
        return FlextAPIHttpError(
            "Internal server error",
            status_code=500,
            error_code="INTERNAL_ERROR",
        )


__all__ = [
    "FlextAPIApplicationError",
    "FlextAPIAuthenticationError",
    "FlextAPIAuthorizationError",
    "FlextAPIBackupError",
    "FlextAPIBusinessRuleViolationError",
    "FlextAPIConfigurationError",
    "FlextAPIConflictError",
    "FlextAPIConnectionError",
    "FlextAPIDatabaseError",
    "FlextAPIDomainError",
    "FlextAPIDomainValidationError",
    "FlextAPIEntityAlreadyExistsError",
    "FlextAPIEntityNotFoundError",
    "FlextAPIError",
    "FlextAPIExceptionFactory",
    "FlextAPIExceptionMapper",
    "FlextAPIExternalServiceError",
    "FlextAPIHealthCheckError",
    "FlextAPIHttpError",
    "FlextAPIInfrastructureError",
    "FlextAPIInvariantViolationError",
    "FlextAPIMaintenanceModeError",
    "FlextAPINotFoundError",
    "FlextAPIPipelineConfigurationError",
    "FlextAPIPipelineError",
    "FlextAPIPipelineExecutionError",
    "FlextAPIPipelineValidationError",
    "FlextAPIPluginConfigurationError",
    "FlextAPIPluginDependencyError",
    "FlextAPIPluginError",
    "FlextAPIPluginInstallationError",
    "FlextAPIPluginNotFoundError",
    "FlextAPIRateLimitExceededError",
    "FlextAPIRepositoryError",
    "FlextAPIServiceError",
    "FlextAPISystemError",
    "FlextAPIUnprocessableEntityError",
    "FlextAPIUseCaseError",
    "FlextAPIValidationError",
]
