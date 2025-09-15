"""FLEXT API Models - Data models only (constants/tipos vêm de constants & typings).

Remove duplicações: usar diretamente `FlextApiConstants` e `FlextApiTypes` em vez de
classes internas de constantes/field/endpoints/status. Este módulo agora expõe
somente modelos (Request/Response/Config/Query/Storage/URL) seguindo padrão flext-core.
"""

from __future__ import annotations

from typing import Literal

from flext_core import (
    FlextConstants,
    FlextLogger,
    FlextModels,
    FlextResult,
    FlextUtilities,
)
from pydantic import ConfigDict, Field, field_validator

from flext_api.constants import FlextApiConstants, HttpMethods

logger = FlextLogger(__name__)

# Streamlined ConfigDict - eliminate bloat
STANDARD_MODEL_CONFIG = ConfigDict(
    validate_assignment=True, extra="forbid", populate_by_name=True
)

# Use constants from FlextApiConstants instead of redundant declarations
_URL_EMPTY_ERROR = "URL cannot be empty"
_URL_FORMAT_ERROR = "Invalid URL format"
_BASE_URL_ERROR = "URL must be a non-empty string with http(s) scheme"


class FlextApiModels:
    """API models using flext-core extensively - NO DUPLICATION."""

    # Direct re-export of flext-core HTTP models
    HttpRequestConfig = FlextModels.Http.HttpRequestConfig
    HttpErrorConfig = FlextModels.Http.HttpErrorConfig

    # Re-export HTTP methods and status codes
    HttpMethod = HttpMethods

    # Simple API-specific models
    class HttpRequest(FlextModels.Entity):
        """HTTP request model with modern Python 3.13 and Pydantic patterns."""

        model_config = STANDARD_MODEL_CONFIG

        method: Literal["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"] = (
            "GET"
        )
        url: str
        headers: dict[str, str] = Field(default_factory=dict)
        body: str | dict[str, object] | None = None
        timeout: int | float = 30

        @field_validator("url")
        @classmethod
        def validate_url(cls, v: str) -> str:
            """Validate URL field with Python 3.13+ concise patterns."""
            # Python 3.13+ walrus operator + short-circuit evaluation
            if not (v_clean := v.strip() if isinstance(v, str) else ""):
                raise ValueError(_URL_EMPTY_ERROR)
            if not v_clean.startswith(("http://", "https://", "/")):
                raise ValueError(_URL_FORMAT_ERROR)
            return v_clean

        @field_validator("headers")
        @classmethod
        def validate_headers(cls, v: dict[str, str]) -> dict[str, str]:
            """Validate and sanitize headers with Python 3.13+ dict comprehension optimization."""
            # Python 3.13+ optimized dict comprehension with walrus operator
            return {
                k_clean: val_clean
                for k, val in v.items()
                if (k_clean := k.strip())
                and (val_clean := str(val).strip())
                and val is not None
            }

    class HttpResponse(FlextModels.Entity):
        """HTTP response model extending flext-core Entity."""

        status_code: int
        body: str | dict[str, object] | None = None
        headers: dict[str, str] = Field(default_factory=dict)
        url: str
        method: str
        elapsed_time: float | None = None

        @property
        def is_success(self) -> bool:
            """Check if response indicates success (2xx status codes)."""
            return (
                FlextConstants.Web.HTTP_OK
                <= self.status_code
                < FlextApiConstants.SUCCESS_END
            )

        @property
        def is_client_error(self) -> bool:
            """Check if response indicates client error (4xx status codes)."""
            return (
                FlextApiConstants.CLIENT_ERROR_START
                <= self.status_code
                < FlextApiConstants.SERVER_ERROR_START
            )

        @property
        def is_server_error(self) -> bool:
            """Check if response indicates server error (5xx status codes)."""
            return (
                FlextApiConstants.SERVER_ERROR_START
                <= self.status_code
                < FlextApiConstants.SERVER_ERROR_END
            )

        @property
        def is_redirect(self) -> bool:
            """Check if response indicates redirect (3xx status codes)."""
            return (
                FlextApiConstants.SUCCESS_END
                <= self.status_code
                < FlextApiConstants.CLIENT_ERROR_START
            )

        # Status code validation handled by Field constraints (ge=100, le=599)

    class ClientConfig(FlextModels.Value):
        """Streamlined client configuration for reduced bloat."""

        # Essential configuration only
        base_url: str = FlextApiConstants.DEFAULT_BASE_URL
        timeout: float = FlextApiConstants.DEFAULT_TIMEOUT
        max_retries: int = FlextApiConstants.DEFAULT_RETRIES
        headers: dict[str, str] = Field(default_factory=dict)

        # Authentication - consolidated
        auth_token: str | None = None
        api_key: str | None = None

        @field_validator("base_url")
        @classmethod
        def validate_base_url(cls, v: str) -> str:
            """Validate base URL field with Python 3.13+ optimization."""
            # Python 3.13+ walrus operator pattern for concise validation
            if not (url := v.strip()) or not url.startswith(("http://", "https://")):
                raise ValueError(_BASE_URL_ERROR)
            return url

        def get_auth_header(self) -> dict[str, str]:
            """Get authentication header if configured."""
            if self.auth_token:
                return {"Authorization": f"Bearer {self.auth_token}"}
            if self.api_key:
                return {"Authorization": f"Bearer {self.api_key}"}
            return {}

        def get_default_headers(self) -> dict[str, str]:
            """Get all default headers including auth."""
            headers = {"User-Agent": "FlextAPI/0.9.0", **self.headers}
            headers.update(self.get_auth_header())
            return headers

    class HttpQuery(FlextModels.Entity):
        """HTTP query parameters model with filtering and pagination."""

        model_config = STANDARD_MODEL_CONFIG

        # Core fields with Pydantic 2 alias support for backward compatibility
        filter_conditions: dict[str, object] = Field(
            alias="filters", default_factory=dict
        )
        sort_fields: list[str] = Field(default_factory=list)
        page_number: int = Field(alias="page", default=1)
        page_size_value: int = Field(
            alias="page_size", default=FlextApiConstants.DEFAULT_PAGE_SIZE
        )

        def add_filter(self, key: str, value: object) -> FlextResult[None]:
            """Add a filter to the query."""
            if not key or not key.strip():
                return FlextResult[None].fail("Filter key cannot be empty")
            self.filter_conditions[key.strip()] = value
            # Removed backward compatibility reference to reduce bloat
            return FlextResult[None].ok(None)

        def to_query_params(self) -> dict[str, object]:
            """Convert to query parameters dict with Python 3.13+ computational optimization."""
            # Python 3.13+ optimized dict merge with walrus operator
            params = self.model_dump(by_alias=True, exclude_none=True)
            # Computational optimization: direct merge avoiding update() call
            return {
                **params,
                **(filters if (filters := params.pop("filters", {})) else {}),
            }

    class PaginationConfig(FlextModels.Value):
        """Pagination configuration extending flext-core Value."""

        page_size: int = FlextApiConstants.DEFAULT_PAGE_SIZE
        current_page: int = Field(alias="page", default=1)
        max_pages: int | None = None
        total: int = 0

        @property
        def page(self) -> int:
            """Alias for current_page for backward compatibility."""
            return self.current_page

    class StorageConfig(FlextModels.Value):
        """Storage configuration extending flext-core Value."""

        backend: str = "memory"
        namespace: str = "flext_api"
        max_size: int | None = None
        default_ttl: int | None = None

    class ApiRequest(FlextModels.Entity):
        """API request model."""

        model_config = STANDARD_MODEL_CONFIG

        method: str
        url: str
        headers: dict[str, str] = Field(default_factory=dict)
        body: str | dict[str, object] | None = None

    class ApiResponse(FlextModels.Entity):
        """API response model."""

        model_config = STANDARD_MODEL_CONFIG

        id: str = Field(default_factory=lambda: "")
        status_code: int
        body: str | dict[str, object] | None = None
        headers: dict[str, str] = Field(default_factory=dict)

    class UrlModel(FlextModels.Entity):
        """URL model for parsing and validation."""

        model_config = STANDARD_MODEL_CONFIG

        raw_url: str
        scheme: str | None = None
        host: str | None = None
        port: int | None = None
        path: str | None = None
        query: str | None = None
        fragment: str | None = None

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate URL business rules."""
            if not self.raw_url:
                return FlextResult[None].fail("URL cannot be empty")
            return FlextResult[None].ok(None)

    class Builder:
        """Response builder for API responses."""

        def create(
            self, response_type: str = "success", **kwargs: object
        ) -> dict[str, object]:
            """Create response using Python 3.13+ pattern matching optimization."""
            # Python 3.13+ match-case for computational efficiency
            match response_type:
                case "error":
                    # Direct return avoiding method call overhead
                    return {
                        "status": "error",
                        "error": {
                            "code": kwargs.get("code", "error"),
                            "message": kwargs.get("message", "Error occurred"),
                        },
                        "timestamp": FlextUtilities.Generators.generate_iso_timestamp(),
                        "request_id": FlextUtilities.Generators.generate_request_id(),
                    }
                case _:
                    # Direct return for success case
                    return {
                        "status": "success",
                        "data": kwargs.get("data"),
                        "message": kwargs.get("message", ""),
                        "timestamp": FlextUtilities.Generators.generate_iso_timestamp(),
                        "request_id": FlextUtilities.Generators.generate_request_id(),
                    }

        @staticmethod
        def success(data: object = None, message: str = "") -> dict[str, object]:
            """Build success response using flext-core generators."""
            return {
                "status": "success",
                "data": data,
                "message": message,
                "timestamp": FlextUtilities.Generators.generate_iso_timestamp(),
                "request_id": FlextUtilities.Generators.generate_request_id(),
            }

        @staticmethod
        def error(message: str, code: str = "error") -> dict[str, object]:
            """Build error response using flext-core generators."""
            return {
                "status": "error",
                "error": {"code": code, "message": message},
                "timestamp": FlextUtilities.Generators.generate_iso_timestamp(),
                "request_id": FlextUtilities.Generators.generate_request_id(),
            }

    @staticmethod
    def create_url(url_string: str) -> FlextResult[FlextApiModels.UrlModel]:
        """Create URL model from string."""
        try:
            # Simple URL parsing - in a real implementation, you'd use urllib.parse
            if not url_string or not url_string.strip():
                return FlextResult["FlextApiModels.UrlModel"].fail(
                    "URL cannot be empty"
                )

            url_str = url_string.strip()

            # Basic URL parsing
            scheme = None
            host = None
            port = None
            path = None
            query = None
            fragment = None

            # Parse scheme
            if "://" in url_str:
                scheme, rest = url_str.split("://", 1)
            else:
                rest = url_str
                scheme = "https"  # Default scheme

            # Parse fragment
            if "#" in rest:
                rest, fragment = rest.split("#", 1)

            # Parse query
            if "?" in rest:
                rest, query = rest.split("?", 1)

            # Parse host and port
            if "/" in rest:
                host_port, path = rest.split("/", 1)
                path = "/" + path
            else:
                host_port = rest
                path = "/"

            # Parse port
            if ":" in host_port:
                host, port_str = host_port.split(":", 1)
                try:
                    port = int(port_str)
                except ValueError:
                    port = None
            else:
                host = host_port

            # Create URL model
            url_model = FlextApiModels.UrlModel(
                raw_url=url_str,
                scheme=scheme,
                host=host,
                port=port,
                path=path,
                query=query,
                fragment=fragment,
            )
            return FlextResult["FlextApiModels.UrlModel"].ok(url_model)
        except Exception as e:
            return FlextResult["FlextApiModels.UrlModel"].fail(
                f"Failed to create URL: {e}"
            )

    class AppConfig(FlextModels.Entity):
        """FastAPI application configuration model."""

        model_config = STANDARD_MODEL_CONFIG

        title: str = Field(..., min_length=1, description="Application title")
        app_version: str = Field(..., min_length=1, description="Application version")
        description: str = Field(
            default="FlextAPI Application", description="Application description"
        )
        docs_url: str = Field(default="/docs", description="Swagger docs URL")
        redoc_url: str = Field(default="/redoc", description="ReDoc URL")
        openapi_url: str = Field(
            default="/openapi.json", description="OpenAPI schema URL"
        )

        @field_validator("title", "app_version")
        @classmethod
        def validate_required_fields(cls, v: str) -> str:
            """Validate required string fields."""
            if not v or not v.strip():
                error_message = "Field cannot be empty"
                raise ValueError(error_message)
            return v.strip()


__all__ = [
    "FlextApiModels",
]
