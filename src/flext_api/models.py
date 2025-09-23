"""FLEXT API Models - Data models only (constants/tipos vêm de constants & typings).

Remove duplicações: usar diretamente `FlextApiConstants` e `FlextApiTypes` em vez de
classes internas de constantes/field/endpoints/status. Este módulo agora expõe
somente modelos (Request/Response/Config/Query/Storage/URL) seguindo padrão flext-core.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator

from flext_core import (
    FlextConstants,
    FlextModels,
    FlextResult,
    FlextUtilities,
)

from .constants import FlextApiConstants
from .typings import FlextApiTypings

# Standard model configuration for all API models
STANDARD_MODEL_CONFIG = ConfigDict(
    validate_assignment=True,
    extra="forbid",
    populate_by_name=True,
)


class FlextApiModels:
    """API models using flext-core extensively - Pydantic models only."""

    # Simple API-specific models
    class HttpRequest(BaseModel):
        """HTTP request model with modern Python 3.13 and Pydantic patterns."""

        model_config = STANDARD_MODEL_CONFIG

        method: str = "GET"
        url: str
        headers: FlextApiTypings.Headers = Field(default_factory=dict)
        body: FlextApiTypings.RequestBody = None
        timeout: FlextApiTypings.Timeout = (
            FlextConstants.Performance.DEFAULT_REQUEST_TIMEOUT
        )

        @field_validator("url")
        @classmethod
        def validate_url(cls, v: str) -> str:
            """Validate URL using centralized FlextModels validation.

            Returns:
                str: Validated URL string.

            Raises:
                ValueError: If URL validation fails.

            """
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
            """Validate and sanitize headers with Python 3.13+ dict comprehension optimization.

            Returns:
                FlextApiTypings.Headers: Sanitized headers dictionary.

            """
            # Python 3.13+ optimized dict comprehension with walrus operator
            return {
                k_clean: val_clean
                for k, val in v.items()
                if (k_clean := k.strip()) and (val_clean := str(val).strip())
            }

    class HttpResponse(BaseModel):
        """HTTP response model extending flext-core Entity."""

        model_config = STANDARD_MODEL_CONFIG

        status_code: int = Field(ge=100, le=599)
        body: str | dict[str, object] | None = None
        headers: dict[str, str] = Field(default_factory=dict)
        url: str
        method: str
        elapsed_time: float | None = None

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

        # Status code validation handled by Field constraints (ge=100, le=599)

    class ClientConfig(BaseModel):
        """Streamlined client configuration for reduced bloat."""

        model_config = STANDARD_MODEL_CONFIG

        # Essential configuration only
        base_url: str = FlextApiConstants.DEFAULT_BASE_URL
        timeout: float = Field(default=FlextApiConstants.DEFAULT_TIMEOUT, gt=0)
        max_retries: int = Field(default=FlextApiConstants.DEFAULT_RETRIES, ge=0)
        headers: dict[str, str] = Field(default_factory=dict)

        # Authentication - consolidated
        auth_token: str | None = None
        api_key: str | None = None

        @field_validator("base_url")
        @classmethod
        def validate_base_url(cls, v: str) -> str:
            """Validate base URL using centralized FlextModels validation.

            Returns:
                str: Validated base URL string.

            Raises:
                ValueError: If base URL validation fails.

            """
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
            """Get authentication header if configured.

            Returns:
                dict[str, str]: Authentication header dictionary.

            """
            if self.auth_token:
                return {"Authorization": f"Bearer {self.auth_token}"}
            if self.api_key:
                return {"Authorization": f"Bearer {self.api_key}"}
            return {}

        def get_default_headers(self) -> dict[str, str]:
            """Get all default headers including auth.

            Returns:
                dict[str, str]: Complete headers dictionary with auth.

            """
            headers = {"User-Agent": "FlextAPI/0.9.0", **self.headers}
            headers.update(self.get_auth_header())
            return headers

    class HttpQuery(BaseModel):
        """HTTP query parameters model with filtering and pagination."""

        model_config = STANDARD_MODEL_CONFIG

        # Core fields with Pydantic 2 alias support for backward compatibility
        filter_conditions: dict[str, object] = Field(
            alias="filters",
            default_factory=dict,
        )
        sort_fields: list[str] = Field(default_factory=list)
        page_number: int = Field(alias="page", default=1, ge=1)
        page_size_value: int = Field(
            alias="page_size",
            default=FlextApiConstants.DEFAULT_PAGE_SIZE,
            ge=1,
            le=1000,
        )

        def add_filter(self, key: str, value: object) -> FlextResult[None]:
            """Add a filter to the query.

            Returns:
                FlextResult[None]: Success or failure result.

            """
            if not key or not key.strip():
                return FlextResult[None].fail("Filter key cannot be empty")
            self.filter_conditions[key.strip()] = value
            # Removed backward compatibility reference to reduce bloat
            return FlextResult[None].ok(None)

        def to_query_params(self) -> dict[str, object]:
            """Convert to query parameters dict with Python 3.13+ computational optimization.

            Returns:
                dict[str, object]: Query parameters dictionary.

            """
            # Python 3.13+ optimized dict merge with walrus operator
            params = self.model_dump(by_alias=True, exclude_none=True)
            # Computational optimization: direct merge avoiding update() call
            return {
                **params,
                **(filters if (filters := params.pop("filters", {})) else {}),
            }

    class PaginationConfig(BaseModel):
        """Pagination configuration extending flext-core Value."""

        model_config = STANDARD_MODEL_CONFIG

        page_size: int = Field(
            default=FlextApiConstants.DEFAULT_PAGE_SIZE,
            gt=0,
            le=1000,
        )
        current_page: int = Field(alias="page", default=1, ge=1)
        max_pages: int | None = Field(default=None, ge=1)
        total: int = Field(default=0, ge=0)

        # Compatibility alias removed - use current_page directly

    class StorageConfig(BaseModel):
        """Storage configuration extending flext-core Value."""

        model_config = STANDARD_MODEL_CONFIG

        backend: str = "memory"
        namespace: str = "flext_api"
        max_size: int | None = None
        default_ttl: int | None = None

    class ApiRequest(BaseModel):
        """API request model."""

        model_config = STANDARD_MODEL_CONFIG

        method: str
        url: str
        headers: dict[str, str] = Field(default_factory=dict)
        body: str | dict[str, object] | None = None

    class ApiResponse(BaseModel):
        """API response model."""

        model_config = STANDARD_MODEL_CONFIG

        id: str = Field(default_factory=lambda: "")
        status_code: int
        body: str | dict[str, object] | None = None
        headers: dict[str, str] = Field(default_factory=dict)

    class UrlModel(BaseModel):
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
            """Validate URL business rules.

            Returns:
                FlextResult[None]: Success or failure result.

            """
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
            """Create response using Python 3.13+ pattern matching optimization.

            Returns:
                dict[str, object]: Response dictionary.

            """
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
            """Build success response using flext-core generators.

            Returns:
                dict[str, object]: Success response dictionary.

            """
            return {
                "status": "success",
                "data": data,
                "message": message,
                "timestamp": FlextUtilities.Generators.generate_iso_timestamp(),
                "request_id": FlextUtilities.Generators.generate_entity_id(),
            }

        @staticmethod
        def error(message: str, code: str = "error") -> dict[str, object]:
            """Build error response using flext-core generators.

            Returns:
                dict[str, object]: Error response dictionary.

            """
            return {
                "status": "error",
                "error": {"code": code, "message": message},
                "timestamp": FlextUtilities.Generators.generate_iso_timestamp(),
                "request_id": FlextUtilities.Generators.generate_entity_id(),
            }

    class AppConfig(BaseModel):
        """FastAPI application configuration model."""

        model_config = STANDARD_MODEL_CONFIG

        title: str = Field(..., description="Application title")
        app_version: str = Field(..., description="Application version")
        description: str = Field(
            default="FlextAPI Application",
            description="Application description",
        )
        docs_url: str = Field(default="/docs", description="Swagger docs URL")
        redoc_url: str = Field(default="/redoc", description="ReDoc URL")
        openapi_url: str = Field(
            default="/openapi.json",
            description="OpenAPI schema URL",
        )

        @field_validator("title", "app_version")
        @classmethod
        def validate_required_fields(cls, v: str) -> str:
            """Validate required string fields.

            Returns:
                str: Validated string field.

            Raises:
                ValueError: If field is empty or invalid.

            """
            if not v or not v.strip():
                error_message = "Field cannot be empty"
                raise ValueError(error_message)
            return v.strip()

    # Backward compatibility aliases for ecosystem integration
    # =========================================================================
    # HTTP CONFIGURATION CLASSES - Moved from flext-core
    # =========================================================================

    class Http:
        """HTTP-related models for API configuration.

        # Usage count: 1 (flext-api/client.py)
        """

        class HttpRequestConfig(BaseModel):
            """Configuration for HTTP requests.

            # Usage count: 1 (flext-api/client.py)
            """

            model_config = STANDARD_MODEL_CONFIG

            config_type: str = Field(default="http_request")
            url: str = Field(min_length=1)
            method: str = Field(default="GET")
            timeout: int = Field(default=30)
            retries: int = Field(default=3)
            headers: dict[str, str] = Field(default_factory=dict)

        class HttpErrorConfig(BaseModel):
            """Configuration for HTTP error handling.

            # Usage count: 0 (tests only)
            """

            model_config = STANDARD_MODEL_CONFIG

            config_type: str = Field(default="http_error")
            status_code: int = Field(ge=100, le=599)
            message: str = Field(min_length=1)
            url: str | None = Field(default=None)
            method: str | None = Field(default=None)
            headers: dict[str, str] | None = Field(default=None)
            context: dict[str, object] = Field(default_factory=dict)
            details: dict[str, object] = Field(default_factory=dict)

        class ValidationConfig(BaseModel):
            """Configuration for validation.

            # Usage count: 0 (tests only)
            """

            model_config = STANDARD_MODEL_CONFIG

            config_type: str = Field(default="validation")
            strict_mode: bool = Field(default=False)
            validate_schema: bool = Field(default=True)
            custom_validators: list[str] = Field(default_factory=list)
            field: str | None = Field(default=None)
            value: object = Field(default=None)
            url: str | None = Field(default=None)

    # Re-export nested classes for backward compatibility
    HttpRequestConfig = Http.HttpRequestConfig
    HttpErrorConfig = Http.HttpErrorConfig
    HttpMethod = FlextApiConstants.HttpMethod


__all__ = [
    "FlextApiModels",
]
