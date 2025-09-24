"""FLEXT API Models - Data models only (constants/tipos vêm de constants & typings).

Remove duplicações: usar diretamente `FlextApiConstants` e `FlextApiTypes` em vez de
classes internas de constantes/field/endpoints/status. Este módulo agora expõe
somente modelos (Request/Response/Config/Query/Storage/URL) seguindo padrão flext-core.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path

from pydantic import ConfigDict, Field, field_validator

from flext_api.constants import FlextApiConstants
from flext_api.http_method import FlextApiHttpMethod
from flext_api.typings import FlextApiTypings
from flext_core import (
    FlextConstants,
    FlextModels,
    FlextResult,
    FlextUtilities,
)

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

    # Base model configuration using Pydantic 2.11 features
    class _BaseApiModel(FlextModels.ArbitraryTypesModel):
        """Base API model with Pydantic 2.11 features."""

        model_config = ConfigDict(
            validate_assignment=True,
            use_enum_values=True,
            arbitrary_types_allowed=True,
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
            # Serialization features
            json_encoders={
                Path: str,
            },
        )

    # Simple API-specific models extending FlextModels base classes
    class HttpRequest(FlextModels.Command):
        """HTTP request model extending FlextModels.Command."""

        url: str = Field(min_length=1, description="Request URL")
        method: str = Field(default="GET", description="HTTP method")
        headers: FlextApiTypings.Headers = Field(
            default_factory=dict, description="Request headers"
        )
        body: FlextApiTypings.RequestBody = Field(
            default=None, description="Request body"
        )
        timeout: FlextApiTypings.Timeout = Field(
            default=FlextApiConstants.DEFAULT_TIMEOUT,
            ge=FlextApiConstants.MIN_TIMEOUT,
            le=FlextApiConstants.MAX_TIMEOUT,
            description="Request timeout",
        )

        @field_validator("url")
        @classmethod
        def validate_url(cls, v: str) -> str:
            """Validate URL using centralized FlextModels validation."""
            if isinstance(v, str) and v.strip().startswith("/"):
                return v.strip()

            validation_result = FlextModels.create_validated_http_url(
                v.strip() if isinstance(v, str) else "",
            )
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
        def validate_headers(
            cls, v: FlextApiTypings.Headers
        ) -> FlextApiTypings.Headers:
            """Validate and sanitize headers with Python 3.13+ dict comprehension optimization."""
            # Python 3.13+ optimized dict comprehension with walrus operator
            return {
                k_clean: val_clean
                for k, val in v.items()
                if (k_clean := k.strip()) and (val_clean := str(val).strip())
            }

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

        @property
        def is_success(self) -> bool:
            """Check if response indicates success (2xx status codes)."""
            return (
                FlextApiConstants.HTTP_SUCCESS_MIN
                <= self.status_code
                <= FlextApiConstants.HTTP_SUCCESS_MAX
            )

        @property
        def is_client_error(self) -> bool:
            """Check if response indicates client error (4xx status codes)."""
            return (
                FlextApiConstants.HTTP_CLIENT_ERROR_MIN
                <= self.status_code
                <= FlextApiConstants.HTTP_CLIENT_ERROR_MAX
            )

        @property
        def is_server_error(self) -> bool:
            """Check if response indicates server error (5xx status codes)."""
            return (
                FlextApiConstants.HTTP_SERVER_ERROR_MIN
                <= self.status_code
                <= FlextApiConstants.HTTP_SERVER_ERROR_MAX
            )

        @property
        def is_redirect(self) -> bool:
            """Check if response indicates redirect (3xx status codes)."""
            return (
                FlextApiConstants.HTTP_REDIRECTION_MIN
                <= self.status_code
                <= FlextApiConstants.HTTP_REDIRECTION_MAX
            )

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

        @field_validator("base_url")
        @classmethod
        def validate_base_url(cls, v: str) -> str:
            """Validate base URL using centralized FlextModels validation."""
            validation_result = FlextModels.create_validated_http_url(
                v.strip() if isinstance(v, str) else "",
            )
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

        # Core fields with Pydantic 2 alias support for backward compatibility
        filter_conditions: dict[str, object] = Field(
            alias="filters", default_factory=dict, description="Filter conditions"
        )
        sort_fields: list[str] = Field(default_factory=list, description="Sort fields")
        page_number: int = Field(
            alias="page",
            default=FlextConstants.Performance.DEFAULT_PAGE_NUMBER,
            ge=FlextConstants.Performance.DEFAULT_PAGE_NUMBER,
            description="Page number",
        )
        page_size_value: int = Field(
            alias="page_size",
            default=FlextApiConstants.DEFAULT_PAGE_SIZE,
            ge=FlextApiConstants.MIN_PAGE_SIZE,
            le=FlextApiConstants.MAX_PAGE_SIZE,
            description="Page size",
        )

        def add_filter(self, key: str, value: object) -> FlextResult[None]:
            """Add a filter to the query."""
            if not key or not key.strip():
                return FlextResult[None].fail("Filter key cannot be empty")
            self.filter_conditions[key.strip()] = value
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
        """Pagination configuration extending FlextModels.Value."""

        page_size: int = Field(
            default=FlextApiConstants.DEFAULT_PAGE_SIZE,
            gt=FlextApiConstants.MIN_PAGE_SIZE,
            le=FlextApiConstants.MAX_PAGE_SIZE,
            description="Page size",
        )
        current_page: int = Field(
            alias="page",
            default=FlextConstants.Performance.DEFAULT_PAGE_NUMBER,
            ge=FlextConstants.Performance.DEFAULT_PAGE_NUMBER,
            description="Current page",
        )
        max_pages: int | None = Field(default=None, ge=1, description="Maximum pages")
        total: int = Field(default=0, ge=0, description="Total items")

    class StorageConfig(FlextModels.Value):
        """Storage configuration extending FlextModels.Value."""

        backend: str = Field(default="memory", description="Storage backend")
        namespace: str = Field(default="flext_api", description="Storage namespace")
        max_size: int | None = Field(default=None, description="Maximum storage size")
        default_ttl: int | None = Field(default=None, description="Default TTL")

    class ApiRequest(FlextModels.Command):
        """API request model extending FlextModels.Command."""

        url: str = Field(min_length=1, description="Request URL")
        headers: dict[str, str] = Field(
            default_factory=dict, description="Request headers"
        )
        body: str | dict[str, object] | None = Field(
            default=None, description="Request body"
        )

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

    class UrlModel(FlextModels.Value):
        """URL model for parsing and validation extending FlextModels.Value."""

        raw_url: str = Field(min_length=1, description="Raw URL")
        scheme: str | None = Field(default=None, description="URL scheme")
        host: str | None = Field(default=None, description="URL host")
        port: int | None = Field(default=None, description="URL port")
        path: str | None = Field(default=None, description="URL path")
        query: str | None = Field(default=None, description="URL query")
        fragment: str | None = Field(default=None, description="URL fragment")

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
            method: str = Field(default="GET", description="HTTP method")
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

    # Re-export nested classes for backward compatibility
    HttpRequestConfig = Http.HttpRequestConfig
    HttpErrorConfig = Http.HttpErrorConfig
    HttpMethod = FlextApiHttpMethod.HttpMethod


__all__ = [
    "FlextApiModels",
]
