"""Unified FlextApiModule facade for flext-api domain.

This module provides the single unified class FlextApiModule that follows FLEXT standards
and provides a comprehensive facade for all flext-api functionality.
Following FLEXT standards: single class per module, uses flext-core exclusively.
"""

from __future__ import annotations

from typing import override

from flext_core import FlextLogger, FlextResult, FlextService

from .constants import FlextApiConstants
from .exceptions import FlextApiExceptions
from .typings import FlextApiTypings

HttpStatusCode = FlextApiTypings.HttpStatusCode
JsonObject = FlextApiTypings.JsonObject


class FlextApiModule(FlextService[FlextResult[object]]):
    """Unified facade for all flext-api domain functionality.

    Single responsibility class providing all HTTP/API operations
    following FLEXT standards with nested helper classes.
    """

    @override
    def __init__(self) -> None:
        """Initialize FlextApiModule with flext-core integration."""
        super().__init__()
        self._logger = FlextLogger(__name__)

    class _HttpValidationHelper:
        """HTTP validation utilities nested helper class."""

        @staticmethod
        def is_success_status(status_code: HttpStatusCode) -> bool:
            """Check if HTTP status code indicates success (2xx range)."""
            return (
                FlextApiConstants.HTTP_SUCCESS_MIN
                <= status_code
                <= FlextApiConstants.HTTP_SUCCESS_MAX
            )

        @staticmethod
        def is_client_error_status(status_code: HttpStatusCode) -> bool:
            """Check if HTTP status code indicates client error (4xx range)."""
            return (
                FlextApiConstants.HTTP_CLIENT_ERROR_MIN
                <= status_code
                <= FlextApiConstants.HTTP_CLIENT_ERROR_MAX
            )

        @staticmethod
        def is_server_error_status(status_code: HttpStatusCode) -> bool:
            """Check if HTTP status code indicates server error (5xx range)."""
            return (
                FlextApiConstants.HTTP_SERVER_ERROR_MIN
                <= status_code
                <= FlextApiConstants.HTTP_SERVER_ERROR_MAX
            )

    class _ResponseBuilder:
        """HTTP response building utilities nested helper class."""

        @staticmethod
        def create_success_response(
            data: object = None, message: str = "Success"
        ) -> JsonObject:
            """Create standardized success response."""
            return {
                "status": "success",
                "data": data,
                "message": message,
                "error": None,
            }

        @staticmethod
        def create_error_response(
            message: str, error_code: str | None = None
        ) -> JsonObject:
            """Create standardized error response."""
            response: JsonObject = {
                "status": "error",
                "data": None,
                "message": message,
                "error": message,
            }
            if error_code:
                response["error_code"] = error_code
            return response

    class _ErrorFactory:
        """HTTP error creation utilities nested helper class."""

        @staticmethod
        def create_http_error(
            message: str,
            status_code: HttpStatusCode = 500,
            url: str | None = None,
            method: str | None = None,
        ) -> FlextApiExceptions.HttpError:
            """Create HTTP error with context."""
            return FlextApiExceptions.HttpError(
                message=message, status_code=status_code, url=url, method=method
            )

        @staticmethod
        def create_validation_error(
            message: str, status_code: HttpStatusCode = 400
        ) -> FlextApiExceptions.ValidationError:
            """Create HTTP validation error."""
            return FlextApiExceptions.ValidationError(
                message=message, status_code=status_code
            )

        @staticmethod
        def create_auth_error(
            message: str, status_code: HttpStatusCode = 401
        ) -> FlextApiExceptions.AuthenticationError:
            """Create HTTP authentication error."""
            return FlextApiExceptions.AuthenticationError(
                message=message, status_code=status_code
            )

    def is_success_status(self, status_code: HttpStatusCode) -> bool:
        """Check if HTTP status code indicates success."""
        return self._HttpValidationHelper.is_success_status(status_code)

    def is_client_error_status(self, status_code: HttpStatusCode) -> bool:
        """Check if HTTP status code indicates client error."""
        return self._HttpValidationHelper.is_client_error_status(status_code)

    def is_server_error_status(self, status_code: HttpStatusCode) -> bool:
        """Check if HTTP status code indicates server error."""
        return self._HttpValidationHelper.is_server_error_status(status_code)

    def create_success_response(
        self, data: object = None, message: str = "Success"
    ) -> JsonObject:
        """Create standardized success response."""
        return self._ResponseBuilder.create_success_response(data, message)

    def create_error_response(
        self, message: str, error_code: str | None = None
    ) -> JsonObject:
        """Create standardized error response."""
        return self._ResponseBuilder.create_error_response(message, error_code)

    def create_http_error(
        self,
        message: str,
        status_code: HttpStatusCode = 500,
        url: str | None = None,
        method: str | None = None,
    ) -> FlextApiExceptions.HttpError:
        """Create HTTP error with context."""
        return self._ErrorFactory.create_http_error(message, status_code, url, method)

    def create_validation_error(
        self, message: str, status_code: HttpStatusCode = 400
    ) -> FlextApiExceptions.ValidationError:
        """Create HTTP validation error."""
        return self._ErrorFactory.create_validation_error(message, status_code)

    def create_auth_error(
        self, message: str, status_code: HttpStatusCode = 401
    ) -> FlextApiExceptions.AuthenticationError:
        """Create HTTP authentication error."""
        return self._ErrorFactory.create_auth_error(message, status_code)

    def validate_status_code(
        self, status_code: HttpStatusCode
    ) -> FlextResult[HttpStatusCode]:
        """Validate HTTP status code range."""
        if (
            FlextApiConstants.HTTP_STATUS_MIN
            <= status_code
            <= FlextApiConstants.HTTP_STATUS_MAX
        ):
            return FlextResult[HttpStatusCode].ok(status_code)

        return FlextResult[HttpStatusCode].fail(
            f"Status code must be between {FlextApiConstants.HTTP_STATUS_MIN} and {FlextApiConstants.HTTP_STATUS_MAX}"
        )

    def get_status_category(self, status_code: HttpStatusCode) -> str:
        """Get HTTP status code category."""
        if self.is_success_status(status_code):
            return "success"
        if self.is_client_error_status(status_code):
            return "client_error"
        if self.is_server_error_status(status_code):
            return "server_error"
        if (
            FlextApiConstants.HTTP_INFORMATIONAL_MIN
            <= status_code
            <= FlextApiConstants.HTTP_INFORMATIONAL_MAX
        ):
            return "informational"
        if (
            FlextApiConstants.HTTP_REDIRECTION_MIN
            <= status_code
            <= FlextApiConstants.HTTP_REDIRECTION_MAX
        ):
            return "redirection"
        return "unknown"


__all__ = ["FlextApiModule"]
