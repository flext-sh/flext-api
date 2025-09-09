"""FLEXT API Models - Data models only (constants/tipos vêm de constants & typings).

Remove duplicações: usar diretamente `FlextApiConstants` e `FlextApiTypes` em vez de
classes internas de constantes/field/endpoints/status. Este módulo agora expõe
somente modelos (Request/Response/Config/Query/Storage/URL) seguindo padrão flext-core.
"""

from __future__ import annotations

from urllib.parse import urlparse

from flext_core import FlextModels, FlextResult, FlextLogger
from pydantic import BaseModel, Field, field_validator

from flext_api.constants import FlextApiConstants
from flext_api.typings import FlextApiTypes

logger = flext_logger(__name__)


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
            """Validate base URL format.

            Returns:
                str: Validated base URL.

            Raises:
                ValueError: If URL format is invalid.

            """
            if not v.strip():
                msg = "Base cannot be empty"
                raise ValueError(msg)
            if not v.startswith(("http://", "https://")):
                msg = "Base must include scheme and host"
                raise ValueError(msg)
            return v

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

    # ===================== Query / Response Builder (interface mínima) =====================
    class ResponseBuilder(BaseModel):
        """Builder de respostas simples retornando FlextResult para testes."""

        def success(
            self,
            data: object,
            message: str = "Success",
            status_code: int = 200,
        ) -> FlextResult[dict[str, object]]:
            response = {
                "success": True,
                "message": message,
                "status_code": status_code,
                "data": data,
            }
            return FlextResult[dict[str, object]].ok(response)

        def error(
            self,
            message: str,
        ) -> FlextResult[dict[str, object]]:
            return FlextResult[dict[str, object]].fail(message)

    class QueryBuilder(BaseModel):
        """Query builder mínima para cobrir testes (equals, sort_desc, paginação)."""

        filters: dict[str, object] = Field(default_factory=dict)
        sort: list[str] = Field(default_factory=list)
        page: int = 1
        page_size: int = 20

        # Métodos fluent
        def equals(self, field: str, value: object) -> FlextApiModels.QueryBuilder:
            self.filters[field] = value
            return self

        def sort_desc(self, field: str) -> FlextApiModels.QueryBuilder:
            self.sort.append(f"-{field}")
            return self

        def set_page(self, value: int) -> FlextApiModels.QueryBuilder:
            if value >= 1:
                self.page = value
            return self

        def set_page_size(self, value: int) -> FlextApiModels.QueryBuilder:
            if value >= 1:
                self.page_size = value
            return self

        def for_response(self) -> FlextApiModels.ResponseBuilder:
            return FlextApiModels.ResponseBuilder()

        # Build final dict
        def build(self) -> dict[str, object]:
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
        """Factory simples para obter um QueryBuilder (usado em testes)."""
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
            """Factory method for creating query builders.

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
            return urlparse(self.url).scheme

        @property
        def host(self) -> str:
            parsed = urlparse(self.url)
            return parsed.netloc.split(":")[0] if parsed.netloc else ""

        @property
        def port(self) -> int | None:
            return urlparse(self.url).port

        @property
        def path(self) -> str:
            parsed = urlparse(self.url)
            return parsed.path or "/"

        @property
        def query(self) -> str:
            return urlparse(self.url).query


__all__ = ["FlextApiModels"]
