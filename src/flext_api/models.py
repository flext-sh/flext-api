"""FLEXT API Models - Data models only (constants/tipos vêm de constants & typings).

Remove duplicações: usar diretamente `FlextApiConstants` e `FlextApiTypes` em vez de
classes internas de constantes/field/endpoints/status. Este módulo agora expõe
somente modelos (Request/Response/Config/Query/Storage/URL) seguindo padrão flext-core.
"""

from __future__ import annotations

from urllib.parse import urlparse

from flext_core import FlextLogger, FlextModels
from pydantic import BaseModel, Field, field_validator

from flext_api.constants import FlextApiConstants
from flext_api.typings import FlextApiTypes
from flext_api.utilities import FlextApiUtilities

logger = FlextLogger(__name__)


class FlextApiModels(FlextModels):
    """Namespace de modelos HTTP da FLEXT API.

    Somente modelos/VOs. Para constantes use `flext_api.constants.FlextApiConstants`.
    Para tipos use `flext_api.typings.FlextApiTypes`.
    """

    class ClientConfig(BaseModel):
        """HTTP client configuration model."""

        base_url: str = Field(default="", description="Base URL for HTTP requests")
        timeout: float = Field(default=30.0, description="Request timeout in seconds")
        max_retries: int = Field(default=3, description="Maximum retry attempts")
        headers: FlextApiTypes.HttpHeaders = Field(
            default_factory=dict, description="Default headers"
        )
        # Integrated features (ex-plugins)
        enable_caching: bool = Field(
            default=False, description="Enable in-memory GET cache"
        )
        cache_ttl: int = Field(default=60, description="Cache TTL seconds")
        cache_max_size: int = Field(default=256, description="Max cache entries")

        enable_rate_limit: bool = Field(
            default=False, description="Enable token bucket rate limiting"
        )
        rate_calls_per_second: float = Field(
            default=10.0, description="Rate limit tokens per second"
        )
        rate_burst_size: int = Field(default=20, description="Rate limit burst size")

        enable_retry: bool = Field(default=True, description="Enable automatic retries")
        retry_backoff_factor: float = Field(
            default=2.0, description="Exponential backoff factor"
        )
        retry_status_codes: list[int] = Field(
            default_factory=lambda: [500, 502, 503, 504],
            description="Status codes that trigger retry",
        )

        auth_type: str | None = Field(
            default=None, description="Auth type: bearer|basic"
        )
        auth_token: str | None = Field(default=None, description="Bearer token")
        auth_username: str | None = Field(
            default=None, description="Basic auth username"
        )
        auth_password: str | None = Field(
            default=None, description="Basic auth password"
        )

        enable_circuit_breaker: bool = Field(
            default=False, description="Enable circuit breaker"
        )
        circuit_failure_threshold: int = Field(
            default=5, description="Failures before open"
        )
        circuit_recovery_timeout: float = Field(
            default=60.0, description="Seconds to half-open"
        )

        log_requests: bool = Field(default=False, description="Log outgoing requests")
        log_responses: bool = Field(default=False, description="Log responses")
        log_errors: bool = Field(default=True, description="Log errors")

        verify_ssl: bool = Field(default=True, description="Verify SSL certificates")

        @field_validator("base_url")
        @classmethod
        def validate_base_url(cls, v: str) -> str:
            """Validate base URL format using FlextApiUtilities.

            Returns:
                str: Validated base URL.

            Raises:
                ValueError: If URL format is invalid.

            """
            validation_result = FlextApiUtilities.HttpValidator.validate_url(v)
            if not validation_result.success:
                raise ValueError(validation_result.error or "Invalid URL format")
            return validation_result.value

        @field_validator("timeout")
        @classmethod
        def validate_timeout(cls, v: float) -> float:
            """Validate timeout is positive.

            Returns:
                float: Validated timeout value.

            Raises:
                ValueError: If timeout is not positive.

            """
            if v <= 0:
                msg = "Timeout must be greater than 0"
                raise ValueError(msg)
            return v

        @field_validator("max_retries")
        @classmethod
        def validate_max_retries(cls, v: int) -> int:
            """Validate max_retries is non-negative.

            Returns:
                int: Validated max retries value.

            Raises:
                ValueError: If max_retries is negative.

            """
            if v < 0:
                msg = "Max retries must be greater than or equal to 0"
                raise ValueError(msg)
            return v

        @field_validator(
            "cache_ttl",
            "cache_max_size",
            "rate_burst_size",
            "circuit_failure_threshold",
            mode="before",
        )
        @classmethod
        def validate_positive_int(cls, v: int) -> int:
            """Validate that integer value is non-negative.

            Args:
                v: Integer value to validate.

            Returns:
                int: Validated integer value.

            Raises:
                ValueError: If value is negative.

            """
            if v < 0:
                msg = "Value must be non-negative"
                raise ValueError(msg)
            return v

        @field_validator(
            "rate_calls_per_second",
            "retry_backoff_factor",
            "circuit_recovery_timeout",
            mode="before",
        )
        @classmethod
        def validate_positive_float(cls, v: float) -> float:
            """Validate that float value is greater than zero.

            Args:
                v: Float value to validate.

            Returns:
                float: Validated float value.

            Raises:
                ValueError: If value is not greater than zero.

            """
            if v <= 0:
                msg = "Value must be greater than zero"
                raise ValueError(msg)
            return v

    class ApiRequest(BaseModel):
        """API request model."""

        id: str = Field(..., description="Request identifier")
        method: FlextApiConstants.HttpMethods = Field(..., description="HTTP method")
        url: str = Field(..., description="Request URL")
        headers: FlextApiTypes.HttpHeaders | None = Field(
            default=None, description="Request headers"
        )
        body: FlextApiTypes.Request.RequestBody = Field(
            default=None, description="Request body"
        )

        @field_validator("url")
        @classmethod
        def validate_url(cls, v: str) -> str:
            """Validate URL is not empty.

            Returns:
                str: Validated URL.

            Raises:
                ValueError: If URL is empty.

            """
            if not v:
                msg = "URL cannot be empty"
                raise ValueError(msg)
            return v

    class HttpResponse(BaseModel):
        """HTTP response model."""

        status_code: int = Field(..., description="HTTP status code")
        body: FlextApiTypes.Request.RequestBody = Field(
            default=None, description="Response body"
        )
        headers: FlextApiTypes.HttpHeaders | None = Field(
            default=None, description="Response headers"
        )
        url: str = Field(..., description="Request URL")
        method: str = Field(..., description="HTTP method")

        @field_validator("status_code")
        @classmethod
        def validate_status_code(cls, v: int) -> int:
            """Validate HTTP status code range.

            Returns:
                int: Validated HTTP status code.

            Raises:
                ValueError: If status code is outside valid range (100-599).

            """
            min_code = 100
            max_code = 600
            if v < min_code or v >= max_code:
                msg = f"Status code must be between {min_code} and {max_code - 1}"
                raise ValueError(msg)
            return v

        @property
        def is_success(self) -> bool:
            """Check if response indicates success (2xx)."""
            success_min = 200
            success_max = 300
            return success_min <= self.status_code < success_max

        @property
        def is_client_error(self) -> bool:
            """Check if response indicates client error (4xx).

            Returns:
                bool: True if status code is 4xx, False otherwise.

            """
            client_error_min = 400
            client_error_max = 500
            return client_error_min <= self.status_code < client_error_max

        @property
        def is_server_error(self) -> bool:
            """Check if response indicates server error (5xx).

            Returns:
                bool: True if status code is 5xx, False otherwise.

            """
            server_error_min = 500
            server_error_max = 600
            return server_error_min <= self.status_code < server_error_max

    class HttpQuery(BaseModel):
        """HTTP query builder model."""

        filter_conditions: FlextApiTypes.Core.Dict = Field(
            default_factory=dict, description="Filter conditions"
        )
        sort_fields: FlextApiTypes.Core.StringList = Field(
            default_factory=list, description="Sort fields"
        )
        page_number: int = Field(default=1, description="Page number")
        page_size_value: int = Field(default=20, description="Page size")

        @field_validator("page_number")
        @classmethod
        def validate_page_number(cls, v: int) -> int:
            """Validate page number is positive.

            Returns:
                int: Validated page number.

            Raises:
                ValueError: If page number is less than 1.

            """
            if v < 1:
                msg = "Page number must be greater than or equal to 1"
                raise ValueError(msg)
            return v

        @field_validator("page_size_value")
        @classmethod
        def validate_page_size(cls, v: int) -> int:
            """Validate page size is within bounds.

            Returns:
                int: Validated page size.

            Raises:
                ValueError: If page size is outside valid range (1-1000).

            """
            min_size = 1
            max_size = 1000
            if v < min_size or v > max_size:
                msg = f"Page size must be between {min_size} and {max_size}"
                raise ValueError(msg)
            return v

    class Builder(BaseModel):
        """Response builder model."""

        def create(self, **kwargs: object) -> FlextApiTypes.Core.Dict:
            """Create method for building responses.

            Returns:
                FlextApiTypes.Core.Dict: Dictionary with provided kwargs.

            """
            return dict(kwargs)

    # ===================== PaginationConfig (necessário para testes) =====================
    class PaginationConfig(BaseModel):
        """Configuração de paginação usada nos testes legados."""

        data: list[object] = Field(default_factory=list)
        total: int = Field(ge=0)
        page: int = Field(ge=1)
        page_size: int = Field(ge=1)

    # ===================== Query Builder (ResponseBuilder moved to utilities.py) =====================

    class QueryBuilder(BaseModel):
        """Query builder mínima para cobrir testes (equals, sort_desc, paginação)."""

        filters: dict[str, object] = Field(default_factory=dict)
        sort: list[str] = Field(default_factory=list)
        page: int = 1
        page_size: int = 20

        # Métodos fluent
        def equals(self, field: str, value: object) -> FlextApiModels.QueryBuilder:
            """Add equality filter condition.

            Args:
                field: Field name.
                value: Field value.

            Returns:
                FlextApiModels.QueryBuilder: Self for chaining.

            """
            self.filters[field] = value
            return self

        def sort_desc(self, field: str) -> FlextApiModels.QueryBuilder:
            """Add descending sort field.

            Args:
                field: Field name to sort by.

            Returns:
                FlextApiModels.QueryBuilder: Self for chaining.

            """
            self.sort.append(f"-{field}")
            return self

        def set_page(self, value: int) -> FlextApiModels.QueryBuilder:
            """Set page number.

            Args:
                value: Page number (must be >= 1).

            Returns:
                FlextApiModels.QueryBuilder: Self for chaining.

            """
            if value >= 1:
                self.page = value
            return self

        def set_page_size(self, value: int) -> FlextApiModels.QueryBuilder:
            """Set page size.

            Args:
                value: Page size (must be >= 1).

            Returns:
                FlextApiModels.QueryBuilder: Self for chaining.

            """
            if value >= 1:
                self.page_size = value
            return self

        def for_response(self) -> FlextApiUtilities.ResponseBuilder:
            """Get response builder for this query.

            Returns:
                FlextApiUtilities.ResponseBuilder: New response builder instance.

            """
            return FlextApiUtilities.ResponseBuilder()

        # Build final dict
        def build(self) -> dict[str, object]:
            """Build final query dictionary.

            Returns:
                dict[str, object]: Query parameters dictionary.

            """
            return {
                "filters": self.filters,
                "sort": self.sort,
                "pagination": {
                    "page": self.page,
                    "page_size": self.page_size,
                },
            }

    # ===================== Factory estática usada pelos testes =====================
    @classmethod
    def for_query(cls) -> FlextApiModels.QueryBuilder:
        """Create QueryBuilder instance for tests."""
        return cls.QueryBuilder()

    class StorageConfig(BaseModel):
        """Storage configuration model."""

        backend: str = Field(default="memory", description="Storage backend type")
        namespace: str = Field(default="default", description="Storage namespace")
        host: str = Field(default="localhost", description="Storage host")
        port: int = Field(default=6379, description="Storage port")
        db: int = Field(default=0, description="Database number")
        file_path: str | None = Field(
            default=None, description="File path for FILE backend"
        )
        redis_url: str | None = Field(
            default=None, description="Redis URL for REDIS backend"
        )
        database_url: str | None = Field(
            default=None, description="Database URL for DATABASE backend"
        )
        options: FlextApiTypes.Core.Dict = Field(
            default_factory=dict, description="Additional options"
        )

    class ApiBaseService:
        """Base service class for API services."""

        def __init__(self, service_name: str = "default-service") -> None:
            """Initialize base service."""
            self._service_name = service_name

    class ApiResponse(BaseModel):
        """API response model."""

        id: str = Field(..., description="Response identifier")
        status_code: int = Field(..., description="HTTP status code")
        data: object | None = Field(default=None, description="Response data")

        @classmethod
        def create_query_builder(cls) -> FlextApiModels.HttpQuery:
            """Create query builder instance.

            Returns:
                FlextApiModels.HttpQuery: New query builder instance.

            """
            return FlextApiModels.HttpQuery()

    # Removidas classes internas de constantes/field/endpoints/status. Usar FlextApiConstants.

    class URL(BaseModel):
        """Value object de URL."""

        url: str = Field(..., description="URL string", min_length=1)

        def __str__(self) -> str:  # pragma: no cover
            """Retorna representação string do valor da URL."""
            return self.url

        @property
        def scheme(self) -> str:
            """Get URL scheme (http/https).

            Returns:
                str: URL scheme.

            """
            return urlparse(self.url).scheme

        @property
        def host(self) -> str:
            """Get URL host.

            Returns:
                str: URL host.

            """
            parsed = urlparse(self.url)
            return parsed.netloc.split(":")[0] if parsed.netloc else ""

        @property
        def port(self) -> int | None:
            """Get URL port.

            Returns:
                int | None: URL port or None if not specified.

            """
            return urlparse(self.url).port

        @property
        def path(self) -> str:
            """Get URL path.

            Returns:
                str: URL path.

            """
            parsed = urlparse(self.url)
            return parsed.path or "/"

        @property
        def query(self) -> str:
            """Get URL query string.

            Returns:
                str: URL query string.

            """
            return urlparse(self.url).query


__all__ = ["FlextApiModels"]
