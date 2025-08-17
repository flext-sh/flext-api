from collections.abc import Mapping
from enum import StrEnum

from _typeshed import Incomplete
from flext_core.exceptions import (
    FlextAuthenticationError,
    FlextConfigurationError,
    FlextConnectionError,
    FlextErrorMixin,
    FlextProcessingError,
    FlextTimeoutError,
    FlextValidationError,
)

from flext_api.typings import FlextTypes

__all__ = [
    "FlextApiAuthenticationError",
    "FlextApiAuthorizationError",
    "FlextApiBuilderError",
    "FlextApiConfigurationError",
    "FlextApiConnectionError",
    "FlextApiError",
    "FlextApiNotFoundError",
    "FlextApiProcessingError",
    "FlextApiRateLimitError",
    "FlextApiRequestError",
    "FlextApiResponseError",
    "FlextApiStorageError",
    "FlextApiTimeoutError",
    "FlextApiValidationError",
    "create_error_response",
    "map_http_status_to_exception",
]

class FlextApiErrorCodes(StrEnum):
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

class FlextApiError(FlextErrorMixin, Exception):
    status_code: Incomplete
    def __init__(
        self,
        message: str = "flext_api error",
        *,
        status_code: int = 500,
        code: FlextApiErrorCodes | None = None,
        context: Mapping[str, object] | None = None,
        **extra_context: object,
    ) -> None: ...
    def to_http_response(self) -> FlextTypes.Core.JsonDict: ...

class FlextApiValidationError(FlextValidationError):
    status_code: Incomplete
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
    ) -> None: ...
    def to_http_response(self) -> FlextTypes.Core.JsonDict: ...

class FlextApiAuthenticationError(FlextAuthenticationError):
    status_code: Incomplete
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
    ) -> None: ...
    def to_http_response(self) -> FlextTypes.Core.JsonDict: ...

class FlextApiAuthorizationError(FlextApiError):
    def __init__(
        self,
        message: str = "Insufficient permissions",
        *,
        required_permission: str | None = None,
        user_permissions: list[str] | None = None,
        endpoint: str | None = None,
        context: Mapping[str, object] | None = None,
        **extra_context: object,
    ) -> None: ...

class FlextApiConfigurationError(FlextConfigurationError):
    status_code: Incomplete
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
    ) -> None: ...
    def to_http_response(self) -> FlextTypes.Core.JsonDict: ...

class FlextApiConnectionError(FlextConnectionError):
    status_code: Incomplete
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
    ) -> None: ...
    def to_http_response(self) -> FlextTypes.Core.JsonDict: ...

class FlextApiProcessingError(FlextProcessingError):
    status_code: Incomplete
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
    ) -> None: ...
    def to_http_response(self) -> FlextTypes.Core.JsonDict: ...

class FlextApiTimeoutError(FlextTimeoutError):
    status_code: Incomplete
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
    ) -> None: ...
    def to_http_response(self) -> FlextTypes.Core.JsonDict: ...

class FlextApiRequestError(FlextApiError):
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
    ) -> None: ...

class FlextApiResponseError(FlextApiError):
    def __init__(
        self,
        message: str = "API response error",
        *,
        status_code: int = 502,
        response_body: str | None = None,
        content_type: str | None = None,
        context: Mapping[str, object] | None = None,
        **extra_context: object,
    ) -> None: ...

class FlextApiStorageError(FlextApiError):
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
    ) -> None: ...

class FlextApiBuilderError(FlextApiError):
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
    ) -> None: ...

class FlextApiRateLimitError(FlextApiError):
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
    ) -> None: ...

class FlextApiNotFoundError(FlextApiError):
    def __init__(
        self,
        message: str = "Resource not found",
        *,
        resource_type: str | None = None,
        resource_id: str | None = None,
        endpoint: str | None = None,
        context: Mapping[str, object] | None = None,
        **extra_context: object,
    ) -> None: ...

def create_error_response(
    exception: FlextApiError, *, include_traceback: bool = False
) -> FlextTypes.Core.JsonDict: ...
def map_http_status_to_exception(
    status_code: int, message: str = "", **context: object
) -> (
    FlextApiError
    | FlextApiAuthenticationError
    | FlextApiProcessingError
    | FlextApiConnectionError
    | FlextApiTimeoutError
): ...
