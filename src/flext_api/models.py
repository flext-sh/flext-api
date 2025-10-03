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
    FlextTypes,
    FlextUtilities,
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
    class HttpRequest(FlextModels.HttpRequest):
        """HTTP client request model extending flext-core HttpRequest base.

        Inherits from flext-core:
            - url: Request URL
            - method: HTTP method (GET, POST, etc.)
            - headers: Request headers
            - body: Request body
            - timeout: Request timeout
            - has_body: Computed field - check if request has body
            - is_secure: Computed field - check if request uses HTTPS
            - validate_method: Validates HTTP method against centralized constants
            - validate_request_consistency: Cross-field validation

        Client-specific additions:
            - full_url: Computed full URL with protocol
            - request_size: Computed request body size in bytes
            - tracking_id: Request tracking identifier for logging
        """

        tracking_id: str | None = Field(
            default=None, description="Request tracking ID for logging"
        )

        @computed_field
        @property
        def full_url(self) -> str:
            """Computed full URL with proper formatting - CLIENT SPECIFIC."""
            base_url = self.url.rstrip("/")
            if not base_url.startswith(("http://", "https://")):
                return f"http://{base_url}"
            return base_url

        @computed_field
        @property
        def request_size(self) -> int:
            """Computed request body size in bytes - CLIENT SPECIFIC."""
            if not self.body:
                return 0
            if isinstance(self.body, str):
                return len(self.body.encode("utf-8"))
            if isinstance(self.body, dict):
                return len(json.dumps(self.body).encode("utf-8"))
            return 0

        @field_validator("url")
        @classmethod
        def validate_url_client_specific(cls, v: str) -> str:
            """Validate URL with client-specific logic (relative paths allowed)."""
            # Handle empty URL case first
            if not v or not v.strip():
                msg = "Invalid URL: URL cannot be empty"
                raise ValueError(msg)

            # CLIENT SPECIFIC: Allow relative paths for API clients
            if v.strip().startswith("/"):
                return v.strip()

            validation_result = FlextApiModels.create_validated_http_url(v.strip())
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
        def validate_headers_client_specific(
            cls, v: FlextApiTypes.Headers
        ) -> FlextApiTypes.Headers:
            """Validate and sanitize headers - CLIENT SPECIFIC Python 3.13+ optimization."""
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
            """Serialize request body for API transmission - CLIENT SPECIFIC.

            Returns:
                Serialized body as dict (if JSON-serializable), string, or None.

            Raises:
                ValueError: If dict value is not JSON-serializable.

            """
            if value is None:
                return None
            if isinstance(value, dict):
                # Ensure all dict values are JSON serializable - fail fast if not
                try:
                    json.dumps(value)  # Validate serialization
                    return value
                except (TypeError, ValueError) as e:
                    # FLEXT: No silent fallbacks - raise proper validation error
                    error_msg = (
                        f"Request body dict contains non-JSON-serializable values: {e}"
                    )
                    raise ValueError(error_msg) from e
            return str(value)

    class HttpResponse(FlextModels.HttpResponse):
        """HTTP client response model extending flext-core HttpResponse base.

        Inherits from flext-core:
            - status_code: HTTP status code
            - headers: Response headers
            - body: Response body
            - elapsed_time: Request/response elapsed time
            - is_success: Computed field - check if response is successful (2xx)
            - is_client_error: Computed field - check if response is client error (4xx)
            - is_server_error: Computed field - check if response is server error (5xx)

        Client-specific additions:
            - url: Request URL (for tracking)
            - method: HTTP method (for tracking)
            - request: Original request object (for tracking)
            - domain_events: Domain events list
            - response_time_ms: Computed response time in milliseconds
            - content_length: Computed content length from headers or body
        """

        # CLIENT-SPECIFIC fields for tracking request context
        url: str = Field(description="Request URL")
        method: str = Field(description="HTTP method")
        request: FlextApiModels.HttpRequest = Field(
            description="Original request object"
        )
        domain_events: FlextTypes.List = Field(
            default_factory=list, description="Domain events"
        )

        @computed_field
        @property
        def response_time_ms(self) -> float:
            """Computed response time in milliseconds - CLIENT SPECIFIC."""
            return (self.elapsed_time * 1000) if self.elapsed_time else 0.0

        @computed_field
        @property
        def content_length(self) -> int:
            """Computed content length from headers or body - CLIENT SPECIFIC.

            Returns:
                Content length in bytes. Returns 0 if header is invalid or body is empty.

            """
            # Try to get from headers first
            if "content-length" in self.headers:
                try:
                    return int(self.headers["content-length"])
                except (ValueError, TypeError):
                    # FLEXT: Invalid header - calculate from body instead
                    # This is acceptable as it's a fallback to calculation, not silent suppression
                    pass

            # Calculate from body if header missing or invalid
            if self.body:
                if isinstance(self.body, str):
                    return len(self.body.encode("utf-8"))
                if isinstance(self.body, dict):
                    return len(json.dumps(self.body).encode("utf-8"))

            return 0

        @model_validator(mode="after")
        def validate_response_consistency_client_specific(self) -> Self:
            """Cross-field validation for HTTP response consistency - CLIENT SPECIFIC."""
            # Validate status code and body consistency
            if (
                self.status_code == FlextConstants.Http.HTTP_NO_CONTENT and self.body
            ):  # No Content
                error_msg = "HTTP 204 responses should not have a body"
                raise ValueError(error_msg)

            # Validate elapsed time
            if self.elapsed_time is not None and self.elapsed_time < 0:
                error_msg = "Elapsed time cannot be negative"
                raise ValueError(error_msg)

            return self

        @field_serializer("body")
        def serialize_response_body(
            self, value: str | dict[str, FlextApiTypes.JsonValue] | None
        ) -> str | dict | None:
            """Serialize response body for storage/transmission - CLIENT SPECIFIC."""
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
        base_url: str = Field(default="http://localhost:8000", description="Base URL")
        timeout: float = Field(
            default=30,
            gt=1,
            le=300,
            description="Request timeout",
        )
        max_retries: int = Field(
            default=3,
            ge=0,
            le=FlextApiConstants.MAX_RETRIES,
            description="Maximum retries",
        )
        headers: FlextTypes.StringDict = Field(
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
            # Note: Both auth_token and api_key can be specified - auth_token takes priority
            # This allows flexible authentication configuration with fallback options

            # Validate retry configuration
            if self.max_retries > FlextApiConstants.MAX_RETRIES_PRODUCTION:
                msg = f"Max retries should not exceed {FlextApiConstants.MAX_RETRIES_PRODUCTION} for production use"
                raise ValueError(msg)

            return self

        @field_validator("base_url")
        @classmethod
        def validate_base_url(cls, v: str) -> str:
            """Validate base URL using centralized FlextModels validation."""
            validation_result = FlextApiModels.create_validated_http_url(v.strip())
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
            if len(value) <= FlextApiConstants.MASK_AUTH_THRESHOLD:
                return "***MASKED***"
            return f"{value[:4]}***{value[-4:]}"

        def get_auth_header(self) -> FlextTypes.StringDict:
            """Get authentication header if configured."""
            if self.auth_token:
                return {
                    FlextConstants.Http.AUTHORIZATION_HEADER: f"Bearer {self.auth_token}"
                }
            if self.api_key:
                return {
                    FlextConstants.Http.AUTHORIZATION_HEADER: f"Bearer {self.api_key}"
                }
            return {}

        def get_default_headers(self) -> FlextTypes.StringDict:
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
        filter_conditions: dict[str, FlextApiTypes.JsonValue] = Field(
            default_factory=dict, description="Filter conditions", alias="filters"
        )
        sort_fields: FlextTypes.StringList = Field(
            default_factory=list, description="Sort fields"
        )
        page_number: int = Field(
            default=FlextConstants.Performance.DEFAULT_PAGE_NUMBER,
            ge=FlextConstants.Performance.DEFAULT_PAGE_NUMBER,
            description="Page number",
            alias="page",
        )
        page_size_value: int = Field(
            default=FlextApiConstants.DEFAULT_PAGE_SIZE,
            ge=FlextApiConstants.MIN_PAGE_SIZE,
            le=FlextApiConstants.MAX_PAGE_SIZE,
            description="Page size",
            alias="page_size",
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
            if self.page_size_value > FlextApiConstants.MAX_PAGE_SIZE_PERFORMANCE:
                msg = "Page size too large for performance"
                raise ValueError(msg)

            return self

        def add_filter(
            self, key: str, value: FlextApiTypes.JsonValue
        ) -> FlextResult[None]:
            """Add a filter to the query."""
            if not key or not key.strip():
                return FlextResult[None].fail("Filter key cannot be empty")
            self.filter_conditions[key.strip()] = value
            return FlextResult[None].ok(None)

        def to_query_params(self) -> dict[str, FlextApiTypes.JsonValue]:
            """Convert to query parameters dict with Python 3.13+ computational optimization."""
            # Python 3.13+ optimized dict merge with walrus operator
            # Use by_alias=True to export with field aliases (page, page_size, filters)
            params = self.model_dump(exclude_none=True, by_alias=True)
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
            alias="page",
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
            default=FlextConstants.Http.Method.GET, description="HTTP method"
        )
        headers: FlextTypes.StringDict = Field(
            default_factory=dict, description="Request headers"
        )
        body: str | dict[str, FlextApiTypes.JsonValue] | None = Field(
            default=None, description="Request body"
        )

        @computed_field
        def content_type(self) -> str | None:
            """Get Content-Type header value."""
            return self.headers.get("Content-Type") or self.headers.get("content-type")

        @computed_field
        def is_json_request(self) -> bool:
            """Check if request contains JSON content."""
            content_type_value = self.headers.get("Content-Type") or self.headers.get(
                "content-type"
            )
            return bool(content_type_value and "application/json" in content_type_value)

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
            ge=FlextConstants.Http.HTTP_STATUS_MIN,
            le=FlextConstants.Http.HTTP_STATUS_MAX,
            description="HTTP status code",
        )
        body: str | dict[str, FlextApiTypes.JsonValue] | None = Field(
            default=None, description="Response body"
        )
        headers: FlextTypes.StringDict = Field(
            default_factory=dict, description="Response headers"
        )
        domain_events: FlextTypes.List = Field(
            default_factory=list, description="Domain events"
        )

        @computed_field
        def is_successful(self) -> bool:
            """Check if response indicates success."""
            return (
                FlextConstants.Http.HTTP_SUCCESS_MIN
                <= self.status_code
                < FlextConstants.Http.HTTP_SUCCESS_MAX
            )

        @computed_field
        def content_type(self) -> str | None:
            """Get Content-Type header value."""
            return self.headers.get("Content-Type") or self.headers.get("content-type")

        @computed_field
        def is_json_response(self) -> bool:
            """Check if response contains JSON content."""
            content_type_value = self.headers.get("Content-Type") or self.headers.get(
                "content-type"
            )
            return bool(content_type_value and "application/json" in content_type_value)

        @model_validator(mode="after")
        def validate_api_response(self) -> Self:
            """Cross-field validation for API responses."""
            # Validate status code and body consistency
            if (
                self.status_code == FlextConstants.Http.HTTP_NO_CONTENT and self.body
            ):  # No Content
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
            if self.port is not None and (
                self.port < FlextApiConstants.MIN_PORT
                or self.port > FlextApiConstants.MAX_PORT
            ):
                msg = f"Port must be between {FlextApiConstants.MIN_PORT} and {FlextApiConstants.MAX_PORT}"
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
            **kwargs: FlextApiTypes.JsonValue,
        ) -> dict[str, FlextApiTypes.JsonValue]:
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
        def success(
            *, data: FlextApiTypes.JsonValue = None, message: str = ""
        ) -> dict[str, FlextApiTypes.JsonValue]:
            """Build success response using flext-core generators."""
            return {
                "status": "success",
                "data": data,
                "message": message,
                "timestamp": FlextUtilities.Generators.generate_iso_timestamp(),
                "request_id": FlextUtilities.Generators.generate_entity_id(),
            }

        @staticmethod
        def error(
            message: str, code: str = "error"
        ) -> dict[str, FlextApiTypes.JsonValue]:
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
                default=FlextConstants.Http.Method.GET, description="HTTP method"
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
            headers: FlextTypes.StringDict = Field(
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
                if self.retries > FlextApiConstants.MAX_RETRIES_PRODUCTION:
                    msg = f"Retries should not exceed {FlextApiConstants.MAX_RETRIES_PRODUCTION} for production"
                    raise ValueError(msg)

                return self

        class HttpErrorConfig(FlextModels.Entity):
            """Configuration for HTTP error handling extending FlextModels.Entity."""

            config_type: str = Field(
                default="http_error", description="Configuration type"
            )
            status_code: int = Field(
                ge=FlextConstants.Http.HTTP_STATUS_MIN,
                le=FlextConstants.Http.HTTP_STATUS_MAX,
                description="HTTP status code",
            )
            message: str = Field(min_length=1, description="Error message")
            url: str | None = Field(default=None, description="Request URL")
            method: str | None = Field(default=None, description="HTTP method")
            headers: FlextTypes.StringDict | None = Field(
                default=None, description="Response headers"
            )
            context: dict[str, FlextApiTypes.JsonValue] = Field(
                default_factory=dict, description="Error context"
            )
            details: dict[str, FlextApiTypes.JsonValue] = Field(
                default_factory=dict, description="Error details"
            )

            @computed_field
            @property
            def is_client_error(self) -> bool:
                """Check if this is a client error (4xx)."""
                return (
                    FlextConstants.Http.HTTP_CLIENT_ERROR_MIN
                    <= self.status_code
                    < FlextConstants.Http.HTTP_CLIENT_ERROR_MAX
                )

            @computed_field
            @property
            def is_server_error(self) -> bool:
                """Check if this is a server error (5xx)."""
                return (
                    FlextConstants.Http.HTTP_SERVER_ERROR_MIN
                    <= self.status_code
                    < FlextConstants.Http.HTTP_SERVER_ERROR_MAX
                )

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
                if self.status_code < FlextConstants.Http.HTTP_CLIENT_ERROR_MIN:
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
            custom_validators: FlextTypes.StringList = Field(
                default_factory=list, description="Custom validators"
            )
            field: str | None = Field(default=None, description="Field name")
            value: FlextApiTypes.JsonValue = Field(
                default=None, description="Field value"
            )
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

    class ProtocolConfig(FlextModels.Value):
        """Protocol configuration model."""

        name: str = Field(
            description="Protocol name (http, websocket, graphql, grpc, sse)"
        )
        version: str = Field(default="1.0.0", description="Protocol version")
        enabled: bool = Field(default=True, description="Whether protocol is enabled")
        options: dict[str, FlextApiTypes.JsonValue] = Field(
            default_factory=dict, description="Protocol-specific options"
        )

        @field_validator("name")
        @classmethod
        def validate_protocol_name(cls, v: str) -> str:
            """Validate protocol name."""
            valid_protocols = {"http", "https", "websocket", "graphql", "grpc", "sse"}
            if v.lower() not in valid_protocols:
                msg = f"Protocol must be one of: {', '.join(valid_protocols)}"
                raise ValueError(msg)
            return v.lower()

    class TransportConfig(FlextModels.Value):
        """Transport configuration model."""

        name: str = Field(description="Transport name (httpx, websockets, gql, grpcio)")
        max_connections: int = Field(
            default=100, ge=1, le=1000, description="Maximum connections"
        )
        max_keepalive_connections: int = Field(
            default=20, ge=1, le=100, description="Max keep-alive connections"
        )
        keepalive_expiry: float = Field(
            default=5.0, ge=0.0, description="Keep-alive expiry seconds"
        )
        connect_timeout: float = Field(
            default=5.0, ge=0.1, description="Connect timeout seconds"
        )
        read_timeout: float = Field(
            default=30.0, ge=0.1, description="Read timeout seconds"
        )
        write_timeout: float = Field(
            default=30.0, ge=0.1, description="Write timeout seconds"
        )
        pool_timeout: float = Field(
            default=5.0, ge=0.1, description="Pool timeout seconds"
        )

    class MiddlewareConfig(FlextModels.Value):
        """Middleware configuration model."""

        name: str = Field(description="Middleware name")
        enabled: bool = Field(default=True, description="Whether middleware is enabled")
        priority: int = Field(
            default=100, ge=0, le=1000, description="Middleware execution priority"
        )
        options: dict[str, FlextApiTypes.JsonValue] = Field(
            default_factory=dict, description="Middleware-specific options"
        )

        @field_validator("name")
        @classmethod
        def validate_middleware_name(cls, v: str) -> str:
            """Validate middleware name is not empty."""
            if not v or not v.strip():
                msg = "Middleware name cannot be empty"
                raise ValueError(msg)
            return v.strip()

    class PluginMetadata(FlextModels.Value):
        """Plugin metadata model."""

        name: str = Field(description="Plugin name")
        version: str = Field(default="1.0.0", description="Plugin version")
        description: str = Field(default="", description="Plugin description")
        plugin_type: str = Field(
            description="Plugin type (protocol, schema, transport, auth)"
        )
        enabled: bool = Field(default=True, description="Whether plugin is enabled")
        dependencies: FlextTypes.StringList = Field(
            default_factory=list, description="Plugin dependencies"
        )

        @field_validator("plugin_type")
        @classmethod
        def validate_plugin_type(cls, v: str) -> str:
            """Validate plugin type."""
            valid_types = {"protocol", "schema", "transport", "auth", "middleware"}
            if v.lower() not in valid_types:
                msg = f"Plugin type must be one of: {', '.join(valid_types)}"
                raise ValueError(msg)
            return v.lower()

    class SchemaValidationResult(FlextModels.Entity):
        """Schema validation result model."""

        valid: bool = Field(description="Whether validation passed")
        errors: FlextTypes.StringList = Field(
            default_factory=list, description="Validation errors"
        )
        warnings: FlextTypes.StringList = Field(
            default_factory=list, description="Validation warnings"
        )
        schema_type: str = Field(
            description="Schema type (openapi, jsonschema, api, graphql)"
        )
        validated_at: str = Field(description="Validation timestamp")

        @computed_field
        @property
        def has_errors(self) -> bool:
            """Check if validation has errors."""
            return len(self.errors) > 0

        @computed_field
        @property
        def has_warnings(self) -> bool:
            """Check if validation has warnings."""
            return len(self.warnings) > 0

        @computed_field
        @property
        def error_count(self) -> int:
            """Get error count."""
            return len(self.errors)

        @computed_field
        @property
        def warning_count(self) -> int:
            """Get warning count."""
            return len(self.warnings)

    # Phase 3: WebSocket & SSE Models

    class WebSocketMessage(FlextModels.Value):
        """WebSocket message model."""

        message: str | bytes = Field(description="Message content")
        message_type: str = Field(
            default="text", description="Message type (text or binary)"
        )
        timestamp: str = Field(description="Message timestamp")
        event_id: str | None = Field(default=None, description="Optional event ID")

        @field_validator("message_type")
        @classmethod
        def validate_message_type(cls, v: str) -> str:
            """Validate message type."""
            if v.lower() not in {"text", "binary"}:
                msg = "Message type must be 'text' or 'binary'"
                raise ValueError(msg)
            return v.lower()

    class WebSocketConnection(FlextModels.Entity):
        """WebSocket connection model."""

        url: str = Field(description="WebSocket URL (ws:// or wss://)")
        state: str = Field(default="connecting", description="Connection state")
        headers: FlextTypes.StringDict = Field(
            default_factory=dict, description="Connection headers"
        )
        subprotocols: FlextTypes.StringList = Field(
            default_factory=list, description="WebSocket subprotocols"
        )
        ping_interval: float = Field(
            default=20.0, ge=0.0, description="Ping interval in seconds"
        )
        connected_at: str | None = Field(
            default=None, description="Connection timestamp"
        )
        last_ping_at: str | None = Field(
            default=None, description="Last ping timestamp"
        )
        messages_sent: int = Field(
            default=0, ge=0, description="Number of messages sent"
        )
        messages_received: int = Field(
            default=0, ge=0, description="Number of messages received"
        )

        @field_validator("state")
        @classmethod
        def validate_state(cls, v: str) -> str:
            """Validate connection state."""
            valid_states = {
                "connecting",
                "connected",
                "disconnecting",
                "disconnected",
                "error",
            }
            if v.lower() not in valid_states:
                msg = f"Connection state must be one of: {', '.join(valid_states)}"
                raise ValueError(msg)
            return v.lower()

        @field_validator("url")
        @classmethod
        def validate_url(cls, v: str) -> str:
            """Validate WebSocket URL."""
            if not v.startswith(("ws://", "wss://")):
                msg = "WebSocket URL must start with ws:// or wss://"
                raise ValueError(msg)
            return v

        @computed_field
        @property
        def is_connected(self) -> bool:
            """Check if connection is active."""
            return self.state == "connected"

        @computed_field
        @property
        def is_secure(self) -> bool:
            """Check if connection is secure (wss://)."""
            return self.url.startswith("wss://")

    class SSEEvent(FlextModels.Value):
        """Server-Sent Events event model."""

        event_type: str = Field(default="message", description="Event type")
        data: str = Field(description="Event data")
        event_id: str | None = Field(default=None, description="Event ID for replay")
        retry: int | None = Field(
            default=None, ge=0, description="Retry timeout in milliseconds"
        )
        timestamp: str = Field(description="Event timestamp")

        @computed_field
        @property
        def has_id(self) -> bool:
            """Check if event has ID."""
            return self.event_id is not None and len(self.event_id) > 0

        @computed_field
        @property
        def data_length(self) -> int:
            """Get data length."""
            return len(self.data)

    class SSEConnection(FlextModels.Entity):
        """Server-Sent Events connection model."""

        url: str = Field(description="SSE endpoint URL")
        state: str = Field(default="connecting", description="Connection state")
        headers: FlextTypes.StringDict = Field(
            default_factory=dict, description="Connection headers"
        )
        last_event_id: str = Field(default="", description="Last received event ID")
        retry_timeout: int = Field(
            default=3000, ge=0, description="Retry timeout in milliseconds"
        )
        connected_at: str | None = Field(
            default=None, description="Connection timestamp"
        )
        events_received: int = Field(
            default=0, ge=0, description="Number of events received"
        )
        reconnect_count: int = Field(
            default=0, ge=0, description="Number of reconnections"
        )

        @field_validator("state")
        @classmethod
        def validate_state(cls, v: str) -> str:
            """Validate connection state."""
            valid_states = {
                "connecting",
                "connected",
                "disconnecting",
                "disconnected",
                "error",
            }
            if v.lower() not in valid_states:
                msg = f"Connection state must be one of: {', '.join(valid_states)}"
                raise ValueError(msg)
            return v.lower()

        @computed_field
        @property
        def is_connected(self) -> bool:
            """Check if connection is active."""
            return self.state == "connected"

        @computed_field
        @property
        def has_last_event_id(self) -> bool:
            """Check if has last event ID."""
            return len(self.last_event_id) > 0

        @computed_field
        @property
        def retry_timeout_seconds(self) -> float:
            """Get retry timeout in seconds."""
            return self.retry_timeout / 1000.0

    # Phase 4: GraphQL Models

    class GraphQLQuery(FlextModels.Command):
        """GraphQL query model."""

        query: str = Field(description="GraphQL query string")
        variables: dict[str, FlextApiTypes.JsonValue] = Field(
            default_factory=dict, description="Query variables"
        )
        operation_name: str | None = Field(default=None, description="Operation name")
        fragments: FlextTypes.StringList = Field(
            default_factory=list, description="GraphQL fragments"
        )

        @computed_field
        @property
        def has_variables(self) -> bool:
            """Check if query has variables."""
            return len(self.variables) > 0

        @computed_field
        @property
        def has_fragments(self) -> bool:
            """Check if query has fragments."""
            return len(self.fragments) > 0

        @computed_field
        @property
        def query_length(self) -> int:
            """Get query string length."""
            return len(self.query)

    class GraphQLResponse(FlextModels.Entity):
        """GraphQL response model."""

        data: dict[str, FlextApiTypes.JsonValue] | None = Field(
            default=None, description="Response data"
        )
        errors: list[dict[str, FlextApiTypes.JsonValue]] = Field(
            default_factory=list, description="GraphQL errors"
        )
        extensions: dict[str, FlextApiTypes.JsonValue] = Field(
            default_factory=dict, description="Response extensions"
        )

        @computed_field
        @property
        def has_errors(self) -> bool:
            """Check if response has errors."""
            return len(self.errors) > 0

        @computed_field
        @property
        def has_data(self) -> bool:
            """Check if response has data."""
            return self.data is not None

        @computed_field
        @property
        def is_success(self) -> bool:
            """Check if response is successful."""
            return self.has_data and not self.has_errors

        @computed_field
        @property
        def error_count(self) -> int:
            """Get error count."""
            return len(self.errors)

    class GraphQLSchema(FlextModels.Value):
        """GraphQL schema model."""

        schema_string: str = Field(description="GraphQL schema SDL string")
        types: FlextTypes.StringList = Field(
            default_factory=list, description="Schema types"
        )
        queries: FlextTypes.StringList = Field(
            default_factory=list, description="Available queries"
        )
        mutations: FlextTypes.StringList = Field(
            default_factory=list, description="Available mutations"
        )
        subscriptions: FlextTypes.StringList = Field(
            default_factory=list, description="Available subscriptions"
        )
        directives: FlextTypes.StringList = Field(
            default_factory=list, description="Schema directives"
        )

        @computed_field
        @property
        def has_queries(self) -> bool:
            """Check if schema has queries."""
            return len(self.queries) > 0

        @computed_field
        @property
        def has_mutations(self) -> bool:
            """Check if schema has mutations."""
            return len(self.mutations) > 0

        @computed_field
        @property
        def has_subscriptions(self) -> bool:
            """Check if schema has subscriptions."""
            return len(self.subscriptions) > 0

        @computed_field
        @property
        def operation_count(self) -> int:
            """Get total operation count."""
            return len(self.queries) + len(self.mutations) + len(self.subscriptions)

    class GraphQLSubscription(FlextModels.Entity):
        """GraphQL subscription model."""

        subscription: str = Field(description="GraphQL subscription string")
        variables: dict[str, FlextApiTypes.JsonValue] = Field(
            default_factory=dict, description="Subscription variables"
        )
        operation_name: str | None = Field(default=None, description="Operation name")
        state: str = Field(default="pending", description="Subscription state")
        events_received: int = Field(
            default=0, ge=0, description="Number of events received"
        )
        started_at: str | None = Field(
            default=None, description="Subscription start time"
        )

        @field_validator("state")
        @classmethod
        def validate_state(cls, v: str) -> str:
            """Validate subscription state."""
            valid_states = {"pending", "active", "completed", "error", "cancelled"}
            if v.lower() not in valid_states:
                msg = f"Subscription state must be one of: {', '.join(valid_states)}"
                raise ValueError(msg)
            return v.lower()

        @computed_field
        @property
        def is_active(self) -> bool:
            """Check if subscription is active."""
            return self.state == "active"

        @computed_field
        @property
        def has_variables(self) -> bool:
            """Check if subscription has variables."""
            return len(self.variables) > 0

    # =========================================================================
    # UTILITY METHODS - Direct access following FLEXT standards
    # =========================================================================

    @classmethod
    def create_validated_http_url(cls, url: str) -> FlextResult[str]:
        """Create and validate an HTTP URL.

        Args:
            url: URL string to validate and create

        Returns:
            FlextResult containing validated URL object or error

        """
        try:
            from urllib.parse import urlparse

            if not url or not isinstance(url, str):
                return FlextResult[str].fail("URL must be a non-empty string")

            url = url.strip()
            if not url:
                return FlextResult[str].fail("URL cannot be empty")

            # Parse URL
            parsed = urlparse(url)

            # Validate scheme
            if not parsed.scheme:
                # Default to https for relative URLs
                url = f"https://{url}"
                parsed = urlparse(url)
            elif parsed.scheme not in {"http", "https"}:
                return FlextResult[str].fail(
                    f"URL scheme must be http or https, got: {parsed.scheme}"
                )

            # Validate hostname
            if not parsed.hostname:
                return FlextResult[str].fail("URL must have a valid hostname")

            # Check hostname length
            if len(parsed.hostname) > FlextApiConstants.MAX_HOSTNAME_LENGTH:
                return FlextResult[str].fail("Hostname too long")

            # Validate port if specified
            if parsed.port is not None and not (
                FlextApiConstants.MIN_PORT <= parsed.port <= FlextApiConstants.MAX_PORT
            ):
                return FlextResult[str].fail("Invalid port number")

            return FlextResult[str].ok(parsed)

        except Exception as e:
            return FlextResult[str].fail(f"URL validation failed: {e}")


__all__ = [
    "FlextApiModels",
]
