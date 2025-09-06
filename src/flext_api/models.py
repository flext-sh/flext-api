"""FLEXT API Models - Unified model classes following flext-core patterns.

Real Pydantic models with proper validation and FlextResult integration.
Single unified class architecture following PEP8 conventions.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from enum import StrEnum
from typing import ClassVar

from flext_core import FlextModels, flext_logger
from pydantic import BaseModel, Field, field_validator

logger = flext_logger(__name__)


class FlextApiModels(FlextModels):
    """Unified models class for FLEXT API with all nested types."""

    class HttpMethod(StrEnum):
        """HTTP method enumeration."""

        GET = "GET"
        POST = "POST"
        PUT = "PUT"
        DELETE = "DELETE"
        PATCH = "PATCH"
        HEAD = "HEAD"
        OPTIONS = "OPTIONS"

    class HttpStatus(StrEnum):
        """HTTP status enumeration."""

        SUCCESS = "success"
        ERROR = "error"
        PENDING = "pending"
        TIMEOUT = "timeout"

    class ClientConfig(BaseModel):
        """HTTP client configuration model."""

        base_url: str = Field(default="", description="Base URL for HTTP requests")
        timeout: float = Field(default=30.0, description="Request timeout in seconds")
        max_retries: int = Field(default=3, description="Maximum retry attempts")
        headers: dict[str, str] = Field(
            default_factory=dict, description="Default headers"
        )

        @field_validator("base_url")
        @classmethod
        def validate_base_url(cls, v: str) -> str:
            """Validate base URL format."""
            if v and not (v.startswith(("http://", "https://"))):
                msg = "Base must include scheme and host if provided"
                raise ValueError(msg)
            return v

        @field_validator("timeout")
        @classmethod
        def validate_timeout(cls, v: float) -> float:
            """Validate timeout is positive."""
            if v <= 0:
                msg = "Timeout must be greater than 0"
                raise ValueError(msg)
            return v

        @field_validator("max_retries")
        @classmethod
        def validate_max_retries(cls, v: int) -> int:
            """Validate max_retries is non-negative."""
            if v < 0:
                msg = "Max retries must be greater than or equal to 0"
                raise ValueError(msg)
            return v

    class ApiRequest(BaseModel):
        """API request model."""

        id: str = Field(..., description="Request identifier")
        method: FlextApiModels.HttpMethod = Field(..., description="HTTP method")
        url: str = Field(..., description="Request URL")
        headers: dict[str, str] | None = Field(
            default=None, description="Request headers"
        )
        body: dict[str, object] | str | bytes | None = Field(
            default=None, description="Request body"
        )

        @field_validator("url")
        @classmethod
        def validate_url(cls, v: str) -> str:
            """Validate URL is not empty."""
            if not v:
                msg = "URL cannot be empty"
                raise ValueError(msg)
            return v

    class HttpResponse(BaseModel):
        """HTTP response model."""

        status_code: int = Field(..., description="HTTP status code")
        body: dict[str, object] | str | bytes | None = Field(
            default=None, description="Response body"
        )
        headers: dict[str, str] | None = Field(
            default=None, description="Response headers"
        )
        url: str = Field(..., description="Request URL")
        method: str = Field(..., description="HTTP method")

        @field_validator("status_code")
        @classmethod
        def validate_status_code(cls, v: int) -> int:
            """Validate HTTP status code range."""
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
            """Check if response indicates client error (4xx)."""
            client_error_min = 400
            client_error_max = 500
            return client_error_min <= self.status_code < client_error_max

        @property
        def is_server_error(self) -> bool:
            """Check if response indicates server error (5xx)."""
            server_error_min = 500
            server_error_max = 600
            return server_error_min <= self.status_code < server_error_max

    class HttpQuery(BaseModel):
        """HTTP query builder model."""

        filter_conditions: dict[str, object] = Field(
            default_factory=dict, description="Filter conditions"
        )
        sort_fields: list[str] = Field(default_factory=list, description="Sort fields")
        page_number: int = Field(default=1, description="Page number")
        page_size_value: int = Field(default=20, description="Page size")

        @field_validator("page_number")
        @classmethod
        def validate_page_number(cls, v: int) -> int:
            """Validate page number is positive."""
            if v < 1:
                msg = "Page number must be greater than or equal to 1"
                raise ValueError(msg)
            return v

        @field_validator("page_size_value")
        @classmethod
        def validate_page_size(cls, v: int) -> int:
            """Validate page size is within bounds."""
            min_size = 1
            max_size = 1000
            if v < min_size or v > max_size:
                msg = f"Page size must be between {min_size} and {max_size}"
                raise ValueError(msg)
            return v

    class Builder(BaseModel):
        """Response builder model."""

        def create(self, **kwargs: object) -> dict[str, object]:
            """Create method for building responses."""
            return dict(kwargs)

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
        options: dict[str, object] = Field(
            default_factory=dict, description="Additional options"
        )

    class ApiBaseService:
        """Base service class for API services."""

        def __init__(self, service_name: str = "default-service") -> None:
            """Initialize base service."""
            self._service_name = service_name

    class ApiResponse(BaseModel):
        """API response model."""

        status_code: int = Field(..., description="HTTP status code")
        data: dict[str, object] | None = Field(
            default=None, description="Response data"
        )
        message: str | None = Field(default=None, description="Response message")
        headers: dict[str, str] = Field(
            default_factory=dict, description="Response headers"
        )
        success: bool = Field(..., description="Success flag")

        @field_validator("status_code")
        @classmethod
        def validate_status_code(cls, v: int) -> int:
            """Validate HTTP status code range."""
            min_code = 100
            max_code = 599
            if not min_code <= v <= max_code:
                msg = f"Status code must be between {min_code}-{max_code}"
                raise ValueError(msg)
            return v

    @classmethod
    def for_query(cls) -> FlextApiModels.HttpQuery:
        """Factory method for creating query builders."""
        return cls.HttpQuery()


# Create proxy classes for constants to integrate with unified architecture
class FlextApiConstants:
    """Unified constants for FLEXT API following single class architecture."""

    class Client:
        """HTTP client constants."""

        DEFAULT_USER_AGENT = "FlextAPI/0.9.0"
        DEFAULT_TIMEOUT = 30
        MAX_RETRIES = 3
        RETRY_BACKOFF_FACTOR = 0.5

    class Network:
        """Network constants."""

        MAX_PORT = 65535
        MIN_PORT = 1

    class HttpStatusRanges:
        """HTTP status code ranges."""

        SUCCESS_MIN = 200
        SUCCESS_MAX = 299
        CLIENT_ERROR_MIN = 400
        CLIENT_ERROR_MAX = 499
        SERVER_ERROR_MIN = 500
        SERVER_ERROR_MAX = 599

    # Error code lists
    CLIENT_ERROR_CODES: ClassVar[list[int]] = [400, 401, 403, 404, 409, 422, 429]
    SERVER_ERROR_CODES: ClassVar[list[int]] = [500, 502, 503, 504]

    # Rate limiting
    RATE_LIMIT_REQUESTS: ClassVar[int] = 1000
    RATE_LIMIT_WINDOW: ClassVar[int] = 3600

    # Response templates
    SUCCESS_RESPONSE: ClassVar[dict[str, object]] = {
        "status": "success",
        "data": None,
        "error": None,
    }
    ERROR_RESPONSE: ClassVar[dict[str, object]] = {
        "status": "error",
        "data": None,
        "error": None,
    }


class FlextApiEndpoints:
    """API endpoints constants."""

    # Base paths
    API_V1 = "/api/v1"
    HEALTH = "/health"
    METRICS = "/metrics"
    DOCS = "/docs"
    STATUS = "/status"

    # Authentication endpoints
    AUTH_LOGIN = "/api/v1/auth/login"
    AUTH_LOGOUT = "/api/v1/auth/logout"
    AUTH_REFRESH = "/api/v1/auth/refresh"
    AUTH_VERIFY = "/api/v1/auth/verify"

    # Pipeline endpoints
    PIPELINES = "/api/v1/pipelines"
    PIPELINE_RUN = "/api/v1/pipelines/{pipeline_id}/run"
    PIPELINE_STATUS = "/api/v1/pipelines/{pipeline_id}/status"
    PIPELINE_LOGS = "/api/v1/pipelines/{pipeline_id}/logs"

    # Plugin endpoints
    PLUGINS = "/api/v1/plugins"
    PLUGIN_STATUS = "/api/v1/plugins/{plugin_id}/status"
    PLUGIN_CONFIG = "/api/v1/plugins/{plugin_id}/config"
    PLUGIN_INSTALL = "/api/v1/plugins/install"
    PLUGIN_UNINSTALL = "/api/v1/plugins/{plugin_id}/uninstall"


class FlextApiFieldType:
    """Field type constants."""

    # Basic field types
    STRING = "string"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"

    # API-specific field types
    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"
    PIPELINE_CONFIG = "pipeline_config"
    PLUGIN_CONFIG = "plugin_config"
    USER_ROLE = "user_role"
    ENDPOINT_PATH = "endpoint_path"
    HTTP_METHOD = "http_method"
    RESPONSE_FORMAT = "response_format"
    REQUEST_ID = "request_id"


class StorageBackend:
    """Storage backend types for FlextApiStorage."""

    MEMORY = "memory"
    FILE = "file"
    REDIS = "redis"
    DATABASE = "database"


# Removed duplicate - use FlextApiModels.StorageConfig instead


class URL(BaseModel):
    """URL value object for FlextAPI."""

    url: str = Field(..., description="URL string", min_length=1)

    def __str__(self) -> str:
        """Return URL as string."""
        return self.url


class FlextApiStatus:
    """API status constants."""

    # Request status
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

    # Service status
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    MAINTENANCE = "maintenance"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"

    # Pipeline status
    PIPELINE_IDLE = "idle"
    PIPELINE_RUNNING = "running"
    PIPELINE_SUCCESS = "success"
    PIPELINE_ERROR = "error"
    PIPELINE_TIMEOUT = "timeout"

    # Plugin status
    PLUGIN_LOADED = "loaded"
    PLUGIN_ACTIVE = "active"
    PLUGIN_INACTIVE = "inactive"
    PLUGIN_ERROR = "error"


# Backward compatibility constants
MAX_PORT = FlextApiConstants.Network.MAX_PORT
MIN_PORT = FlextApiConstants.Network.MIN_PORT

# Backward compatibility aliases for models
ApiRequest = FlextApiModels.ApiRequest
HttpResponse = FlextApiModels.HttpResponse
ClientConfig = FlextApiModels.ClientConfig
StorageConfig = FlextApiModels.StorageConfig

__all__ = [
    "MAX_PORT",
    "MIN_PORT",
    "URL",
    "ApiRequest",
    "ClientConfig",
    "FlextApiConstants",
    "FlextApiEndpoints",
    "FlextApiFieldType",
    "FlextApiModels",
    "FlextApiStatus",
    "HttpResponse",
    "StorageBackend",
    "StorageConfig",
]
