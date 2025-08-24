"""FLEXT API domain models.

Este módulo implementa modelos de domínio usando padrões FLEXT Core centralizados,
eliminando duplicação de código e garantindo consistência arquitetural.

Padrões FLEXT aplicados:
- FlextModel como base para todos os modelos Pydantic
- FlextResult para operações que podem falhar
- Imports diretos sem TYPE_CHECKING
- Tipos centralizados do flext-core
"""

from __future__ import annotations

import math
from datetime import UTC, datetime, timedelta
from enum import IntEnum, StrEnum
from typing import override
from urllib.parse import ParseResult, urlparse

from flext_core import (
    FlextEntity,
    FlextModel,
    FlextResult,
    FlextTimestamp,
    flext_alias_generator,
    get_logger,
)
from pydantic import (
    AliasGenerator,
    ConfigDict as PydanticConfigDict,
    Field,
    field_validator,
)

from flext_api.constants import FlextApiConstants
from flext_api.typings import HeadersDict, HttpUrl

logger = get_logger(__name__)

# ==============================================================================
# CONSTANTS
# ==============================================================================

MIN_PORT: int = 1
MAX_PORT: int = 65535
MIN_TOKEN_LENGTH: int = 16
JWT_PARTS_COUNT: int = 3
MIN_CONTROL_CHAR: int = 32
MIN_HTTP_STATUS: int = 100
MAX_HTTP_STATUS: int = 599
DEFAULT_TIMEOUT: float = 30.0
DEFAULT_PAGE_SIZE: int = 20
DEFAULT_MAX_RETRIES: int = 3

HTTP_STATUS_RANGES: dict[str, tuple[int, int]] = {
    "INFORMATIONAL": (100, 200),
    "SUCCESS": (200, 300),
    "REDIRECTION": (300, 400),
    "CLIENT_ERROR": (400, 500),
    "SERVER_ERROR": (500, 600),
}

# ==============================================================================
# ENUMERATIONS
# ==============================================================================


class HttpMethod(StrEnum):
    """HTTP method enumeration."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"
    TRACE = "TRACE"


class HttpStatus(IntEnum):
    """HTTP status code enumeration with semantic categories."""

    # 1xx Informational
    CONTINUE = 100
    SWITCHING_PROTOCOLS = 101
    PROCESSING = 102

    # 2xx Success
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204
    PARTIAL_CONTENT = 206

    # 3xx Redirection
    MOVED_PERMANENTLY = 301
    FOUND = 302
    NOT_MODIFIED = 304
    TEMPORARY_REDIRECT = 307

    # 4xx Client Error
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    CONFLICT = 409
    GONE = 410
    UNPROCESSABLE_ENTITY = 422
    TOO_MANY_REQUESTS = 429

    # 5xx Server Error
    INTERNAL_SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503
    GATEWAY_TIMEOUT = 504

    @property
    def is_informational(self) -> bool:
        """Check if status is informational (1xx)."""
        return (
            HTTP_STATUS_RANGES["INFORMATIONAL"][0]
            <= self.value
            < HTTP_STATUS_RANGES["INFORMATIONAL"][1]
        )

    @property
    def is_success(self) -> bool:
        """Check if status indicates success (2xx)."""
        return (
            HTTP_STATUS_RANGES["SUCCESS"][0]
            <= self.value
            < HTTP_STATUS_RANGES["SUCCESS"][1]
        )

    @property
    def is_redirection(self) -> bool:
        """Check if status indicates redirection (3xx)."""
        return (
            HTTP_STATUS_RANGES["REDIRECTION"][0]
            <= self.value
            < HTTP_STATUS_RANGES["REDIRECTION"][1]
        )

    @property
    def is_client_error(self) -> bool:
        """Check if status indicates client error (4xx)."""
        return (
            HTTP_STATUS_RANGES["CLIENT_ERROR"][0]
            <= self.value
            < HTTP_STATUS_RANGES["CLIENT_ERROR"][1]
        )

    @property
    def is_server_error(self) -> bool:
        """Check if status indicates server error (5xx)."""
        return (
            HTTP_STATUS_RANGES["SERVER_ERROR"][0]
            <= self.value
            < HTTP_STATUS_RANGES["SERVER_ERROR"][1]
        )


class ClientProtocol(StrEnum):
    """Supported client protocols."""

    HTTP = "http"
    HTTPS = "https"


class ClientStatus(StrEnum):
    """Client status enumeration."""

    IDLE = "idle"
    ACTIVE = "active"
    RUNNING = "running"
    STOPPED = "stopped"
    CLOSED = "closed"
    ERROR = "error"


class RequestState(StrEnum):
    """API request processing states."""

    CREATED = "created"
    VALIDATED = "validated"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ResponseState(StrEnum):
    """API response states."""

    PENDING = "pending"
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"


class TokenType(StrEnum):
    """Token type enumeration."""

    BEARER = "Bearer"
    JWT = "JWT"
    API_KEY = "ApiKey"


class OperationType(StrEnum):
    """API operation types."""

    QUERY = "query"
    RESPONSE = "response"
    BATCH = "batch"
    STREAM = "stream"


# ==============================================================================
# VALUE OBJECTS (Immutable)
# ==============================================================================


class URL(FlextModel):
    """HTTP URL value object following FlextModel foundation pattern.

    Immutable URL representation with validation, parsing, and domain behavior.
    Uses centralized FlextModel patterns from flext-core.
    """

    model_config = PydanticConfigDict(
        # Inherit from FlextModel base configuration
        alias_generator=AliasGenerator(
            alias=flext_alias_generator,
            validation_alias=flext_alias_generator,
            serialization_alias=flext_alias_generator,
        ),
        extra="allow",
        validate_assignment=True,
        use_enum_values=True,
        str_strip_whitespace=True,
        arbitrary_types_allowed=True,
        validate_default=True,
        populate_by_name=True,
        frozen=True,  # Immutable value object
        use_attribute_docstrings=True,
        json_schema_extra={
            "examples": [],
            "description": "HTTP URL value object with modern FlextModel patterns",
            "title": "URL",
        },
    )

    raw_url: str = Field(description="Raw URL string")
    scheme: str = Field(description="URL scheme (http/https)")
    host: str = Field(description="Host portion")
    port: int | None = Field(None, description="Port number")
    path: str = Field(default="/", description="URL path")
    query: str | None = Field(None, description="Query string")
    fragment: str | None = Field(None, description="URL fragment")

    @field_validator("raw_url")
    @classmethod
    def validate_raw_url(cls, v: str) -> str:
        """Validate URL string is non-empty."""
        if not v or not v.strip():
            msg = "URL cannot be empty"
            raise ValueError(msg)
        return v.strip()

    @field_validator("scheme")
    @classmethod
    def validate_scheme(cls, v: str) -> str:
        """Validate URL scheme is http or https."""
        if v not in {"http", "https"}:
            msg = f"Invalid URL scheme: {v}"
            raise ValueError(msg)
        return v

    @field_validator("host")
    @classmethod
    def validate_host(cls, v: str) -> str:
        """Validate host is non-empty."""
        if not v or not v.strip():
            msg = "URL must have a valid host"
            raise ValueError(msg)
        return v.strip()

    @field_validator("port")
    @classmethod
    def validate_port(cls, v: int | None) -> int | None:
        """Validate port number is within valid range."""
        if v is not None and not (MIN_PORT <= v <= MAX_PORT):
            msg = f"Invalid port number: {v}"
            raise ValueError(msg)
        return v

    @override
    def validate_business_rules(self) -> FlextResult[None]:
        """Validate URL business rules following foundation pattern."""
        if not self.raw_url or not self.raw_url.strip():
            return FlextResult[None].fail("URL cannot be empty")

        if self.scheme not in {"http", "https"}:
            return FlextResult[None].fail(f"Invalid URL scheme: {self.scheme}")

        if not self.host or not self.host.strip():
            return FlextResult[None].fail("URL must have a valid host")

        if self.port is not None and not (MIN_PORT <= self.port <= MAX_PORT):
            return FlextResult[None].fail(f"Invalid port number: {self.port}")

        return FlextResult[None].ok(None)

    @classmethod
    def create(cls, url: str) -> FlextResult[URL]:
        """Create URL with validation following foundation pattern."""
        try:
            parsed: ParseResult = urlparse(url)

            instance = cls(
                raw_url=url,
                scheme=parsed.scheme or "https",
                host=parsed.hostname or "",
                port=parsed.port,
                path=parsed.path or "/",
                query=parsed.query or None,
                fragment=parsed.fragment or None,
            )

            validation_result = instance.validate_business_rules()
            if not validation_result:
                return FlextResult[URL].fail(
                    f"URL validation failed: {validation_result.error}",
                )

            return FlextResult[URL].ok(instance)
        except (RuntimeError, ValueError, TypeError, KeyError) as e:
            return FlextResult[URL].fail(f"URL parsing failed: {e}")

    def is_secure(self) -> bool:
        """Check if URL uses HTTPS."""
        return self.scheme == "https"

    def base_url(self) -> str:
        """Get base URL without path, query, or fragment."""
        port_part = f":{self.port}" if self.port else ""
        return f"{self.scheme}://{self.host}{port_part}"

    def full_path(self) -> str:
        """Get full path including query and fragment (no scheme/host)."""
        path_part = self.path or "/"
        query_part = f"?{self.query}" if self.query else ""
        fragment_part = f"#{self.fragment}" if self.fragment else ""
        return f"{path_part}{query_part}{fragment_part}"


class HttpHeader(FlextModel):
    """HTTP header value object following FlextModel foundation pattern.

    Uses centralized FlextModel patterns from flext-core for consistent validation
    and serialization across the FLEXT ecosystem.
    """

    model_config = PydanticConfigDict(
        # Inherit from FlextModel base configuration
        alias_generator=AliasGenerator(
            alias=flext_alias_generator,
            validation_alias=flext_alias_generator,
            serialization_alias=flext_alias_generator,
        ),
        extra="allow",
        validate_assignment=True,
        use_enum_values=True,
        str_strip_whitespace=True,
        arbitrary_types_allowed=True,
        validate_default=True,
        populate_by_name=True,
        frozen=True,  # Immutable value object
        use_attribute_docstrings=True,
        json_schema_extra={
            "examples": [],
            "description": "HTTP header value object with modern FlextModel patterns",
            "title": "HttpHeader",
        },
    )

    name: str = Field(description="Header name")
    value: str = Field(description="Header value")

    @override
    def validate_business_rules(self) -> FlextResult[None]:
        """Validate header business rules."""
        if not self.name or not self.name.strip():
            return FlextResult[None].fail("Header name cannot be empty")

        if not self.value or not self.value.strip():
            return FlextResult[None].fail("Header value cannot be empty")

        # Header name validation (no control characters)
        if any(ord(c) < MIN_CONTROL_CHAR for c in self.name):
            return FlextResult[None].fail("Header name contains invalid characters")

        return FlextResult[None].ok(None)

    @classmethod
    def create(cls, name: str, value: str) -> FlextResult[HttpHeader]:
        """Create HTTP header with validation.

        Args:
            name: Header name
            value: Header value

        Returns:
            FlextResult containing HttpHeader or error

        """

        # Validation helper
        def validate_header_input() -> str | None:
            """Validate header input and return error message if invalid."""
            # Validate header name
            if not name or not name.strip():
                return "Header name cannot be empty"

            # RFC 7230 header name validation - no spaces or special characters allowed
            if " " in name:
                return "Invalid header name"

            # Check for common invalid characters in header names
            invalid_chars = '@(){}[]<>\\"/?='
            if any(char in name for char in invalid_chars):
                return "Invalid header name"

            if any(ord(char) < MIN_CONTROL_CHAR for char in name):
                return "Header name contains invalid control characters"

            # Validate header value
            if any(ord(char) < MIN_CONTROL_CHAR and char != "\t" for char in value):
                return "Header value contains invalid control characters"

            return None

        # Perform validation
        error = validate_header_input()
        if error:
            return FlextResult[HttpHeader].fail(error)

        # Create header
        try:
            header = cls(name=name.strip(), value=value)
            return FlextResult[HttpHeader].ok(header)
        except Exception as e:
            return FlextResult[HttpHeader].fail(f"Failed to create header: {e}")

    def is_authorization(self) -> bool:
        """Check if this is an authorization header."""
        return self.name.lower() == "authorization"

    def is_content_type(self) -> bool:
        """Check if this is a content-type header."""
        return self.name.lower() == "content-type"

    @override
    def to_dict(
        self,
        *,
        by_alias: bool = False,
        exclude_none: bool = False,
    ) -> dict[str, object]:
        """Convert to dictionary representation."""
        _ = by_alias, exclude_none  # Parameters maintained for compatibility
        return {self.name: self.value}

    def to_tuple(self) -> tuple[str, str]:
        """Convert to tuple format."""
        return (self.name, self.value)


class BearerToken(FlextModel):
    """Bearer token value object with JWT format validation.

    Uses centralized FlextModel patterns from flext-core for consistent token
    validation and serialization across the FLEXT ecosystem.
    """

    model_config = PydanticConfigDict(
        # Inherit from FlextModel base configuration
        alias_generator=AliasGenerator(
            alias=flext_alias_generator,
            validation_alias=flext_alias_generator,
            serialization_alias=flext_alias_generator,
        ),
        extra="allow",
        validate_assignment=True,
        use_enum_values=True,
        str_strip_whitespace=True,
        arbitrary_types_allowed=True,
        validate_default=True,
        populate_by_name=True,
        frozen=True,  # Immutable value object
        use_attribute_docstrings=True,
        json_schema_extra={
            "examples": [],
            "description": "Bearer token value object with modern FlextModel patterns",
            "title": "BearerToken",
        },
    )

    token: str = Field(description="Bearer token string")
    token_type: TokenType = Field(default=TokenType.BEARER, description="Token type")
    expires_at: datetime | None = Field(None, description="Token expiration")

    @field_validator("token")
    @classmethod
    def validate_token(cls, v: str) -> str:
        """Validate bearer token format and length."""
        if not v or not v.strip():
            msg = "Bearer token cannot be empty"
            raise ValueError(msg)

        v = v.strip()
        if len(v) < MIN_TOKEN_LENGTH:
            msg = f"Token must be at least {MIN_TOKEN_LENGTH} characters"
            raise ValueError(msg)

        # JWT format validation - check for empty parts in any 3-part token
        if v.count(".") == FlextApiConstants.Auth.JWT_SEPARATOR_COUNT:
            parts = v.split(".")
            if len(parts) == FlextApiConstants.Auth.JWT_PARTS_COUNT and not all(
                part.strip() for part in parts
            ):
                msg = "JWT format error - empty parts not allowed"
                raise ValueError(msg)

        return v

    @override
    def validate_business_rules(self) -> FlextResult[None]:
        """Validate bearer token business rules."""
        if not self.token or not self.token.strip():
            return FlextResult[None].fail("Bearer token cannot be empty")

        if len(self.token.strip()) < MIN_TOKEN_LENGTH:
            return FlextResult[None].fail(
                f"Token must be at least {MIN_TOKEN_LENGTH} characters",
            )

        # JWT format validation - check for empty parts in any 3-part token

        if self.token.count(".") == FlextApiConstants.Auth.JWT_SEPARATOR_COUNT:
            parts = self.token.split(".")
            if len(parts) == FlextApiConstants.Auth.JWT_PARTS_COUNT and not all(
                part.strip() for part in parts
            ):
                return FlextResult[None].fail(
                    "JWT format error - empty parts not allowed"
                )

        return FlextResult[None].ok(None)

    @classmethod
    def create(
        cls,
        token: str,
        token_type: str | TokenType | None = None,
    ) -> FlextResult[BearerToken]:
        """Create bearer token with validation."""
        # Normalize token type
        token_type_enum: TokenType
        if token_type is None:
            token_type_enum = TokenType.BEARER
        elif isinstance(token_type, TokenType):  # Check enum first (subclass of str)
            token_type_enum = token_type
        elif isinstance(token_type, str):
            valid_types = [t.value for t in TokenType]
            if token_type not in valid_types:
                return FlextResult[BearerToken].fail(
                    f"Invalid token type: {token_type}"
                )
            token_type_enum = TokenType(token_type)
        # No else branch needed: all union members are covered above

        try:
            instance = cls(token=token, token_type=token_type_enum, expires_at=None)
        except Exception as e:
            return FlextResult[BearerToken].fail(f"Token creation failed: {e}")

        validation_result = instance.validate_business_rules()
        if not validation_result:
            return FlextResult[BearerToken].fail(
                validation_result.error or "Token validation failed",
            )
        return FlextResult[BearerToken].ok(instance)

    def is_expired(self) -> bool:
        """Check if token is expired."""
        if not self.expires_at:
            return False
        return datetime.now(UTC) >= self.expires_at

    def is_jwt_format(self) -> bool:
        """Check if token follows JWT format (3 parts separated by dots)."""
        parts = self.token.split(".")
        return len(parts) == JWT_PARTS_COUNT and all(part.strip() for part in parts)

    def to_authorization_header(self) -> HttpHeader:
        """Convert to authorization header."""
        token_type_str = (
            self.token_type.value
            if hasattr(self.token_type, "value")
            else str(self.token_type)
        )
        header_value = f"{token_type_str} {self.token}"
        # Direct instantiation since we know the values are valid
        return HttpHeader(name="Authorization", value=header_value)

    def get_raw_token(self) -> str:
        """Get raw token value."""
        return self.token


class ClientConfig(FlextModel):
    """Client configuration value object with validation.

    Uses centralized FlextModel patterns from flext-core for consistent configuration
    management across the FLEXT ecosystem.
    """

    model_config = PydanticConfigDict(
        # Inherit from FlextModel base configuration
        alias_generator=AliasGenerator(
            alias=flext_alias_generator,
            validation_alias=flext_alias_generator,
            serialization_alias=flext_alias_generator,
        ),
        # FlextModel patterns: immutable configuration object
        extra="allow",
        validate_assignment=True,
        use_enum_values=True,
        str_strip_whitespace=True,
        arbitrary_types_allowed=True,
        validate_default=True,
        populate_by_name=True,
        frozen=True,  # Immutable value object
        use_attribute_docstrings=True,
        json_schema_extra={
            "examples": [],
            "description": "Client configuration value object with modern FlextModel patterns",
            "title": "ClientConfig",
        },
    )

    base_url: HttpUrl = Field(description="Base URL for requests")
    timeout: float = Field(default=DEFAULT_TIMEOUT, description="Request timeout")
    headers: HeadersDict = Field(default_factory=dict, description="Default headers")
    max_retries: int = Field(
        default=DEFAULT_MAX_RETRIES,
        description="Maximum retry attempts",
    )

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, v: str) -> str:
        """Validate base URL format."""
        if not v:
            msg = "base_url is required"
            raise ValueError(msg)

        if not v.startswith(("http://", "https://")):
            msg = "Invalid URL format"
            raise ValueError(msg)

        return v

    @field_validator("timeout")
    @classmethod
    def validate_timeout(cls, v: float) -> float:
        """Validate timeout is positive."""
        if v <= 0:
            msg = "Timeout must be positive"
            raise ValueError(msg)
        return v

    @field_validator("max_retries")
    @classmethod
    def validate_max_retries(cls, v: int) -> int:
        """Validate max retries is non-negative."""
        if v < 0:
            msg = "Max retries must be non-negative"
            raise ValueError(msg)
        return v

    @override
    def validate_business_rules(self) -> FlextResult[None]:
        """Validate configuration business rules."""
        if not self.base_url:
            return FlextResult[None].fail("base_url is required")

        if not self.base_url.startswith(("http://", "https://")):
            return FlextResult[None].fail("Invalid URL format")

        if self.timeout <= 0:
            return FlextResult[None].fail("Timeout must be positive")

        if self.max_retries < 0:
            return FlextResult[None].fail("Max retries must be non-negative")

        return FlextResult[None].ok(None)


class QueryConfig(FlextModel):
    """Query configuration value object following FlextModel foundation pattern.

    Uses centralized FlextModel patterns from flext-core for consistent query
    configuration across the FLEXT ecosystem.
    """

    model_config = PydanticConfigDict(
        # Inherit from FlextModel base configuration
        alias_generator=AliasGenerator(
            alias=flext_alias_generator,
            validation_alias=flext_alias_generator,
            serialization_alias=flext_alias_generator,
        ),
        extra="allow",
        validate_assignment=True,
        use_enum_values=True,
        str_strip_whitespace=True,
        arbitrary_types_allowed=True,
        validate_default=True,
        populate_by_name=True,
        frozen=True,  # Immutable value object
        use_attribute_docstrings=True,
        json_schema_extra={
            "examples": [],
            "description": "Query configuration value object with modern FlextModel patterns",
            "title": "QueryConfig",
        },
    )

    filters: list[dict[str, object]] = Field(default_factory=list[dict[str, object]])
    sorts: list[dict[str, str]] = Field(default_factory=list[dict[str, str]])
    page: int = Field(default=1)
    page_size: int = Field(default=DEFAULT_PAGE_SIZE)
    search: str | None = None
    fields: list[str] | None = None

    @override
    def validate_business_rules(self) -> FlextResult[None]:
        """Validate query configuration."""
        if self.page <= 0:
            return FlextResult[None].fail("Page must be positive")

        if self.page_size <= 0:
            return FlextResult[None].fail("Page size must be positive")

        return FlextResult[None].ok(None)

    @override
    def to_dict(
        self,
        *,
        by_alias: bool = False,
        exclude_none: bool = False,
    ) -> dict[str, object]:
        """Convert to dictionary representation."""
        _ = by_alias, exclude_none  # Parameters maintained for compatibility
        return {
            "filters": self.filters,
            "sorts": self.sorts,
            "page": self.page,
            "page_size": self.page_size,
            "limit": self.page_size,
            "offset": (self.page - 1) * self.page_size,
            "search": self.search,
            "fields": self.fields,
        }


class PaginationInfo(FlextModel):
    """Pagination information value object following FlextModel foundation pattern.

    Uses centralized FlextModel patterns from flext-core for consistent pagination
    information across the FLEXT ecosystem.
    """

    model_config = PydanticConfigDict(
        # Inherit from FlextModel base configuration
        alias_generator=AliasGenerator(
            alias=flext_alias_generator,
            validation_alias=flext_alias_generator,
            serialization_alias=flext_alias_generator,
        ),
        # FlextModel patterns: immutable with validation
        extra="allow",
        validate_assignment=True,
        use_enum_values=True,
        str_strip_whitespace=True,
        arbitrary_types_allowed=True,
        validate_default=True,
        populate_by_name=True,
        frozen=True,  # Immutable value object
        use_attribute_docstrings=True,
        json_schema_extra={
            "examples": [],
            "description": "Pagination information value object with modern FlextModel patterns",
            "title": "PaginationInfo",
        },
    )

    page: int = Field(ge=1, description="Current page number")
    page_size: int = Field(ge=1, description="Items per page")
    total: int = Field(ge=0, description="Total items count")
    total_pages: int = Field(ge=0, description="Total pages count")
    has_next: bool = Field(description="Has next page")
    has_previous: bool = Field(description="Has previous page")

    @classmethod
    def create(
        cls,
        page: int,
        page_size: int,
        total: int,
    ) -> FlextResult[PaginationInfo]:
        """Create pagination info with validation."""
        try:
            total_pages = math.ceil(total / page_size) if page_size > 0 else 0
            has_next = page < total_pages
            has_previous = page > 1

            instance = cls(
                page=page,
                page_size=page_size,
                total=total,
                total_pages=total_pages,
                has_next=has_next,
                has_previous=has_previous,
            )

            validation = instance.validate_business_rules()
            if not validation:
                return FlextResult[PaginationInfo].fail(
                    validation.error or "Validation failed"
                )

            return FlextResult[PaginationInfo].ok(instance)
        except Exception as e:
            return FlextResult[PaginationInfo].fail(
                f"Failed to create pagination info: {e}"
            )


# ==============================================================================
# ENTITIES (With Identity)
# ==============================================================================


class ApiRequest(FlextEntity):
    """HTTP request entity with lifecycle management."""

    model_config = PydanticConfigDict(
        alias_generator=AliasGenerator(
            alias=flext_alias_generator,
            validation_alias=flext_alias_generator,
            serialization_alias=flext_alias_generator,
        ),
        extra="allow",
        validate_assignment=True,
        use_enum_values=True,
        str_strip_whitespace=True,
        arbitrary_types_allowed=True,
        validate_default=True,
        populate_by_name=True,
        frozen=False,  # Mutable entity
    )

    method: HttpMethod = Field(description="HTTP method")
    url: str = Field(description="Request URL")
    headers: dict[str, str] = Field(default_factory=dict, description="HTTP headers")
    body: dict[str, object] | None = Field(None, description="Request body")
    query_params: dict[str, str] = Field(
        default_factory=dict,
        description="Query parameters",
    )
    state: RequestState = Field(
        default=RequestState.CREATED,
        description="Request state",
    )
    timeout: float = Field(default=DEFAULT_TIMEOUT, description="Request timeout")
    retry_count: int = Field(default=0, description="Current retry count")
    max_retries: int = Field(default=DEFAULT_MAX_RETRIES, description="Maximum retries")

    # NOTE: Using FlextTimestamp from FlextEntity base class for lifecycle fields

    @override
    def validate_business_rules(self) -> FlextResult[None]:
        """Validate request business rules."""
        # Consolidated validation checks
        checks = [
            (not self.url or not self.url.strip(), "Request URL cannot be empty"),
            (
                not self.url.startswith(("http://", "https://", "/")),
                "Request URL must be valid HTTP URL or path",
            ),
            (self.method not in HttpMethod, f"Invalid HTTP method: {self.method}"),
            (self.timeout <= 0, "Timeout must be positive"),
        ]

        # Check basic validations
        for condition, message in checks:
            if condition:
                return FlextResult[None].fail(message)

        # Check headers if they exist
        if self.headers:
            for key, value in self.headers.items():
                if not key:
                    return FlextResult[None].fail(
                        "Header keys must be non-empty strings"
                    )
                if not value:
                    return FlextResult[None].fail("Header values cannot be empty")

        return FlextResult[None].ok(None)

    def can_retry(self) -> bool:
        """Check if request can be retried."""
        return self.retry_count < self.max_retries

    def increment_retry(self) -> FlextResult[ApiRequest]:
        """Increment retry count."""
        if not self.can_retry():
            return FlextResult[ApiRequest].fail("Maximum retries exceeded")

        updated = self.model_copy(
            update={
                "retry_count": self.retry_count + 1,
                "updated_at": FlextTimestamp.now(),
            },
        )
        return FlextResult[ApiRequest].ok(updated)

    def start_processing(self) -> FlextResult[ApiRequest]:
        """Start request processing with state transition."""
        if self.state != RequestState.VALIDATED:
            return FlextResult[ApiRequest].fail(
                f"Cannot start processing from state: {self.state}"
            )

        updated = self.model_copy(
            update={
                "state": RequestState.PROCESSING,
                "updated_at": FlextTimestamp.now(),
            },
        )
        logger.info("Request processing started", request_id=self.id)
        return FlextResult[ApiRequest].ok(updated)

    def complete_processing(self) -> FlextResult[ApiRequest]:
        """Complete request processing."""
        if self.state != RequestState.PROCESSING:
            return FlextResult[ApiRequest].fail(
                f"Cannot complete from state: {self.state}"
            )

        updated = self.model_copy(
            update={
                "state": RequestState.COMPLETED,
                "updated_at": FlextTimestamp.now(),
            },
        )
        logger.info("Request processing completed", request_id=self.id)
        return FlextResult[ApiRequest].ok(updated)

    def fail_processing(self, error: str) -> FlextResult[ApiRequest]:
        """Mark request as failed."""
        updated = self.model_copy(
            update={
                "state": RequestState.FAILED,
                "updated_at": FlextTimestamp.now(),
            },
        )
        logger.error("Request processing failed", request_id=self.id, error=error)
        return FlextResult[ApiRequest].ok(updated)


class ApiResponse(FlextEntity):
    """HTTP response entity with state management."""

    model_config = PydanticConfigDict(
        # Inherit modern Pydantic patterns from FlextEntity
        alias_generator=AliasGenerator(
            alias=flext_alias_generator,
            validation_alias=flext_alias_generator,
            serialization_alias=flext_alias_generator,
        ),
        # FlextEntity patterns: mutable with lifecycle management
        extra="allow",
        validate_assignment=True,
        use_enum_values=True,
        str_strip_whitespace=True,
        arbitrary_types_allowed=True,
        validate_default=True,
        populate_by_name=True,
        frozen=False,  # Mutable entity
        use_attribute_docstrings=True,
        json_schema_extra={
            "examples": [],
            "description": "HTTP response entity with modern Pydantic patterns and state management",
            "title": "ApiResponse",
        },
    )

    status_code: int = Field(description="HTTP status code")
    headers: dict[str, str] = Field(
        default_factory=dict,
        description="Response headers",
    )
    body: dict[str, object] | None = Field(None, description="Response body")
    state: ResponseState = Field(
        default=ResponseState.PENDING,
        description="Response state",
    )
    request_id: str | None = Field(None, description="Associated request ID")
    elapsed_time: float = Field(default=0.0, description="Response time in seconds")
    from_cache: bool = Field(default=False, description="Response from cache")
    error_message: str | None = Field(None, description="Error message if failed")

    # NOTE: Using FlextTimestamp from FlextEntity base class for lifecycle fields

    @override
    def validate_business_rules(self) -> FlextResult[None]:
        """Validate response business rules."""
        if not (MIN_HTTP_STATUS <= self.status_code <= MAX_HTTP_STATUS):
            return FlextResult[None].fail(
                f"Invalid HTTP status code: {self.status_code}"
            )

        if self.headers:
            for key, value in self.headers.items():
                if not key:
                    return FlextResult[None].fail(
                        "Response header keys must be non-empty strings",
                    )
                # Only reject empty strings (value is always str in dict[str, str])
                if not value.strip():
                    return FlextResult[None].fail(
                        "Response header values cannot be empty"
                    )

        return FlextResult[None].ok(None)

    def is_success(self) -> bool:
        """Check if response is successful."""
        return (
            FlextApiConstants.HTTP.SUCCESS_MIN
            <= self.status_code
            < FlextApiConstants.HTTP.SUCCESS_MAX
        )

    def is_error(self) -> bool:
        """Check if response is error."""
        return self.status_code >= FlextApiConstants.HTTP.CLIENT_ERROR_MIN

    def mark_success(self) -> FlextResult[ApiResponse]:
        """Mark response as successful."""
        updated = self.model_copy(
            update={
                "state": ResponseState.SUCCESS,
                "updated_at": FlextTimestamp.now(),
            },
        )
        logger.info("Response marked as success", response_id=self.id)
        return FlextResult[ApiResponse].ok(updated)

    def mark_error(self, error_message: str) -> FlextResult[ApiResponse]:
        """Mark response as error with message."""
        error_body: dict[str, object] = {
            "error": error_message,
            "timestamp": datetime.now(UTC).isoformat(),
            "response_id": self.id,
        }

        updated = self.model_copy(
            update={
                "state": ResponseState.ERROR,
                "body": error_body,
                "error_message": error_message,
                "updated_at": FlextTimestamp.now(),
            },
        )
        logger.error(
            "Response marked as error",
            response_id=self.id,
            error=error_message,
        )
        return FlextResult[ApiResponse].ok(updated)

    def mark_timeout(self) -> FlextResult[ApiResponse]:
        """Mark response as timeout."""
        updated = self.model_copy(
            update={
                "state": ResponseState.TIMEOUT,
                "error_message": "Request timeout",
                "updated_at": FlextTimestamp.now(),
            },
        )
        return FlextResult[ApiResponse].ok(updated)


class ApiEndpoint(FlextEntity):
    """API endpoint entity with routing and configuration."""

    model_config = PydanticConfigDict(
        alias_generator=AliasGenerator(
            alias=flext_alias_generator,
            validation_alias=flext_alias_generator,
            serialization_alias=flext_alias_generator,
        ),
        extra="allow",
        validate_assignment=True,
        use_enum_values=True,
        str_strip_whitespace=True,
        arbitrary_types_allowed=True,
        validate_default=True,
        populate_by_name=True,
        frozen=False,  # Mutable entity
    )

    path: str = Field(description="Endpoint path pattern")
    methods: list[HttpMethod] = Field(description="Allowed HTTP methods")
    description: str | None = Field(None, description="Endpoint description")
    auth_required: bool = Field(default=True, description="Authentication requirement")
    rate_limit: int | None = Field(None, description="Rate limit per minute")
    timeout: float = Field(default=DEFAULT_TIMEOUT, description="Endpoint timeout")
    deprecated: bool = Field(default=False, description="Endpoint deprecated status")
    api_version: str = Field(default="v1", description="API version")

    # NOTE: Using FlextTimestamp from FlextEntity base class for lifecycle fields

    @override
    def validate_business_rules(self) -> FlextResult[None]:
        """Validate endpoint business rules."""
        # Consolidated validation checks
        checks = [
            (not self.path or not self.path.strip(), "Endpoint path cannot be empty"),
            (not self.path.startswith("/"), "Endpoint path must start with '/'"),
            (not self.methods, "Endpoint must support at least one HTTP method"),
            (
                self.rate_limit is not None and self.rate_limit <= 0,
                "Rate limit must be positive",
            ),
            (self.timeout <= 0, "Timeout must be positive"),
        ]

        # Check basic validations
        for condition, message in checks:
            if condition:
                return FlextResult[None].fail(message)

        # Check methods validity
        for method in self.methods:
            if method not in HttpMethod:
                return FlextResult[None].fail(f"Invalid HTTP method: {method}")

        return FlextResult[None].ok(None)

    def supports_method(self, method: HttpMethod) -> bool:
        """Check if endpoint supports HTTP method."""
        return method in self.methods

    def requires_authentication(self) -> bool:
        """Check if endpoint requires authentication."""
        return self.auth_required

    def is_deprecated(self) -> bool:
        """Check if endpoint is deprecated."""
        return self.deprecated


class ApiSession(FlextEntity):
    """API session entity with authentication state."""

    model_config = PydanticConfigDict(
        # Inherit modern Pydantic patterns from FlextEntity
        alias_generator=AliasGenerator(
            alias=flext_alias_generator,
            validation_alias=flext_alias_generator,
            serialization_alias=flext_alias_generator,
        ),
        # FlextEntity patterns: mutable with lifecycle management
        extra="allow",
        validate_assignment=True,
        use_enum_values=True,
        str_strip_whitespace=True,
        arbitrary_types_allowed=True,
        validate_default=True,
        populate_by_name=True,
        frozen=False,  # Mutable entity
        use_attribute_docstrings=True,
        json_schema_extra={
            "examples": [],
            "description": "API session entity with modern Pydantic patterns and authentication state",
            "title": "ApiSession",
        },
    )

    user_id: str | None = Field(None, description="Authenticated user ID")
    token: str | None = Field(None, description="Session token")
    token_type: TokenType = Field(default=TokenType.BEARER, description="Token type")
    expires_at: datetime | None = Field(None, description="Session expiration")
    last_activity: datetime | None = Field(None, description="Last activity timestamp")
    is_active: bool = Field(default=True, description="Session active state")
    refresh_token: str | None = Field(None, description="Refresh token")
    permissions: list[str] = Field(
        default_factory=list[str],
        description="Session permissions",
    )

    # NOTE: Using FlextTimestamp from FlextEntity base class for lifecycle fields

    @override
    def validate_business_rules(self) -> FlextResult[None]:
        """Validate session business rules."""
        if self.token and len(self.token) < MIN_TOKEN_LENGTH:
            return FlextResult[None].fail(
                f"Session token must be at least {MIN_TOKEN_LENGTH} characters",
            )

        if self.expires_at and self.expires_at <= datetime.now(UTC):
            return FlextResult[None].fail(
                "Session cannot be created with past expiration"
            )

        return FlextResult[None].ok(None)

    def is_expired(self) -> bool:
        """Check if session is expired."""
        if not self.expires_at:
            return False
        return datetime.now(UTC) >= self.expires_at

    def has_permission(self, permission: str) -> bool:
        """Check if session has specific permission."""
        return permission in self.permissions

    def extend_session(self, duration_minutes: int = 60) -> FlextResult[ApiSession]:
        """Extend session expiration."""
        if not self.is_active:
            return FlextResult[ApiSession].fail("Cannot extend inactive session")

        if self.is_expired():
            return FlextResult[ApiSession].fail("Cannot extend expired session")

        new_expiration = datetime.now(UTC) + timedelta(minutes=duration_minutes)

        updated = self.model_copy(
            update={
                "expires_at": new_expiration,
                "last_activity": datetime.now(UTC),
                "updated_at": FlextTimestamp.now(),
            },
        )
        return FlextResult[ApiSession].ok(updated)

    def deactivate(self) -> FlextResult[ApiSession]:
        """Deactivate session."""
        updated = self.model_copy(
            update={
                "is_active": False,
                "updated_at": FlextTimestamp.now(),
            },
        )
        return FlextResult[ApiSession].ok(updated)


# ==============================================================================
# DATA TRANSFER OBJECTS (Pure Pydantic Models)
# ==============================================================================


class RequestDto(FlextModel):
    """Request data transfer object using pure Pydantic patterns."""

    method: str = Field(description="HTTP method")
    url: str = Field(description="Request URL")
    headers: dict[str, str] | None = Field(None, description="HTTP headers")
    params: dict[str, object] | None = Field(None, description="Query parameters")
    json_data: dict[str, object] | None = Field(None, description="JSON payload")
    data: str | bytes | None = Field(None, description="Raw request data")
    timeout: float | None = Field(None, description="Request timeout")

    @override
    def validate_business_rules(self) -> FlextResult[None]:
        """Validate request DTO business rules."""
        if not self.method or not self.method.strip():
            return FlextResult[None].fail("HTTP method is required")

        if not self.url or not self.url.strip():
            return FlextResult[None].fail("Request URL is required")

        if self.timeout is not None and self.timeout <= 0:
            return FlextResult[None].fail("Timeout must be positive")

        return FlextResult[None].ok(None)


class ResponseDto(FlextModel):
    """Response data transfer object using pure Pydantic patterns."""

    status_code: int = Field(description="HTTP status code")
    headers: dict[str, str] | None = Field(None, description="Response headers")
    data: dict[str, object] | list[object] | str | bytes | None = Field(
        None,
        description="Response data",
    )
    elapsed_time: float = Field(default=0.0, description="Request duration")
    request_id: str | None = Field(None, description="Associated request ID")
    from_cache: bool = Field(default=False, description="Cache hit indicator")

    @override
    def validate_business_rules(self) -> FlextResult[None]:
        """Validate response DTO business rules."""
        if not (MIN_HTTP_STATUS <= self.status_code <= MAX_HTTP_STATUS):
            return FlextResult[None].fail(
                f"Invalid HTTP status code: {self.status_code}"
            )

        if self.elapsed_time < 0:
            return FlextResult[None].fail("Elapsed time cannot be negative")

        return FlextResult[None].ok(None)


class ApiErrorContext(FlextModel):
    """API error context using pure Pydantic patterns."""

    method: str | None = Field(None, description="HTTP method")
    endpoint: str | None = Field(None, description="API endpoint")
    status_code: int | None = Field(None, description="HTTP status code")
    error_code: str | None = Field(None, description="Application error code")
    details: dict[str, object] | None = Field(None, description="Error details")

    @override
    def validate_business_rules(self) -> FlextResult[None]:
        """Validate error context business rules."""
        if self.status_code is not None and not (
            MIN_HTTP_STATUS <= self.status_code <= MAX_HTTP_STATUS
        ):
            return FlextResult[None].fail(
                f"Invalid HTTP status code: {self.status_code}"
            )

        return FlextResult[None].ok(None)

    @override
    def to_dict(
        self,
        *,
        by_alias: bool = False,
        exclude_none: bool = False,
    ) -> dict[str, object]:
        """Convert to dictionary representation."""
        _ = by_alias, exclude_none  # Parameters maintained for compatibility
        result: dict[str, object] = {}

        if self.method is not None:
            result["method"] = self.method
        if self.endpoint is not None:
            result["endpoint"] = self.endpoint
        if self.status_code is not None:
            result["status_code"] = self.status_code
        if self.error_code is not None:
            result["error_code"] = self.error_code
        if self.details is not None:
            result["details"] = self.details

        return result


# ==============================================================================
# BUILDER MODELS (Pure Pydantic Models)
# ==============================================================================


class QueryBuilder(FlextModel):
    """Query builder configuration using pure Pydantic patterns."""

    filters: list[dict[str, object]] = Field(
        default_factory=list[dict[str, object]],
        description="Query filters",
    )
    sorts: list[dict[str, str]] = Field(
        default_factory=list[dict[str, str]],
        description="Sort criteria",
    )
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(
        default=DEFAULT_PAGE_SIZE,
        ge=1,
        le=1000,
        description="Items per page",
    )
    search: str | None = Field(None, description="Search term")
    fields: list[str] | None = Field(None, description="Fields to include")
    includes: list[str] | None = Field(None, description="Relations to include")
    excludes: list[str] | None = Field(None, description="Fields to exclude")

    @override
    def validate_business_rules(self) -> FlextResult[None]:
        """Validate query builder business rules."""
        if self.page < 1:
            return FlextResult[None].fail("Page number must be positive")

        if (
            self.page_size < 1
            or self.page_size > FlextApiConstants.Config.MAX_PAGE_SIZE
        ):
            return FlextResult[None].fail(
                f"Page size must be between 1 and {FlextApiConstants.Config.MAX_PAGE_SIZE}",
            )

        return FlextResult[None].ok(None)

    def to_query_config(self) -> QueryConfig:
        """Convert to QueryConfig value object."""
        return QueryConfig(
            filters=self.filters,
            sorts=self.sorts,
            page=self.page,
            page_size=self.page_size,
            search=self.search,
            fields=self.fields,
        )


class ResponseBuilder(FlextModel):
    """Response builder configuration using pure Pydantic patterns."""

    success: bool = Field(default=True, description="Success indicator")
    data: dict[str, object] | list[object] | str | None = Field(
        None,
        description="Response data",
    )
    message: str | None = Field(None, description="Response message")
    errors: list[str] | None = Field(None, description="Error messages")
    metadata: dict[str, object] | None = Field(None, description="Response metadata")
    pagination: PaginationInfo | None = Field(None, description="Pagination info")
    status_code: int = Field(
        default=200,
        ge=100,
        le=599,
        description="HTTP status code",
    )

    @override
    def validate_business_rules(self) -> FlextResult[None]:
        """Validate response builder business rules."""
        if not (MIN_HTTP_STATUS <= self.status_code <= MAX_HTTP_STATUS):
            return FlextResult[None].fail(
                f"Invalid HTTP status code: {self.status_code}"
            )

        if not self.success and not (self.errors or self.message):
            return FlextResult[None].fail(
                "Error responses must include error messages or details",
            )

        return FlextResult[None].ok(None)

    @override
    def to_dict(
        self,
        *,
        by_alias: bool = False,
        exclude_none: bool = False,
    ) -> dict[str, object]:
        """Convert to dictionary representation."""
        _ = by_alias, exclude_none  # Parameters maintained for compatibility
        result: dict[str, object] = {
            "success": self.success,
            "data": self.data,
        }

        if self.message:
            result["message"] = self.message
        if self.errors:
            result["errors"] = self.errors
        if self.metadata:
            result["metadata"] = self.metadata
        if self.pagination:
            result["pagination"] = self.pagination.model_dump()

        return result


# Value Objects
URL.model_rebuild()
HttpHeader.model_rebuild()
BearerToken.model_rebuild()
ClientConfig.model_rebuild()
QueryConfig.model_rebuild()
PaginationInfo.model_rebuild()

# Entities
ApiRequest.model_rebuild()
ApiResponse.model_rebuild()
ApiEndpoint.model_rebuild()
ApiSession.model_rebuild()

# DTOs (now using pure Pydantic)
RequestDto.model_rebuild()
ResponseDto.model_rebuild()
ApiErrorContext.model_rebuild()

# Builders (now using pure Pydantic)
QueryBuilder.model_rebuild()
ResponseBuilder.model_rebuild()


# ==============================================================================
# EXPORTS
# ==============================================================================

__all__ = [
    "DEFAULT_MAX_RETRIES",
    "DEFAULT_PAGE_SIZE",
    # Constants
    "DEFAULT_TIMEOUT",
    # Value Objects
    "URL",
    "ApiEndpoint",
    "ApiErrorContext",
    # Entities
    "ApiRequest",
    "ApiResponse",
    "ApiSession",
    "BearerToken",
    "ClientConfig",
    "ClientProtocol",
    "ClientStatus",
    "HttpHeader",
    # Enumerations
    "HttpMethod",
    "HttpStatus",
    "OperationType",
    "PaginationInfo",
    # Builders
    "QueryBuilder",
    "QueryConfig",
    # DTOs
    "RequestDto",
    "RequestState",
    "ResponseBuilder",
    "ResponseDto",
    "ResponseState",
    "TokenType",
]
