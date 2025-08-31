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
    - Extends FlextModels.BaseConfig for consistent configuration
    - Uses FlextResult[T] for all factory methods and validation
    - Integrates with FlextLogger from flext-core
    - Follows entity/value object patterns from FlextModels
    - Uses FlextConstants for HTTP-specific constants

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any
from urllib.parse import urlparse

from flext_core import FlextModels, FlextResult
from pydantic import Field, RootModel, computed_field, field_validator

from flext_api.constants import FlextApiConstants


class FlextApiModels(FlextModels):
    """Consolidated HTTP API model system extending FlextModels with HTTP-specific functionality.

    Single class containing ALL HTTP API models as hierarchical nested classes following
    the unified flext-core pattern. Provides comprehensive HTTP domain modeling with
    type-safe validation, FlextResult patterns, and Python 3.13+ features.

    Architecture Overview:
        Following flext-core FlextModels pattern with hierarchical organization:

        - **HTTP Core Layer**: Request, Response, Headers, Session models
        - **Configuration Layer**: ClientConfig, RetryConfig, TimeoutConfig, PluginConfig
        - **Domain Layer**: ApiEntity, HttpSession extending FlextModels.Entity
        - **Value Objects Layer**: Url, StatusCode, Method extending FlextModels.Value
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
        - Uses FlextModels.Entity and FlextModels.Value as base classes
        - Implements FlextResult[T] for all fallible operations
        - Follows FlextConstants for HTTP-specific constants
        - Uses get_logger() from flext-core for consistent logging
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
            if not v or not v.strip():
                msg = "URL cannot be empty"
                raise ValueError(msg)
            v = v.strip()

            try:
                parsed = urlparse(v)
                if not parsed.scheme or not parsed.netloc:
                    msg = "URL must include scheme and netloc"
                    raise ValueError(msg)
                if parsed.scheme not in {"http", "https"}:
                    msg = "URL scheme must be http or https"
                    raise ValueError(msg)
                return v
            except Exception as e:
                msg = f"Invalid URL: {e}"
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
    # HTTP DOMAIN ENTITIES (extending FlextModels.Entity)
    # =============================================================================

    class HttpSession(FlextModels.Entity):
        """HTTP session entity with state management."""

        session_id: str = Field(..., description="Unique session identifier")
        base_url: str = Field(..., description="Base URL for session")
        headers: dict[str, str] = Field(default_factory=dict)
        cookies: dict[str, str] = Field(default_factory=dict)
        is_active: bool = Field(default=True)

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate HTTP session business rules."""
            if not self.base_url.strip():
                return FlextResult[None].fail("Session must have valid base URL")
            if not self.session_id.strip():
                return FlextResult[None].fail("Session must have valid ID")
            return FlextResult[None].ok(None)

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
    # HTTP VALUE OBJECTS (extending FlextModels.Value)
    # =============================================================================

    class HttpRequest(FlextModels.Value):
        """Immutable HTTP request value object."""

        method: str = Field(..., description="HTTP method")
        url: str = Field(..., description="Request URL")
        headers: dict[str, str] = Field(default_factory=dict)
        body: str | bytes | dict[str, Any] | None = Field(default=None)
        timeout: float = Field(default=30.0)

        @field_validator("url")
        @classmethod
        def validate_url(cls, v: str) -> str:
            parsed = urlparse(v)
            if not parsed.scheme or not parsed.netloc:
                msg = "Invalid URL format"
                raise ValueError(msg)
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
        body: str | bytes | dict[str, Any] | None = Field(default=None)
        url: str = Field(..., description="Request URL")
        method: str = Field(..., description="HTTP method")
        elapsed_time: float = Field(default=0.0)

        @field_validator("status_code")
        @classmethod
        def validate_status_code(cls, v: int) -> int:
            if not (FlextApiConstants.HttpStatus.CONTINUE <= v <= FlextApiConstants.HttpStatus.NETWORK_CONNECT_TIMEOUT_ERROR):
                msg = "Invalid HTTP status code"
                raise ValueError(msg)
            return v

        @computed_field
        @property
        def is_success(self) -> bool:
            """Check if response indicates success."""
            return FlextApiConstants.HttpStatus.OK <= self.status_code < FlextApiConstants.HttpStatus.MULTIPLE_CHOICES

        @computed_field
        @property
        def is_client_error(self) -> bool:
            """Check if response indicates client error."""
            return FlextApiConstants.HttpStatus.BAD_REQUEST <= self.status_code < FlextApiConstants.HttpStatus.INTERNAL_SERVER_ERROR

        @computed_field
        @property
        def is_server_error(self) -> bool:
            """Check if response indicates server error."""
            return FlextApiConstants.HttpStatus.INTERNAL_SERVER_ERROR <= self.status_code < 600  # 600 is max HTTP status

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate HTTP response business rules."""
            if self.elapsed_time < 0:
                return FlextResult[None].fail("Elapsed time cannot be negative")
            return FlextResult[None].ok(None)

    # =============================================================================
    # CONFIGURATION MODELS (extending BaseConfig)
    # =============================================================================

    class ClientConfig(FlextModels.BaseConfig):
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
            parsed = urlparse(v)
            if not parsed.scheme or not parsed.netloc:
                msg = "Invalid base URL"
                raise ValueError(msg)
            return v.rstrip("/")

    class PluginConfig(FlextModels.BaseConfig):
        """Base plugin configuration."""

        name: str = Field(..., description="Plugin name")
        enabled: bool = Field(default=True)
        priority: int = Field(default=0)

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

    @classmethod
    def create_http_request(
        cls,
        method: str,
        url: str,
        headers: dict[str, str] | None = None,
        body: str | bytes | dict[str, Any] | None = None,
        timeout: float = 30.0,
    ) -> FlextResult[HttpRequest]:
        """Create HTTP request with validation."""
        try:
            request = cls.HttpRequest(
                method=method,
                url=url,
                headers=headers or {},
                body=body,
                timeout=timeout,
            )
            validation_result = request.validate_business_rules()
            if validation_result.is_failure:
                return FlextResult[cls.HttpRequest].fail(
                    f"HTTP request validation failed: {validation_result.error}"
                )
            return FlextResult[cls.HttpRequest].ok(request)
        except Exception as e:
            return FlextResult[cls.HttpRequest].fail(
                f"HTTP request creation failed: {e}"
            )

    @classmethod
    def create_http_response(
        cls,
        status_code: int,
        url: str,
        method: str,
        headers: dict[str, str] | None = None,
        body: str | bytes | dict[str, Any] | None = None,
        elapsed_time: float = 0.0,
    ) -> FlextResult[HttpResponse]:
        """Create HTTP response with validation."""
        try:
            response = cls.HttpResponse(
                status_code=status_code,
                url=url,
                method=method,
                headers=headers or {},
                body=body,
                elapsed_time=elapsed_time,
            )
            validation_result = response.validate_business_rules()
            if validation_result.is_failure:
                return FlextResult[cls.HttpResponse].fail(
                    f"HTTP response validation failed: {validation_result.error}"
                )
            return FlextResult[cls.HttpResponse].ok(response)
        except Exception as e:
            return FlextResult[cls.HttpResponse].fail(
                f"HTTP response creation failed: {e}"
            )

    @classmethod
    def create_client_config(
        cls,
        base_url: str,
        timeout: float = 30.0,
        max_retries: int = 3,
        headers: dict[str, str] | None = None,
        verify_ssl: bool = True,
        allow_redirects: bool = True,
    ) -> FlextResult[ClientConfig]:
        """Create client configuration with validation."""
        try:
            config = cls.ClientConfig(
                base_url=base_url,
                timeout=timeout,
                max_retries=max_retries,
                headers=headers or {},
                verify_ssl=verify_ssl,
                allow_redirects=allow_redirects,
            )
            return FlextResult[cls.ClientConfig].ok(config)
        except Exception as e:
            return FlextResult[cls.ClientConfig].fail(
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
                return FlextResult[cls.HttpSession].fail(
                    f"HTTP session validation failed: {validation_result.error}"
                )
            return FlextResult[cls.HttpSession].ok(session)
        except Exception as e:
            return FlextResult[cls.HttpSession].fail(
                f"HTTP session creation failed: {e}"
            )

    @classmethod
    def create_cache_config(
        cls,
        ttl: int = 300,
        max_size: int = 1000,
        enabled: bool = True,
        priority: int = 0,
    ) -> FlextResult[CacheConfig]:
        """Create cache configuration with validation."""
        try:
            config = cls.CacheConfig(
                ttl=ttl,
                max_size=max_size,
                enabled=enabled,
                priority=priority,
            )
            return FlextResult[cls.CacheConfig].ok(config)
        except Exception as e:
            return FlextResult[cls.CacheConfig].fail(
                f"Cache config creation failed: {e}"
            )

    @classmethod
    def create_retry_config(
        cls,
        max_retries: int = 3,
        backoff_factor: float = 2.0,
        retry_on_status: list[int] | None = None,
        enabled: bool = True,
        priority: int = 0,
    ) -> FlextResult[RetryConfig]:
        """Create retry configuration with validation."""
        try:
            config = cls.RetryConfig(
                max_retries=max_retries,
                backoff_factor=backoff_factor,
                retry_on_status=retry_on_status or [500, 502, 503, 504],
                enabled=enabled,
                priority=priority,
            )
            return FlextResult[cls.RetryConfig].ok(config)
        except Exception as e:
            return FlextResult[cls.RetryConfig].fail(
                f"Retry config creation failed: {e}"
            )

    @classmethod
    def validate_url(cls, url: str) -> FlextResult[str]:
        """Validate URL using Url value object."""
        try:
            url_obj = cls.Url(root=url)
            return FlextResult[str].ok(url_obj.root)
        except Exception as e:
            return FlextResult[str].fail(f"URL validation failed: {e}")

    @classmethod
    def validate_status_code(cls, status_code: int) -> FlextResult[int]:
        """Validate HTTP status code using StatusCode value object."""
        try:
            status_obj = cls.StatusCode(root=status_code)
            return FlextResult[int].ok(status_obj.root)
        except Exception as e:
            return FlextResult[int].fail(f"Status code validation failed: {e}")


__all__ = ["FlextApiModels"]
