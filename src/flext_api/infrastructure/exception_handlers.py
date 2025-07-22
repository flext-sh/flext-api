"""SOLID-compliant exception handling for FLEXT API.

This module implements the Open/Closed Principle by providing extensible
exception handlers that can be added without modifying existing code.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import Request, status
from fastapi.responses import JSONResponse
from flext_observability.logging import get_logger
from pydantic import ValidationError

if TYPE_CHECKING:
    from fastapi import FastAPI

logger = get_logger(__name__)


# ==============================================================================
# OPEN/CLOSED PRINCIPLE: Extensible Exception Handlers
# ==============================================================================


class BaseExceptionHandler:
    """Base class for exception handlers (OCP compliance)."""

    def __init__(self) -> None:
        """Initialize base exception handler."""
        self.logger = get_logger(self.__class__.__module__)

    async def handle(self, request: Request, exc: Exception) -> JSONResponse:
        """Handle exception and return JSON response."""
        msg = "Subclasses must implement handle method"
        raise NotImplementedError(msg)

    def get_exception_type(self) -> type[Exception]:
        """Get the exception type this handler processes."""
        msg = "Subclasses must implement get_exception_type method"
        raise NotImplementedError(msg)


class ValidationExceptionHandler(BaseExceptionHandler):
    """Handler for Pydantic validation errors (SRP compliance)."""

    def get_exception_type(self) -> type[Exception]:
        """Get the validation exception type."""
        return ValidationError

    async def handle(self, request: Request, exc: Exception) -> JSONResponse:
        """Handle validation errors with detailed error messages."""
        if not isinstance(exc, ValidationError):
            self.logger.error("Invalid exception type for ValidationExceptionHandler")
            return await self._handle_generic_error(request, exc)

        self.logger.warning(
            "Validation error on %s %s: %s",
            request.method,
            request.url.path,
            exc.errors(),
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": "Validation error",
                "errors": exc.errors(),
                "type": "validation_error",
                "timestamp": self._get_timestamp(),
            },
        )

    async def _handle_generic_error(
        self, request: Request, exc: Exception,
    ) -> JSONResponse:
        """Handle generic errors as fallback."""
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Internal server error",
                "type": "internal_error",
                "timestamp": self._get_timestamp(),
            },
        )

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import UTC, datetime

        return datetime.now(UTC).isoformat()


class HTTPExceptionHandler(BaseExceptionHandler):
    """Handler for FastAPI HTTP exceptions (SRP compliance)."""

    def get_exception_type(self) -> type[Exception]:
        """Get the HTTP exception type."""
        from fastapi import HTTPException

        return HTTPException

    async def handle(self, request: Request, exc: Exception) -> JSONResponse:
        """Handle HTTP exceptions with structured responses."""
        from fastapi import HTTPException

        if not isinstance(exc, HTTPException):
            self.logger.error("Invalid exception type for HTTPExceptionHandler")
            return await self._handle_generic_error(request, exc)

        self.logger.warning(
            "HTTP exception on %s %s: %d - %s",
            request.method,
            request.url.path,
            exc.status_code,
            exc.detail,
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "type": "http_error",
                "status_code": exc.status_code,
                "timestamp": self._get_timestamp(),
            },
        )

    async def _handle_generic_error(
        self, request: Request, exc: Exception,
    ) -> JSONResponse:
        """Handle generic errors as fallback."""
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Internal server error",
                "type": "internal_error",
                "timestamp": self._get_timestamp(),
            },
        )

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import UTC, datetime

        return datetime.now(UTC).isoformat()


class AuthenticationExceptionHandler(BaseExceptionHandler):
    """Handler for authentication-related errors (SRP compliance)."""

    def get_exception_type(self) -> type[Exception]:
        """Get authentication exception types."""
        # This would be a custom authentication exception
        return Exception  # Placeholder - would be actual auth exception

    async def handle(self, request: Request, exc: Exception) -> JSONResponse:
        """Handle authentication errors with security-appropriate responses."""
        self.logger.warning(
            "Authentication error on %s %s: %s",
            request.method,
            request.url.path,
            str(exc),
        )

        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "detail": "Authentication required",
                "type": "authentication_error",
                "timestamp": self._get_timestamp(),
            },
        )

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import UTC, datetime

        return datetime.now(UTC).isoformat()


class GenericExceptionHandler(BaseExceptionHandler):
    """Handler for all other unhandled exceptions (SRP compliance)."""

    def get_exception_type(self) -> type[Exception]:
        """Get the generic exception type."""
        return Exception

    async def handle(self, request: Request, exc: Exception) -> JSONResponse:
        """Handle unexpected exceptions with safe error responses."""
        # Log the full exception for debugging
        self.logger.error(
            "Unhandled exception on %s %s",
            request.method,
            request.url.path,
            exc_info=exc,
        )

        # Return generic error to avoid leaking internal details
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Internal server error",
                "type": "internal_error",
                "timestamp": self._get_timestamp(),
            },
        )

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import UTC, datetime

        return datetime.now(UTC).isoformat()


# ==============================================================================
# SINGLE RESPONSIBILITY PRINCIPLE: Exception Handler Factory
# ==============================================================================


class ExceptionHandlerFactory:
    """Factory for configuring exception handlers (SRP compliance)."""

    def __init__(self) -> None:
        """Initialize exception handler factory."""
        self.handlers: list[BaseExceptionHandler] = []
        self._register_default_handlers()

    def _register_default_handlers(self) -> None:
        """Register default exception handlers."""
        self.handlers.extend(
            [
                ValidationExceptionHandler(),
                HTTPExceptionHandler(),
                AuthenticationExceptionHandler(),
                GenericExceptionHandler(),  # This should be last (catch-all)
            ],
        )

    def register_handler(self, handler: BaseExceptionHandler) -> None:
        """Register a custom exception handler (OCP compliance).

        Args:
            handler: Custom exception handler to register

        """
        # Insert before the generic handler (which should be last)
        self.handlers.insert(-1, handler)
        logger.info(
            "Registered custom exception handler: %s", handler.__class__.__name__,
        )

    def configure_handlers(self, app: FastAPI) -> None:
        """Configure all exception handlers on the FastAPI app.

        Args:
            app: FastAPI application instance

        """
        for handler in self.handlers:
            exception_type = handler.get_exception_type()

            # Create a closure to capture the handler
            async def exception_handler(
                request: Request,
                exc: Exception,
                handler_instance: BaseExceptionHandler = handler,
            ) -> JSONResponse:
                return await handler_instance.handle(request, exc)

            app.add_exception_handler(exception_type, exception_handler)

            logger.info(
                "Configured exception handler %s for %s",
                handler.__class__.__name__,
                exception_type.__name__,
            )


# ==============================================================================
# DEPENDENCY INVERSION PRINCIPLE: Factory Function
# ==============================================================================


def create_exception_handler_factory() -> ExceptionHandlerFactory:
    """Create exception handler factory with default configuration.

    Returns:
        Configured exception handler factory

    """
    factory = ExceptionHandlerFactory()
    logger.info(
        "Created exception handler factory with %d handlers", len(factory.handlers),
    )
    return factory


# Export public interface
__all__ = [
    "AuthenticationExceptionHandler",
    "BaseExceptionHandler",
    "ExceptionHandlerFactory",
    "GenericExceptionHandler",
    "HTTPExceptionHandler",
    "ValidationExceptionHandler",
    "create_exception_handler_factory",
]
