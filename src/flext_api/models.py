"""FLEXT API Models - Data models only (constants/tipos vêm de constants & typings).

Remove duplicações: usar diretamente `FlextApiConstants` e `FlextApiTypes` em vez de
classes internas de constantes/field/endpoints/status. Este módulo agora expõe
somente modelos (Request/Response/Config/Query/Storage/URL) seguindo padrão flext-core.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Self

from pydantic import (
    ConfigDict,
    Field,
    computed_field,
    field_serializer,
    field_validator,
    model_validator,
)

from flext_api.constants import FlextApiConstants
from flext_api.typings import FlextApiTypes
from flext_core import (
    FlextConstants,
    FlextModels,
    FlextResult,
    FlextUtilities,
)

# Constants for HTTP status codes and validation
HTTP_NO_CONTENT = 204
HTTP_SUCCESS_MIN = 200
HTTP_SUCCESS_MAX = 300
HTTP_CLIENT_ERROR_MIN = 400
HTTP_CLIENT_ERROR_MAX = 500
HTTP_SERVER_ERROR_MIN = 500
HTTP_SERVER_ERROR_MAX = 600
MAX_RETRIES_PRODUCTION = 10
MAX_PAGE_SIZE_PERFORMANCE = 1000
MIN_PORT = 1
MAX_PORT = 65535
MASK_AUTH_THRESHOLD = 8

# Standard model configuration for all API models
STANDARD_MODEL_CONFIG = ConfigDict(
    validate_assignment=True,
    extra="forbid",
    populate_by_name=True,
)


class FlextApiModels(FlextModels):
    """API models using flext-core extensively - Pydantic models only.

    Inherits from FlextModels to avoid duplication and ensure consistency.
    Follows FLEXT standardization patterns with Pydantic 2.11 features.

    ARCHITECTURAL COMPLIANCE:
    - Inherits from FlextModels to avoid duplication
    - Uses FlextApiConstants for all defaults
    - Implements Pydantic 2.11 features
    - Uses FlextModels base classes (Entity, Value, Command, Query)
    """

    # Enhanced model configuration with Pydantic 2.11 features
    model_config = ConfigDict(
        validate_assignment=True,
        use_enum_values=True,
        arbitrary_types_allowed=True,
        extra="forbid",
        frozen=False,
        # Pydantic 2.11 enhanced features
        validate_return=True,
        ser_json_timedelta="iso8601",
        ser_json_bytes="base64",
        # Enhanced serialization
        serialize_by_alias=True,
        populate_by_name=True,
        # String processing features
        str_strip_whitespace=True,
        str_to_lower=False,
        str_to_upper=False,
        # Performance optimizations
        defer_build=False,
        # Type coercion features
        coerce_numbers_to_str=False,
        # Validation features
        validate_default=True,
        # JSON encoding
        json_encoders={
            Path: str,
        },
    )

    # Simple API-specific models extending FlextModels base classes
    class HttpRequest(FlextModels.Command):
        """HTTP request model extending FlextModels.Command."""

        url: str = Field(description="Request URL")
        method: str = Field(
            default=FlextApiConstants.HttpMethod.GET, description="HTTP method"
        )
        headers: FlextApiTypes.Headers = Field(
            default_factory=dict, description="Request headers"
        )
        body: FlextApiTypes.RequestBody | None = Field(
            default=None, description="Request body"
        )
        timeout: FlextApiTypes.Timeout = Field(
            default=FlextApiConstants.DEFAULT_TIMEOUT,
            ge=FlextApiConstants.MIN_TIMEOUT,
            le=FlextApiConstants.MAX_TIMEOUT,
            description="Request timeout",
        )

        @computed_field
        def full_url(self) -> str:
            """Computed full URL with proper formatting."""
            base_url = self.url.rstrip("/")
            if not base_url.startswith(("http://", "https://")):
                return f"http://{base_url}"
            return base_url

        @computed_field
        def request_size(self) -> int:
            """Computed request body size in bytes."""
            if not self.body:
                return 0
            if isinstance(self.body, str):
                return len(self.body.encode("utf-8"))
            if isinstance(self.body, dict):
                return len(json.dumps(self.body).encode("utf-8"))
            return 0

        @computed_field
        def is_secure(self) -> bool:
            """Check if the request uses HTTPS."""
            return self.url.startswith("https://")

        @model_validator(mode="after")
        def validate_request_consistency(self) -> Self:
            """Cross-field validation for HTTP request consistency."""
            # Validate method-body consistency
            methods_without_body = {"GET", "HEAD", "DELETE"}
            if self.method in methods_without_body and self.body is not None:
                error_msg = f"HTTP {self.method} requests should not have a body"
                raise ValueError(error_msg)

            # Validate Content-Type for POST/PUT requests
            methods_with_body = {"POST", "PUT", "PATCH"}
            if self.method in methods_with_body and self.body:
                headers_lower = {k.lower(): v for k, v in self.headers.items()}
                if "content-type" not in headers_lower:
                    # Auto-add Content-Type based on body type
                    if isinstance(self.body, dict):
                        self.headers["Content-Type"] = "application/json"
                    elif isinstance(self.body, str):
                        self.headers["Content-Type"] = "text/plain"

            return self

        @field_validator("url")
        @classmethod
        def validate_url(cls, v: str) -> str:
            """Validate URL using centralized FlextModels validation."""
            # Handle empty URL case first
            if not v or not v.strip():
                msg = "Invalid URL: URL cannot be empty"
                raise ValueError(msg)

            if v.strip().startswith("/"):
                return v.strip()

            validation_result = FlextModels.create_validated_http_url(v.strip())
            if validation_result.is_failure:
                error_msg = validation_result.error or "Invalid URL"
                if "URL must start with http:// or https://" in error_msg:
                    error_msg = "Invalid URL format"
                elif "URL cannot be empty" in error_msg:
                    error_msg = "URL cannot be empty"
                elif "URL must have a valid hostname" in error_msg:
                    error_msg = "Invalid URL format"
                msg = f"Invalid URL: {error_msg}"
                raise ValueError(msg)
            url_obj = validation_result.unwrap()
            return str(url_obj.url) if hasattr(url_obj, "url") else str(url_obj)

        @field_validator("headers")
        @classmethod
        def validate_headers(cls, v: FlextApiTypes.Headers) -> FlextApiTypes.Headers:
            """Validate and sanitize headers with Python 3.13+ dict comprehension optimization."""
            # Python 3.13+ optimized dict comprehension with walrus operator
            return {
                k_clean: val_clean
                for k, val in v.items()
                if (k_clean := k.strip()) and (val_clean := str(val).strip())
            }

        @field_serializer("body")
        def serialize_body(
            self, value: FlextApiTypes.RequestBody | None
        ) -> str | dict | None:
            """Serialize request body for API transmission."""
            if value is None:
                return None
            if isinstance(value, dict):
                # Ensure all dict values are JSON serializable
                try:
                    json.dumps(value)  # Test serialization
                    return value
                except (TypeError, ValueError):
                    return str(value)
            return str(value)

    class HttpResponse(FlextModels.Entity):
        """HTTP response model extending FlextModels.Entity."""

        status_code: int = Field(
            ge=FlextApiConstants.HTTP_STATUS_MIN,
            le=FlextApiConstants.HTTP_STATUS_MAX,
            description="HTTP status code",
        )
        body: str | dict[str, object] | None = Field(
            default=None, description="Response body"
        )
        headers: dict[str, str] = Field(
            default_factory=dict, description="Response headers"
        )
        url: str = Field(description="Request URL")
        method: str = Field(description="HTTP method")
        elapsed_time: float | None = Field(
            default=None, description="Request elapsed time"
        )
        domain_events: list[object] = Field(
            default_factory=list, description="Domain events"
        )

        @computed_field
        def is_success(self) -> bool:
            """Check if response indicates success (2xx status codes)."""
            return (
                FlextApiConstants.HTTP_SUCCESS_MIN
                <= self.status_code
                <= FlextApiConstants.HTTP_SUCCESS_MAX
            )

        @computed_field
        def is_client_error(self) -> bool:
            """Check if response indicates client error (4xx status codes)."""
            return (
                FlextApiConstants.HTTP_CLIENT_ERROR_MIN
                <= self.status_code
                <= FlextApiConstants.HTTP_CLIENT_ERROR_MAX
            )

        @computed_field
        def is_server_error(self) -> bool:
            """Check if response indicates server error (5xx status codes)."""
            return (
                FlextApiConstants.HTTP_SERVER_ERROR_MIN
                <= self.status_code
                <= FlextApiConstants.HTTP_SERVER_ERROR_MAX
            )

        @computed_field
        def is_redirect(self) -> bool:
            """Check if response indicates redirect (3xx status codes)."""
            return (
                FlextApiConstants.HTTP_REDIRECTION_MIN
                <= self.status_code
                <= FlextApiConstants.HTTP_REDIRECTION_MAX
            )

        @computed_field
        def response_time_ms(self) -> float:
            """Computed response time in milliseconds."""
            return (self.elapsed_time * 1000) if self.elapsed_time else 0.0

        @computed_field
        def content_length(self) -> int:
            """Computed content length from headers or body."""
            if "content-length" in self.headers:
                try:
                    return int(self.headers["content-length"])
                except (ValueError, TypeError):
                    pass

            if self.body:
                if isinstance(self.body, str):
                    return len(self.body.encode("utf-8"))
                if isinstance(self.body, dict):
                    return len(json.dumps(self.body).encode("utf-8"))

            return 0

        @model_validator(mode="after")
        def validate_response_consistency(self) -> Self:
            """Cross-field validation for HTTP response consistency."""
            # Validate status code and body consistency
            if self.status_code == HTTP_NO_CONTENT and self.body:  # No Content
                error_msg = "HTTP 204 responses should not have a body"
                raise ValueError(error_msg)

            # Validate elapsed time
            if self.elapsed_time is not None and self.elapsed_time < 0:
                error_msg = "Elapsed time cannot be negative"
                raise ValueError(error_msg)

            return self

        @field_serializer("body")
        def serialize_response_body(
            self, value: str | dict[str, object] | None
        ) -> str | dict | None:
            """Serialize response body for storage/transmission."""
            if value is None:
                return None
            if isinstance(value, dict):
                # Ensure response dict is JSON serializable
                try:
                    json.dumps(value)
                    return value
                except (TypeError, ValueError):
                    return {"serialized_content": str(value)}
            return str(value)

    class ClientConfig(FlextModels.Value):
        """Streamlined client configuration extending FlextModels.Value."""

        # Essential configuration only
        base_url: str = Field(
            default=FlextApiConstants.DEFAULT_BASE_URL, description="Base URL"
        )
        timeout: float = Field(
            default=FlextApiConstants.DEFAULT_TIMEOUT,
            gt=FlextApiConstants.MIN_TIMEOUT,
            le=FlextApiConstants.MAX_TIMEOUT,
            description="Request timeout",
        )
        max_retries: int = Field(
            default=FlextApiConstants.DEFAULT_RETRIES,
            ge=FlextApiConstants.MIN_RETRIES,
            le=FlextApiConstants.MAX_RETRIES,
            description="Maximum retries",
        )
        headers: dict[str, str] = Field(
            default_factory=dict, description="Default headers"
        )

        # Authentication - consolidated
        auth_token: str | None = Field(default=None, description="Authentication token")
        api_key: str | None = Field(default=None, description="API key")

        @computed_field
        def has_authentication(self) -> bool:
            """Check if client has authentication configured."""
            return bool(self.auth_token or self.api_key)

        @computed_field
        def auth_type(self) -> str:
            """Determine the authentication type being used."""
            if self.auth_token:
                return "bearer_token"
            if self.api_key:
                return "api_key"
            return "none"

        @computed_field
        def timeout_ms(self) -> int:
            """Get timeout in milliseconds for compatibility."""
            return int(self.timeout * 1000)

        @model_validator(mode="after")
        def validate_client_config(self) -> Self:
            """Cross-field validation for client configuration."""
            # Validate authentication consistency
            if self.auth_token and self.api_key:
                msg = "Cannot specify both auth_token and api_key"
                raise ValueError(msg)

            # Validate retry configuration
            if self.max_retries > MAX_RETRIES_PRODUCTION:
                msg = f"Max retries should not exceed {MAX_RETRIES_PRODUCTION} for production use"
                raise ValueError(msg)

            return self

        @field_validator("base_url")
        @classmethod
        def validate_base_url(cls, v: str) -> str:
            """Validate base URL using centralized FlextModels validation."""
            validation_result = FlextModels.create_validated_http_url(v.strip())
            if validation_result.is_failure:
                error_msg = validation_result.error or "Invalid base URL"
                if (
                    "URL must start with http:// or https://" in error_msg
                    or "URL cannot be empty" in error_msg
                    or "URL must have a valid hostname" in error_msg
                ):
                    error_msg = "URL must be a non-empty string"
                msg = f"Invalid base URL: {error_msg}"
                raise ValueError(msg)

            url_obj = validation_result.unwrap()
            return str(url_obj.url) if hasattr(url_obj, "url") else str(url_obj)

        @field_serializer("auth_token", "api_key")
        def serialize_auth_fields(self, value: str | None) -> str | None:
            """Serialize authentication fields securely."""
            if value is None:
                return None
            # Mask sensitive authentication data for logging/serialization
            if len(value) <= MASK_AUTH_THRESHOLD:
                return "***MASKED***"
            return f"{value[:4]}***{value[-4:]}"

        def get_auth_header(self) -> dict[str, str]:
            """Get authentication header if configured."""
            if self.auth_token:
                return {
                    FlextApiConstants.AUTHORIZATION_HEADER: f"Bearer {self.auth_token}"
                }
            if self.api_key:
                return {
                    FlextApiConstants.AUTHORIZATION_HEADER: f"Bearer {self.api_key}"
                }
            return {}

        def get_default_headers(self) -> dict[str, str]:
            """Get all default headers including auth."""
            headers = {
                FlextApiConstants.USER_AGENT_HEADER: FlextApiConstants.DEFAULT_USER_AGENT,
                **self.headers,
            }
            headers.update(self.get_auth_header())
            return headers

    class HttpQuery(FlextModels.Query):
        """HTTP query parameters model extending FlextModels.Query."""

        # Core fields using direct Pydantic 2 field names
        filter_conditions: dict[str, object] = Field(
            default_factory=dict, description="Filter conditions"
        )
        sort_fields: list[str] = Field(default_factory=list, description="Sort fields")
        page_number: int = Field(
            default=FlextConstants.Performance.DEFAULT_PAGE_NUMBER,
            ge=FlextConstants.Performance.DEFAULT_PAGE_NUMBER,
            description="Page number",
        )
        page_size_value: int = Field(
            default=FlextApiConstants.DEFAULT_PAGE_SIZE,
            ge=FlextApiConstants.MIN_PAGE_SIZE,
            le=FlextApiConstants.MAX_PAGE_SIZE,
            description="Page size",
        )

        @computed_field
        def has_filters(self) -> bool:
            """Check if any filters are applied."""
            return bool(self.filter_conditions)

        @computed_field
        def has_sorting(self) -> bool:
            """Check if any sorting is applied."""
            return bool(self.sort_fields)

        @computed_field
        def offset(self) -> int:
            """Calculate SQL-style offset for pagination."""
            return (self.page_number - 1) * self.page_size_value

        @model_validator(mode="after")
        def validate_query_params(self) -> Self:
            """Cross-field validation for query parameters."""
            # Validate sort fields format
            for field in self.sort_fields:
                if not field.strip():
                    msg = "Sort field names cannot be empty"
                    raise ValueError(msg)

            # Validate pagination consistency
            if self.page_size_value > MAX_PAGE_SIZE_PERFORMANCE:
                msg = "Page size too large for performance"
                raise ValueError(msg)

            return self

        def add_filter(self, key: str, value: object) -> FlextResult[None]:
            """Add a filter to the query."""
            if not key or not key.strip():
                return FlextResult[None].fail("Filter key cannot be empty")
            self.filter_conditions[key.strip()] = value
            return FlextResult[None].ok(None)

        def to_query_params(self) -> dict[str, object]:
            """Convert to query parameters dict with Python 3.13+ computational optimization."""
            # Python 3.13+ optimized dict merge with walrus operator
            params = self.model_dump(exclude_none=True)
            # Computational optimization: direct merge avoiding update() call
            return {
                **params,
                **(filters if (filters := params.pop("filters", {})) else {}),
            }

    class PaginationConfig(FlextModels.Value):
        """Pagination configuration extending FlextModels.Value."""

        page_size: int = Field(
            default=FlextApiConstants.DEFAULT_PAGE_SIZE,
            ge=FlextApiConstants.MIN_PAGE_SIZE,
            le=FlextApiConstants.MAX_PAGE_SIZE,
            description="Page size",
        )
        current_page: int = Field(
            default=FlextConstants.Performance.DEFAULT_PAGE_NUMBER,
            ge=FlextConstants.Performance.DEFAULT_PAGE_NUMBER,
            description="Current page",
        )
        max_pages: int | None = Field(default=None, ge=1, description="Maximum pages")
        total: int = Field(default=0, ge=0, description="Total items")

        @computed_field
        def offset(self) -> int:
            """Calculate offset for database queries."""
            return (self.current_page - 1) * self.page_size

        @computed_field
        def has_next_page(self) -> bool:
            """Check if there's a next page available."""
            if self.max_pages is None:
                return self.total > (self.current_page * self.page_size)
            return self.current_page < self.max_pages

        @computed_field
        def has_previous_page(self) -> bool:
            """Check if there's a previous page available."""
            return self.current_page > 1

        @model_validator(mode="after")
        def validate_pagination(self) -> Self:
            """Cross-field validation for pagination configuration."""
            if self.max_pages is not None and self.current_page > self.max_pages:
                msg = "Current page cannot exceed max pages"
                raise ValueError(msg)

            if self.total > 0 and self.page_size > 0:
                calculated_max_pages = (
                    self.total + self.page_size - 1
                ) // self.page_size
                if self.current_page > calculated_max_pages:
                    msg = "Current page exceeds pages based on total items"
                    raise ValueError(msg)

            return self

    class StorageConfig(FlextModels.Value):
        """Storage configuration extending FlextModels.Value."""

        backend: str = Field(default="memory", description="Storage backend")
        namespace: str = Field(default="flext_api", description="Storage namespace")
        max_size: int | None = Field(default=None, description="Maximum storage size")
        default_ttl: int | None = Field(default=None, description="Default TTL")

        @computed_field
        def has_size_limit(self) -> bool:
            """Check if storage has size limitations."""
            return self.max_size is not None

        @computed_field
        def has_ttl(self) -> bool:
            """Check if storage has TTL configured."""
            return self.default_ttl is not None

        @model_validator(mode="after")
        def validate_storage_config(self) -> Self:
            """Cross-field validation for storage configuration."""
            if self.max_size is not None and self.max_size <= 0:
                msg = "Max size must be positive"
                raise ValueError(msg)

            if self.default_ttl is not None and self.default_ttl <= 0:
                msg = "TTL must be positive"
                raise ValueError(msg)

            return self

    class ApiRequest(FlextModels.Command):
        """API request model extending FlextModels.Command."""

        url: str = Field(description="Request URL")
        method: str = Field(
            default=FlextApiConstants.HttpMethod.GET, description="HTTP method"
        )
        headers: dict[str, str] = Field(
            default_factory=dict, description="Request headers"
        )
        body: str | dict[str, object] | None = Field(
            default=None, description="Request body"
        )

        @computed_field
        def content_type(self) -> str | None:
            """Get Content-Type header value."""
            return self.headers.get("Content-Type") or self.headers.get("content-type")

        @computed_field
        def is_json_request(self) -> bool:
            """Check if request contains JSON content."""
            content_type = self.content_type
            return bool(content_type and "application/json" in content_type)

        @model_validator(mode="after")
        def validate_api_request(self) -> Self:
            """Cross-field validation for API requests."""
            # Validate method-body consistency
            methods_without_body = {"GET", "HEAD", "DELETE"}
            if self.method in methods_without_body and self.body is not None:
                error_msg = f"HTTP {self.method} requests should not have a body"
                raise ValueError(error_msg)

            return self

    class ApiResponse(FlextModels.Entity):
        """API response model extending FlextModels.Entity."""

        status_code: int = Field(
            ge=FlextApiConstants.HTTP_STATUS_MIN,
            le=FlextApiConstants.HTTP_STATUS_MAX,
            description="HTTP status code",
        )
        body: str | dict[str, object] | None = Field(
            default=None, description="Response body"
        )
        headers: dict[str, str] = Field(
            default_factory=dict, description="Response headers"
        )
        domain_events: list[object] = Field(
            default_factory=list, description="Domain events"
        )

        @computed_field
        def is_successful(self) -> bool:
            """Check if response indicates success."""
            return HTTP_SUCCESS_MIN <= self.status_code < HTTP_SUCCESS_MAX

        @computed_field
        def content_type(self) -> str | None:
            """Get Content-Type header value."""
            return self.headers.get("Content-Type") or self.headers.get("content-type")

        @computed_field
        def is_json_response(self) -> bool:
            """Check if response contains JSON content."""
            content_type = self.content_type
            return bool(content_type and "application/json" in content_type)

        @model_validator(mode="after")
        def validate_api_response(self) -> Self:
            """Cross-field validation for API responses."""
            # Validate status code and body consistency
            if self.status_code == HTTP_NO_CONTENT and self.body:  # No Content
                error_msg = "HTTP 204 responses should not have a body"
                raise ValueError(error_msg)

            return self

    class UrlModel(FlextModels.Value):
        """URL model for parsing and validation extending FlextModels.Value."""

        raw_url: str = Field(min_length=1, description="Raw URL")
        scheme: str | None = Field(default=None, description="URL scheme")
        host: str | None = Field(default=None, description="URL host")
        port: int | None = Field(default=None, description="URL port")
        path: str | None = Field(default=None, description="URL path")
        query: str | None = Field(default=None, description="URL query")
        fragment: str | None = Field(default=None, description="URL fragment")

        @computed_field
        def is_secure(self) -> bool:
            """Check if URL uses HTTPS scheme."""
            return self.scheme == "https"

        @computed_field
        def has_query(self) -> bool:
            """Check if URL has query parameters."""
            return bool(self.query)

        @computed_field
        def full_url(self) -> str:
            """Reconstruct full URL from components."""
            url = self.raw_url
            if self.scheme and self.host:
                url = f"{self.scheme}://{self.host}"
                if self.port:
                    url += f":{self.port}"
                if self.path:
                    url += self.path
                if self.query:
                    url += f"?{self.query}"
                if self.fragment:
                    url += f"#{self.fragment}"
            return url

        @model_validator(mode="after")
        def validate_url_components(self) -> Self:
            """Cross-field validation for URL components."""
            if self.port is not None and (self.port < MIN_PORT or self.port > MAX_PORT):
                msg = f"Port must be between {MIN_PORT} and {MAX_PORT}"
                raise ValueError(msg)

            if self.scheme and self.scheme not in {"http", "https", "ftp", "ftps"}:
                msg = "Unsupported URL scheme"
                raise ValueError(msg)

            return self

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate URL business rules."""
            if not self.raw_url:
                return FlextResult[None].fail("URL cannot be empty")
            return FlextResult[None].ok(None)

    class Builder:
        """Response builder for API responses."""

        def create(
            self,
            response_type: str = "success",
            **kwargs: object,
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
                        "request_id": FlextUtilities.Generators.generate_entity_id(),
                    }
                case _:
                    # Direct return for success case
                    return {
                        "status": "success",
                        "data": kwargs.get("data"),
                        "message": kwargs.get("message", ""),
                        "timestamp": FlextUtilities.Generators.generate_iso_timestamp(),
                        "request_id": FlextUtilities.Generators.generate_entity_id(),
                    }

        @staticmethod
        def success(*, data: object = None, message: str = "") -> dict[str, object]:
            """Build success response using flext-core generators."""
            return {
                "status": "success",
                "data": data,
                "message": message,
                "timestamp": FlextUtilities.Generators.generate_iso_timestamp(),
                "request_id": FlextUtilities.Generators.generate_entity_id(),
            }

        @staticmethod
        def error(message: str, code: str = "error") -> dict[str, object]:
            """Build error response using flext-core generators."""
            return {
                "status": "error",
                "error": {"code": code, "message": message},
                "timestamp": FlextUtilities.Generators.generate_iso_timestamp(),
                "request_id": FlextUtilities.Generators.generate_entity_id(),
            }

    class AppConfig(FlextModels.Value):
        """FastAPI application configuration model extending FlextModels.Value."""

        title: str = Field(min_length=1, description="Application title")
        app_version: str = Field(min_length=1, description="Application version")
        description: str = Field(
            default="FlextAPI Application", description="Application description"
        )
        docs_url: str = Field(default="/docs", description="Swagger docs URL")
        redoc_url: str = Field(default="/redoc", description="ReDoc URL")
        openapi_url: str = Field(
            default="/openapi.json", description="OpenAPI schema URL"
        )

        @computed_field
        def has_docs(self) -> bool:
            """Check if documentation is enabled."""
            return bool(self.docs_url or self.redoc_url)

        @computed_field
        def app_identifier(self) -> str:
            """Generate unique app identifier."""
            return f"{self.title.lower().replace(' ', '-')}-{self.app_version}"

        @model_validator(mode="after")
        def validate_app_config(self) -> Self:
            """Cross-field validation for app configuration."""
            # Validate URL paths start with /
            if self.docs_url and not self.docs_url.startswith("/"):
                msg = "docs_url must start with /"
                raise ValueError(msg)
            if self.redoc_url and not self.redoc_url.startswith("/"):
                msg = "redoc_url must start with /"
                raise ValueError(msg)
            if self.openapi_url and not self.openapi_url.startswith("/"):
                msg = "openapi_url must start with /"
                raise ValueError(msg)

            return self

        @field_validator("title", "app_version")
        @classmethod
        def validate_required_fields(cls, v: str) -> str:
            """Validate required string fields."""
            if not v or not v.strip():
                error_message = "Field cannot be empty"
                raise ValueError(error_message)
            return v.strip()

    # HTTP CONFIGURATION CLASSES - Moved from flext-core
    class Http:
        """HTTP-related models for API configuration."""

        class HttpRequestConfig(FlextModels.Command):
            """Configuration for HTTP requests extending FlextModels.Command."""

            config_type: str = Field(
                default="http_request", description="Configuration type"
            )
            url: str = Field(min_length=1, description="Request URL")
            method: str = Field(
                default=FlextApiConstants.HttpMethod.GET, description="HTTP method"
            )
            timeout: int = Field(
                default=int(FlextApiConstants.DEFAULT_TIMEOUT),
                ge=int(FlextApiConstants.MIN_TIMEOUT),
                le=int(FlextApiConstants.MAX_TIMEOUT),
                description="Request timeout",
            )
            retries: int = Field(
                default=FlextApiConstants.DEFAULT_RETRIES,
                ge=FlextApiConstants.MIN_RETRIES,
                le=FlextApiConstants.MAX_RETRIES,
                description="Retry count",
            )
            headers: dict[str, str] = Field(
                default_factory=dict, description="Request headers"
            )

            @computed_field
            @property
            def timeout_ms(self) -> int:
                """Get timeout in milliseconds."""
                return self.timeout * 1000

            @computed_field
            @property
            def has_retries(self) -> bool:
                """Check if retries are configured."""
                return self.retries > 0

            @model_validator(mode="after")
            def validate_http_request_config(self) -> Self:
                """Cross-field validation for HTTP request configuration."""
                if self.retries > MAX_RETRIES_PRODUCTION:
                    msg = f"Retries should not exceed {MAX_RETRIES_PRODUCTION} for production"
                    raise ValueError(msg)

                return self

        class HttpErrorConfig(FlextModels.Entity):
            """Configuration for HTTP error handling extending FlextModels.Entity."""

            config_type: str = Field(
                default="http_error", description="Configuration type"
            )
            status_code: int = Field(
                ge=FlextApiConstants.HTTP_STATUS_MIN,
                le=FlextApiConstants.HTTP_STATUS_MAX,
                description="HTTP status code",
            )
            message: str = Field(min_length=1, description="Error message")
            url: str | None = Field(default=None, description="Request URL")
            method: str | None = Field(default=None, description="HTTP method")
            headers: dict[str, str] | None = Field(
                default=None, description="Response headers"
            )
            context: dict[str, object] = Field(
                default_factory=dict, description="Error context"
            )
            details: dict[str, object] = Field(
                default_factory=dict, description="Error details"
            )

            @computed_field
            @property
            def is_client_error(self) -> bool:
                """Check if this is a client error (4xx)."""
                return HTTP_CLIENT_ERROR_MIN <= self.status_code < HTTP_CLIENT_ERROR_MAX

            @computed_field
            @property
            def is_server_error(self) -> bool:
                """Check if this is a server error (5xx)."""
                return HTTP_SERVER_ERROR_MIN <= self.status_code < HTTP_SERVER_ERROR_MAX

            @computed_field
            @property
            def error_category(self) -> str:
                """Categorize the error type."""
                if self.is_client_error:
                    return "client_error"
                if self.is_server_error:
                    return "server_error"
                return "other_error"

            @model_validator(mode="after")
            def validate_http_error_config(self) -> Self:
                """Cross-field validation for HTTP error configuration."""
                if self.status_code < HTTP_CLIENT_ERROR_MIN:
                    msg = "Error status codes should be 400 or higher"
                    raise ValueError(msg)

                return self

        class ValidationConfig(FlextModels.Value):
            """Configuration for validation extending FlextModels.Value."""

            config_type: str = Field(
                default="validation", description="Configuration type"
            )
            strict_mode: bool = Field(
                default=False, description="Strict validation mode"
            )
            validate_schema: bool = Field(default=True, description="Validate schema")
            custom_validators: list[str] = Field(
                default_factory=list, description="Custom validators"
            )
            field: str | None = Field(default=None, description="Field name")
            value: object = Field(default=None, description="Field value")
            url: str | None = Field(default=None, description="Validation URL")

            @computed_field
            @property
            def has_custom_validators(self) -> bool:
                """Check if custom validators are configured."""
                return bool(self.custom_validators)

            @computed_field
            @property
            def validation_level(self) -> str:
                """Determine validation level."""
                if self.strict_mode:
                    return "strict"
                if self.validate_schema:
                    return "standard"
                return "minimal"

            @model_validator(mode="after")
            def validate_validation_config(self) -> Self:
                """Cross-field validation for validation configuration."""
                if self.custom_validators:
                    for validator in self.custom_validators:
                        if not validator.strip():
                            msg = "Custom validator names cannot be empty"
                            raise ValueError(msg)

                return self


__all__ = [
    "FlextApiModels",
]
