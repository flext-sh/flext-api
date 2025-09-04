"""FLEXT API Models - Consolidated HTTP API model system following flext-core patterns.

Single FlextApiModels class containing ALL HTTP API models as hierarchical nested classes,
extending FlextModels from flext-core with HTTP-specific functionality using Python 3.13+
and Pydantic advanced patterns for type-safe HTTP operations and domain modeling.

Architecture Hierarchy:
    FlextApiModels(FlextModels) - Single consolidated class containing:
        - HTTP Core Models: Request, Response, Headers with validation
        - Client Configuration: ClientConfig, RetryConfig, TimeoutConfig
        - Plugin System: PluginConfig, CacheConfig, CircuitBreakerConfig
        - Builder Patterns: QueryBuilder, ResponseBuilder, RequestBuilder
        - Domain Entities: ApiEntity, HttpSession, ClientSession
        - Value Objects: Url, Port, Timeout, StatusCode with RootModel
        - Factory Methods: Comprehensive creation with FlextResult patterns
        - Validation System: HTTP-specific business rules and constraints

Python 3.13+ Features:
    - Discriminated unions with type narrowing
    - Generic type parameters with constraints
    - Advanced pattern matching with structural typing
    - Enhanced type annotations with Self and TypeVars
    - Pydantic RootModel for primitive validation
    - ConfigDict with strict validation settings

Integration with flext-core:
    - Extends FlextModels for consistent configuration
    - Uses FlextResult[T] for all factory methods and validation
    - Integrates with FlextLogger from flext-core
    - Follows entity/value object patterns from FlextModels
    - Uses FlextConstants for HTTP-specific constants

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import sys
from enum import StrEnum
from typing import Annotated, Literal, Self
from urllib.parse import urlparse

from flext_core import (
    FlextDomainService,
    FlextHandlers,
    FlextMixins,
    FlextModels,
    FlextResult,
    FlextUtilities,
)
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    computed_field,
    field_validator,
)

from flext_api.constants import FlextApiConstants


# Python 3.13 Configuration Models with Pydantic V2 Advanced Features
class HttpResponseConfig(BaseModel):
    """HTTP Response configuration using Pydantic V2 with advanced features."""

    # Pydantic V2 Advanced Configuration
    model_config = ConfigDict(
        # Performance optimizations
        validate_assignment=True,
        validate_default=True,
        use_enum_values=True,
        populate_by_name=True,
        # JSON Schema generation
        json_schema_extra={
            "examples": [
                {
                    "config_type": "http_response",
                    "status_code": 200,
                    "url": "https://api.example.com/data",
                    "method": "GET",
                    "headers": {"content-type": "application/json"},
                    "body": {"message": "success"},
                    "elapsed_time": 0.125,
                }
            ]
        },
        # Serialization options
        ser_json_bytes="base64",
        hide_input_in_errors=True,
    )

    config_type: Literal["http_response"] = "http_response"
    status_code: int = Field(ge=100, le=599, description="HTTP status code")
    url: str = Field(min_length=1, description="Request URL")
    method: str = Field(min_length=1, description="HTTP method")
    headers: dict[str, str] = Field(
        default_factory=dict, description="Response headers"
    )
    body: str | bytes | dict[str, object] | None = Field(
        None, description="Response body"
    )
    elapsed_time: float = Field(ge=0.0, description="Request duration in seconds")


class ClientConfig(BaseModel):
    """Client configuration using Pydantic V2."""

    config_type: Literal["client"] = "client"
    base_url: str
    timeout: float = 30.0
    max_retries: int = 3
    headers: dict[str, str] = Field(default_factory=dict)
    enable_ssl_verify: bool = True
    follow_redirects: bool = True
    proxy: dict[str, str] | None = None


class CacheConfig(BaseModel):
    """Cache configuration using Pydantic V2."""

    config_type: Literal["cache"] = "cache"
    ttl: int = 300
    max_size: int = 1000
    enabled: bool = True
    strategy: str = "lru"
    persistent: bool = False


class RetryConfig(BaseModel):
    """Retry configuration using Pydantic V2."""

    config_type: Literal["retry"] = "retry"
    max_retries: int = 3
    backoff_factor: float = 2.0
    retry_on_status: list[int] = Field(default_factory=lambda: [500, 502, 503, 504])
    max_delay: float = 60.0
    jitter: bool = True
    exponential: bool = True


# Python 3.13 Discriminated Union for API Configuration Types with Pydantic V2
ApiConfigType = Annotated[
    HttpResponseConfig | ClientConfig | CacheConfig | RetryConfig,
    Field(discriminator="config_type"),
]


class FlextApiModels(FlextModels):
    """Consolidated HTTP API model system extending FlextModels with HTTP-specific functionality.

    Single class containing ALL HTTP API models as hierarchical nested classes following
    the unified flext-core pattern. Provides comprehensive HTTP domain modeling with
    type-safe validation, FlextResult patterns, and Python 3.13+ features.

    Architecture Overview:
        Following flext-core FlextModels pattern with hierarchical organization:

        - **HTTP Core Layer**: Request, Response, Headers, Session models
        - **Configuration Layer**: ClientConfig, RetryConfig, TimeoutConfig, PluginConfig
        - **Domain Layer**: ApiEntity, HttpSession extending FlextModels
        - **Value Objects Layer**: Url, StatusCode, Method extending FlextModels
        - **Primitive Validation**: RootModel classes for HTTP-specific primitives
        - **Builder Layer**: QueryBuilder, ResponseBuilder, RequestBuilder
        - **Factory Methods**: Creation methods returning FlextResult[T]
        - **Business Rules**: HTTP-specific validation and constraints

    Key Features:
        - **Unified Model System**: All models in single hierarchical class
        - **FlextResult Integration**: All operations return FlextResult[T]
        - **Python 3.13+ Syntax**: Advanced type annotations and discriminated unions
        - **Pydantic Advanced**: RootModel, ConfigDict, computed fields
        - **HTTP Domain Logic**: Business rules for HTTP operations
        - **Type Safety**: Comprehensive generic typing and validation
        - **flext-core Compliance**: Strict adherence to foundation patterns

    Design Principles:
        - Single Point of Truth: All HTTP models in one location
        - No Legacy Access: Only modern flext-core patterns allowed
        - Railway Programming: FlextResult for all fallible operations
        - Domain-Driven Design: Clear entity/value object separation
        - Type Safety First: Comprehensive validation and constraints
        - Factory Pattern: Safe creation with validation and error handling

    Usage Examples:
        HTTP request creation with validation:
        >>> request_result = FlextApiModels.create_http_request(
        ...     method="POST",
        ...     url="https://api.example.com/users",
        ...     body={"name": "John", "email": "john@example.com"},
        ...     headers={"Content-Type": "application/json"},
        ... )
        >>> if request_result.success:
        ...     request = request_result.value
        ...     logger.info(f"Request created: {request.method} {request.url}")

        Client configuration with validation:
        >>> config_result = FlextApiModels.create_client_config(
        ...     base_url="https://api.example.com",
        ...     timeout=30.0,
        ...     max_retries=3,
        ...     headers={"User-Agent": "FlextAPI/1.0"},
        ... )

        Response building with business rules:
        >>> response_result = FlextApiModels.create_http_response(
        ...     status_code=200,
        ...     body={"users": [{"id": 1, "name": "John"}]},
        ...     url="https://api.example.com/users",
        ...     method="GET",
        ... )

    Integration:
        Seamlessly integrates with flext-core foundation:
        - Uses FlextModels and FlextModels as base classes
        - Implements FlextResult[T] for all fallible operations
        - Follows FlextConstants for HTTP-specific constants
        - Uses FlextLogger() from flext-core for consistent logging
        - Extends FlextTypes for HTTP-specific type definitions

    Note:
        This is the ONLY model class in this module following strict
        single-class-per-module pattern. No legacy interfaces or
        backwards compatibility - only modern flext-core patterns.

    """

    # =============================================================================
    # HTTP CORE ENUMS
    # =============================================================================

    class HttpMethod(StrEnum):
        """HTTP method enumeration."""

        GET = "GET"
        POST = "POST"
        PUT = "PUT"
        DELETE = "DELETE"
        PATCH = "PATCH"
        HEAD = "HEAD"
        OPTIONS = "OPTIONS"
        TRACE = "TRACE"

    class HttpStatus(StrEnum):
        """HTTP status enumeration."""

        SUCCESS = "success"
        ERROR = "error"
        PENDING = "pending"
        TIMEOUT = "timeout"

    # =============================================================================
    # PRIMITIVE VALIDATION CLASSES (RootModel)
    # =============================================================================

    class HttpUrl(RootModel[str]):
        """HTTP URL with comprehensive HTTP validation."""

        root: str = Field(description="Valid HTTP/HTTPS URL")

        @field_validator("root")
        @classmethod
        def validate_url(cls, v: str) -> str:
            def _raise_scheme_netloc_error() -> None:
                msg = "URL must include scheme and netloc"
                raise ValueError(msg)

            def _raise_scheme_validation_error() -> None:
                msg = "URL scheme must be http or https"
                raise ValueError(msg)

            # Use REAL FlextUtilities for string validation
            if not FlextUtilities.is_non_empty_string(v):
                msg = "URL cannot be empty"
                raise ValueError(msg)

            # Clean using REAL FlextUtilities text processing
            cleaned_url = FlextUtilities.clean_text(v)

            # Parse and validate HTTP-specific requirements
            try:
                parsed = urlparse(cleaned_url)
                if not parsed.scheme or not parsed.netloc:
                    _raise_scheme_netloc_error()
                if parsed.scheme not in {"http", "https"}:
                    _raise_scheme_validation_error()
                return cleaned_url
            except Exception as e:
                msg = f"Invalid URL format: {e}"
                raise ValueError(msg) from e

    class StatusCode(RootModel[int]):
        """HTTP status code with validation."""

        root: int = Field(ge=100, le=599, description="Valid HTTP status code")

    class Timeout(RootModel[float]):
        """Request timeout with validation."""

        root: float = Field(
            gt=0,
            le=FlextApiConstants.HttpValidation.MAX_TIMEOUT,
            description="Request timeout in seconds",
        )

    class HttpPort(RootModel[int]):
        """HTTP network port with validation."""

        root: int = Field(ge=1, le=65535, description="Valid network port")

    # =============================================================================
    # HTTP DOMAIN ENTITIES (extending FlextModels)
    # =============================================================================

    class HttpSession(FlextModels.Entity):
        """HTTP session entity with state management."""

        session_id: str = Field(..., description="Unique session identifier")
        base_url: str = Field(..., description="Base URL for session")
        headers: dict[str, str] = Field(default_factory=dict)
        cookies: dict[str, str] = Field(default_factory=dict)
        is_active: bool = Field(default=True)

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate HTTP session business rules using Python 3.13 + Railway Pattern."""
            # Use Railway Pattern to chain validations
            return (
                self._validate_base_url()
                .bind(lambda _: self._validate_session_id())
                .bind(lambda _: self._validate_url_format())
            )

        def _validate_base_url(self) -> FlextResult[None]:
            """Validate base URL using FlextUtilities."""
            return (
                FlextResult[None].ok(None)
                if FlextUtilities.is_non_empty_string(self.base_url)
                else FlextResult[None].fail("Session must have valid base URL")
            )

        def _validate_session_id(self) -> FlextResult[None]:
            """Validate session ID using FlextUtilities."""
            return (
                FlextResult[None].ok(None)
                if FlextUtilities.is_non_empty_string(self.session_id)
                else FlextResult[None].fail("Session must have valid ID")
            )

        def _validate_url_format(self) -> FlextResult[None]:
            """Validate URL format using Python 3.13 match/case."""
            try:
                parsed = urlparse(self.base_url)

                # Use Python 3.13 pattern matching for validation
                match (parsed.scheme, parsed.netloc):
                    case (scheme, netloc) if not scheme or not netloc:
                        return FlextResult[None].fail("Invalid base URL format")
                    case (scheme, _) if scheme not in {"http", "https"}:
                        return FlextResult[None].fail("Base URL must use HTTP/HTTPS")
                    case _:
                        return FlextResult[None].ok(None)

            except Exception as e:
                return FlextResult[None].fail(f"URL parsing failed: {e}")

    class ApiEndpoint(FlextModels.Entity):
        """API endpoint entity with configuration."""

        endpoint_path: str = Field(..., description="Endpoint path")
        method: str = Field(..., description="HTTP method")
        base_url: str = Field(..., description="Base URL")
        timeout: float = Field(default=30.0)
        retries: int = Field(default=3)

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate API endpoint business rules."""
            if not self.endpoint_path.startswith("/"):
                return FlextResult[None].fail("Endpoint path must start with /")
            if self.method not in {"GET", "POST", "PUT", "DELETE", "PATCH"}:
                return FlextResult[None].fail("Invalid HTTP method")
            return FlextResult[None].ok(None)

    # =============================================================================
    # HTTP VALUE OBJECTS (extending FlextModels)
    # =============================================================================

    class HttpRequest(FlextModels.Value):
        """Immutable HTTP request value object with Pydantic V2 advanced features."""

        method: str = Field(..., description="HTTP method")
        url: str = Field(..., description="Request URL")
        headers: dict[str, str] = Field(default_factory=dict)
        body: str | bytes | dict[str, object] | None = Field(default=None)
        timeout: float = Field(default=30.0)

        @computed_field
        def is_get_request(self) -> bool:
            """Computed field: Check if this is a GET request."""
            return self.method.upper() == "GET"

        @computed_field
        def has_body(self) -> bool:
            """Computed field: Check if request has a body."""
            return self.body is not None

        @computed_field
        def content_type(self) -> str | None:
            """Computed field: Extract content-type from headers."""
            return self.headers.get("content-type") or self.headers.get("Content-Type")

        @field_validator("url")
        @classmethod
        def validate_url(cls, v: str) -> str:
            """Advanced Pydantic V2 validator using Python 3.13 + FlextUtilities."""
            # Use REAL FlextUtilities for string validation
            if not FlextUtilities.is_non_empty_string(v):
                msg = "URL cannot be empty"
                raise ValueError(msg)

            # Parse and validate using Python 3.13 match/case
            try:
                parsed = urlparse(v)

                # String literal validation messages - EM101/102 compliance
                no_scheme_msg = "URL must include scheme (http/https)"
                no_hostname_msg = "URL must include hostname"

                # Abstract raise to inner functions as per TRY301
                def raise_url_error(message: str) -> None:
                    raise ValueError(message)  # noqa: TRY301

                # Python 3.13 pattern matching for elegant validation
                match (parsed.scheme, parsed.netloc):
                    case ("", _):
                        raise_url_error(no_scheme_msg)
                    case (scheme, "") if scheme:
                        raise_url_error(no_hostname_msg)
                    case (scheme, _) if scheme not in {"http", "https"}:
                        invalid_scheme_msg = (
                            f"Unsupported scheme '{scheme}', use http/https"
                        )
                        raise_url_error(invalid_scheme_msg)
                    case _:
                        return v

            except ValueError:
                raise  # Re-raise our validation errors
            except Exception as e:
                msg = f"URL validation failed: {e}"
                raise ValueError(msg) from e

            # This should never be reached due to match/case, but satisfy MyPy
            return v

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate HTTP request business rules."""
            if self.method not in {
                "GET",
                "POST",
                "PUT",
                "DELETE",
                "PATCH",
                "HEAD",
                "OPTIONS",
            }:
                return FlextResult[None].fail("Invalid HTTP method")
            if self.timeout <= 0:
                return FlextResult[None].fail("Timeout must be positive")
            return FlextResult[None].ok(None)

    class HttpResponse(FlextModels.Value):
        """Immutable HTTP response value object."""

        status_code: int = Field(..., description="HTTP status code")
        headers: dict[str, str] = Field(default_factory=dict)
        body: str | bytes | dict[str, object] | None = Field(default=None)
        url: str = Field(..., description="Request URL")
        method: str = Field(..., description="HTTP method")
        elapsed_time: float = Field(default=0.0)

        @field_validator("status_code")
        @classmethod
        def validate_status_code(cls, v: int) -> int:
            if not (
                FlextApiConstants.HttpStatus.CONTINUE
                <= v
                <= FlextApiConstants.HttpStatus.NETWORK_CONNECT_TIMEOUT_ERROR
            ):
                msg = "Invalid HTTP status code"
                raise ValueError(msg)
            return v

        @computed_field
        def is_success(self) -> bool:
            """Check if response indicates success."""
            return (
                FlextApiConstants.HttpStatus.OK
                <= self.status_code
                < FlextApiConstants.HttpStatus.MULTIPLE_CHOICES
            )

        @computed_field
        def is_client_error(self) -> bool:
            """Check if response indicates client error."""
            return (
                FlextApiConstants.HttpStatus.BAD_REQUEST
                <= self.status_code
                < FlextApiConstants.HttpStatus.INTERNAL_SERVER_ERROR
            )

        @computed_field
        def is_server_error(self) -> bool:
            """Check if response indicates server error."""
            return (
                FlextApiConstants.HttpStatus.INTERNAL_SERVER_ERROR
                <= self.status_code
                < FlextApiConstants.HttpStatus.MAX_STATUS_CODE
            )

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate HTTP response business rules."""
            if self.elapsed_time < 0:
                return FlextResult[None].fail("Elapsed time cannot be negative")
            return FlextResult[None].ok(None)

    # =============================================================================
    # CONFIGURATION MODELS (extending Config)
    # =============================================================================

    class ClientConfig(FlextModels.Value):
        """HTTP client configuration."""

        base_url: str = Field(..., description="Base URL for requests")
        timeout: float = Field(default=30.0, description="Request timeout")
        max_retries: int = Field(default=3, description="Maximum retries")
        headers: dict[str, str] = Field(default_factory=dict)
        verify_ssl: bool = Field(default=True)
        allow_redirects: bool = Field(default=True)

        @field_validator("base_url")
        @classmethod
        def validate_base_url(cls, v: str) -> str:
            def _raise_invalid_base_url_error() -> None:
                msg = "Invalid base URL format"
                raise ValueError(msg)

            # Use REAL FlextUtilities for string validation and cleaning
            if not FlextUtilities.is_non_empty_string(v):
                msg = "Base URL cannot be empty"
                raise ValueError(msg)

            # Clean using REAL FlextUtilities text processing
            cleaned_url = FlextUtilities.clean_text(v)

            # Parse and validate URL format
            try:
                parsed = urlparse(cleaned_url)
                if not parsed.scheme or not parsed.netloc:
                    _raise_invalid_base_url_error()
                return cleaned_url.rstrip("/")
            except Exception as e:
                msg = f"Base URL validation failed: {e}"
                raise ValueError(msg) from e

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate client configuration business rules using REAL FlextUtilities."""
            # Use REAL FlextUtilities for safe conversions and range validation
            safe_timeout = (
                float(self.timeout) if isinstance(self.timeout, (int, float)) else -1.0
            )
            if (
                safe_timeout <= 0
                or safe_timeout > FlextApiConstants.ApiValidation.MAX_TIMEOUT
            ):
                return FlextResult[None].fail(
                    f"Timeout must be between {FlextApiConstants.ApiValidation.MIN_TIMEOUT} and {FlextApiConstants.ApiValidation.MAX_TIMEOUT} seconds, got: {safe_timeout}"
                )

            safe_retries = FlextUtilities.safe_int(self.max_retries, -1)
            if (
                safe_retries < 0
                or safe_retries > FlextApiConstants.ApiValidation.MAX_RETRIES
            ):
                return FlextResult[None].fail(
                    f"Max retries must be between 0 and {FlextApiConstants.ApiValidation.MAX_RETRIES}, got: {safe_retries}"
                )

            return FlextResult[None].ok(None)

    class PluginConfig(FlextModels.Value):
        """Base plugin configuration."""

        name: str = Field(..., description="Plugin name")
        enabled: bool = Field(default=True)
        priority: int = Field(default=0)

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate plugin configuration business rules using FlextUtilities."""
            # Use REAL FlextUtilities for string validation
            if not FlextUtilities.is_non_empty_string(self.name):
                return FlextResult[None].fail("Plugin name cannot be empty")

            # Clean and validate name length
            clean_name = FlextUtilities.clean_text(self.name)
            if (
                len(clean_name) < FlextApiConstants.ApiValidation.MIN_NAME_LENGTH
                or len(clean_name) > FlextApiConstants.ApiValidation.MAX_NAME_LENGTH
            ):
                return FlextResult[None].fail(
                    f"Plugin name length must be between {FlextApiConstants.ApiValidation.MIN_NAME_LENGTH} and {FlextApiConstants.ApiValidation.MAX_NAME_LENGTH} characters, got: {len(clean_name)}"
                )

            return FlextResult[None].ok(None)

    class CacheConfig(PluginConfig):
        """Cache plugin configuration."""

        name: str = Field(default="cache")
        ttl: int = Field(default=300, gt=0)
        max_size: int = Field(default=1000, gt=0)

    class RetryConfig(PluginConfig):
        """Retry plugin configuration."""

        name: str = Field(default="retry")
        max_retries: int = Field(default=3, ge=0)
        backoff_factor: float = Field(default=2.0, gt=0)
        retry_on_status: list[int] = Field(default_factory=lambda: [500, 502, 503, 504])

    class CircuitBreakerConfig(PluginConfig):
        """Circuit breaker plugin configuration."""

        name: str = Field(default="circuit_breaker")
        failure_threshold: int = Field(default=5, gt=0)
        timeout: float = Field(default=60.0, gt=0)
        recovery_timeout: float = Field(default=30.0, gt=0)

    # =============================================================================
    # FACTORY METHODS (following flext-core FlextModels pattern EXACTLY)
    # =============================================================================

    # Universal Builder Pattern - eliminates ALL parameter overload
    class Builder:
        """Universal builder eliminating ALL methods with many parameters."""

        @classmethod
        def create(cls, model_name: str, **kwargs: object) -> FlextResult[object]:
            """Universal creation method using reflection and Pydantic validation."""
            try:
                # Get model class dynamically from current module
                current_module = sys.modules[cls.__module__]
                parent_class_name = cls.__qualname__.split(".")[0]  # FlextApiModels
                parent_class = getattr(current_module, parent_class_name)
                model_class = getattr(parent_class, model_name)

                # Use Pydantic's built-in validation
                instance = model_class(**kwargs)

                # Business validation if available
                if hasattr(instance, "validate_business_rules"):
                    validation_result = instance.validate_business_rules()
                    if validation_result.is_failure:
                        return FlextResult.fail(
                            f"Validation failed: {validation_result.error}"
                        )

                return FlextResult.ok(instance)
            except Exception as e:
                return FlextResult.fail(f"Model creation failed: {e}")

    # Convenience methods using the universal builder
    @classmethod
    def create_http_request(cls, **kwargs: object) -> FlextResult[object]:
        """Create HTTP request using universal builder."""
        return cls.Builder.create("HttpRequest", **kwargs)

    @classmethod
    def create_http_response(
        cls, config: HttpResponseConfig
    ) -> FlextResult[HttpResponse]:
        """Create HTTP response using Builder Pattern with Pydantic V2."""
        try:
            # Pydantic V2 handles validation automatically
            response = cls.HttpResponse(**config.model_dump())
            validation_result = response.validate_business_rules()
            if validation_result.is_failure:
                return FlextResult["FlextApiModels.HttpResponse"].fail(
                    f"HTTP response validation failed: {validation_result.error}"
                )
            return FlextResult["FlextApiModels.HttpResponse"].ok(response)
        except Exception as e:
            return FlextResult["FlextApiModels.HttpResponse"].fail(
                f"HTTP response creation failed: {e}"
            )

    @classmethod
    def create_client_config(
        cls, config: ClientConfig
    ) -> FlextResult[FlextApiModels.ClientConfig]:
        """Create client configuration using Pydantic V2 validation."""
        try:
            # Pydantic V2 handles all validation automatically
            validated_config = cls.ClientConfig(**config.model_dump())
            return FlextResult[FlextApiModels.ClientConfig].ok(validated_config)
        except Exception as e:
            return FlextResult[FlextApiModels.ClientConfig].fail(
                f"Client config creation failed: {e}"
            )

    @classmethod
    def create_http_session(
        cls,
        session_id: str,
        base_url: str,
        headers: dict[str, str] | None = None,
        cookies: dict[str, str] | None = None,
    ) -> FlextResult[HttpSession]:
        """Create HTTP session entity with validation."""
        try:
            session = cls.HttpSession(
                id=session_id,
                session_id=session_id,
                base_url=base_url,
                headers=headers or {},
                cookies=cookies or {},
            )
            validation_result = session.validate_business_rules()
            if validation_result.is_failure:
                return FlextResult["FlextApiModels.HttpSession"].fail(
                    f"HTTP session validation failed: {validation_result.error}"
                )
            return FlextResult["FlextApiModels.HttpSession"].ok(session)
        except Exception as e:
            return FlextResult["FlextApiModels.HttpSession"].fail(
                f"HTTP session creation failed: {e}"
            )

    @classmethod
    def create_cache_config(
        cls, config: CacheConfig
    ) -> FlextResult[FlextApiModels.CacheConfig]:
        """Create cache configuration using Pydantic V2 validation."""
        try:
            # Pydantic V2 handles all validation automatically
            validated_config = cls.CacheConfig(**config.model_dump())
            return FlextResult[FlextApiModels.CacheConfig].ok(validated_config)
        except Exception as e:
            return FlextResult[FlextApiModels.CacheConfig].fail(
                f"Cache config creation failed: {e}"
            )

    @classmethod
    def create_retry_config(
        cls, config: RetryConfig
    ) -> FlextResult[FlextApiModels.RetryConfig]:
        """Create retry configuration using Pydantic V2 validation."""
        try:
            # Pydantic V2 handles all validation automatically
            validated_config = cls.RetryConfig(**config.model_dump())
            return FlextResult[FlextApiModels.RetryConfig].ok(validated_config)
        except Exception as e:
            return FlextResult[FlextApiModels.RetryConfig].fail(
                f"Retry config creation failed: {e}"
            )

    # Validation methods removed - use Pydantic field_validator directly in model classes

    # =============================================================================
    # HTTP-SPECIFIC QUERY SYSTEM - Using flext-core CQRS patterns
    # =============================================================================

    class HttpQuery(FlextModels.Config):
        """HTTP query using flext-core CQRS QueryHandler pattern."""

        query_params: dict[str, str] = Field(default_factory=dict)
        sort_fields: list[str] = Field(default_factory=list)
        filter_conditions: dict[str, str] = Field(default_factory=dict)
        page_number: int = Field(default=1, ge=1)
        page_size: int = Field(default=20, ge=1, le=100)

        def equals(self, field: str, value: str) -> Self:
            """Add equals filter condition."""
            self.filter_conditions[field] = value
            return self

        def sort_desc(self, field: str) -> Self:
            """Add descending sort."""
            self.sort_fields.append(f"-{field}")
            return self

        def sort_asc(self, field: str) -> Self:
            """Add ascending sort."""
            self.sort_fields.append(field)
            return self

        def page(self, page_number: int) -> Self:
            """Set page number."""
            self.page_number = page_number
            return self

        def set_page_size(self, size: int) -> Self:
            """Set page size."""
            self.page_size = size
            return self

        def build(self) -> dict[str, str]:
            """Build final query parameters."""
            params = self.query_params.copy()
            params.update(self.filter_conditions)

            if self.sort_fields:
                params["sort"] = ",".join(self.sort_fields)

            params["page"] = str(self.page_number)
            params["page_size"] = str(self.page_size)

            return params

    # =============================================================================
    # DIRECT FLEXT-CORE USAGE - No duplication, use what exists
    # =============================================================================

    # Use flext-core classes directly - no local copies
    QueryBus = FlextHandlers.CQRS.QueryBus
    QueryHandler = FlextHandlers.CQRS.QueryHandler

    # Storage uses flext-core cache system
    CacheBackend = FlextMixins.Cacheable

    # State management from flext-core
    StatefulService = FlextMixins.Stateful

    class ApiBaseService(FlextDomainService[dict[str, object]]):
        """Concrete base service for HTTP API operations."""

        service_name: str = Field(default="FlextApiBaseService")
        service_version: str = Field(default="0.9.0")

        def execute(self) -> FlextResult[dict[str, object]]:
            """Execute base service operation."""
            return FlextResult[dict[str, object]].ok({
                "service": self.service_name,
                "version": self.service_version,
                "status": "active",
            })

    # =========================================================================
    # CONFIGURATION MODELS - Configuration management patterns
    # =========================================================================

    class StorageConfig(FlextModels.Config):
        """Storage configuration for FlextApiStorage."""

        namespace: str = Field(default="default", description="Storage namespace")
        backend: type[FlextMixins.Cacheable] = Field(
            default=FlextMixins.Cacheable, description="Storage backend class"
        )

    class PaginationConfig(FlextModels.Config):
        """Pagination configuration."""

        page: int = Field(default=1, description="Page number")
        page_size: int = Field(default=20, description="Page size")
        max_page_size: int = Field(default=100, description="Maximum page size")

    # =========================================================================
    # REQUEST MODELS - HTTP request handling patterns
    # =========================================================================

    class ApiRequest(BaseModel):
        """API request model with proper Pydantic BaseModel inheritance."""

        id: str = Field(description="Request ID")
        method: str = Field(default="GET", description="HTTP method")
        url: str = Field(description="Request URL")
        headers: dict[str, str] | None = Field(
            default=None, description="Request headers"
        )

        @field_validator("method")
        @classmethod
        def validate_method(cls, v: str) -> str:
            """Validate HTTP method."""
            valid_methods = {
                "GET",
                "POST",
                "PUT",
                "DELETE",
                "PATCH",
                "HEAD",
                "OPTIONS",
                "TRACE",
            }
            if v.upper() not in valid_methods:
                msg = f"Invalid HTTP method: {v}"
                raise ValueError(msg)
            return v.upper()

        @field_validator("url")
        @classmethod
        def validate_url(cls, v: str) -> str:
            """Validate URL format."""
            if not FlextUtilities.is_non_empty_string(v):
                msg = "URL cannot be empty"
                raise ValueError(msg)
            return FlextUtilities.clean_text(v)


__all__ = [
    "FlextApiModels",
]
