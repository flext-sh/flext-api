"""Advanced API test factories using Pydantic V2 Builder Pattern.

Provides zero-parameter factory builders eliminating ALL parameter complexity.
Follows flext-core patterns with advanced Pydantic V2 and Python 3.13 features.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextTypes, FlextUtilities
from pydantic import BaseModel, ConfigDict, Field

from flext_api import FlextApiModels
from flext_api.config import FlextApiConfig

# =============================================================================
# ADVANCED PYDANTIC V2 BUILDER PATTERN - ZERO PARAMETER COMPLEXITY
# =============================================================================


class Builder(BaseModel):
    """Advanced Pydantic V2 builder for - eliminates ALL parameters."""

    model_config = ConfigDict(
        validate_assignment=True,
        frozen=False,  # Mutable for builder pattern
        arbitrary_types_allowed=True,
    )

    method: str = Field(default="GET", description="HTTP method")
    url: str = Field(default="https://httpbin.org/get", description="Request ")
    headers: FlextTypes.Core.Headers = Field(
        default_factory=dict, description="HTTP headers"
    )
    params: FlextTypes.Core.Dict = Field(
        default_factory=dict, description="Query parameters"
    )
    timeout: float = Field(default=30.0, description="Request timeout")

    def build(self) -> FlextApiModels.ApiRequest:
        """Build using current configuration."""
        return FlextApiModels.ApiRequest(
            method=FlextApiModels.HttpMethod(self.method)
            if isinstance(self.method, str)
            else self.method,
            url=self.url,
            headers=self.headers,
            params=self.params,
            timeout=self.timeout,
        )

    # Fluent interface methods for chaining
    def with_method(self, method: str) -> Builder:
        self.method = method
        return self

    def with_url(self, url: str) -> Builder:
        self.url = url
        return self

    def with_headers(self, headers: FlextTypes.Core.Headers) -> Builder:
        self.headers = headers
        return self

    def with_params(self, params: FlextTypes.Core.Dict) -> Builder:
        self.params = params
        return self

    def with_timeout(self, timeout: float) -> Builder:
        self.timeout = timeout
        return self


def create_flext_api_client_request(
    method: str = "GET",
    url: str = "https://httpbin.org/get",
    headers: FlextTypes.Core.Headers | None = None,
    params: FlextTypes.Core.Dict | None = None,
    timeout: float = 30.0,
) -> FlextApiModels.ApiRequest:
    """Create FlextApiModels.for testing - BACKWARD COMPATIBILITY."""
    return (
        Builder()
        .with_method(method)
        .with_url(url)
        .with_headers(headers or {})
        .with_params(params or {})
        .with_timeout(timeout)
        .build()
    )


class ApiResponseBuilder(BaseModel):
    """Advanced Pydantic V2 builder for ApiResponse - eliminates ALL parameters."""

    model_config = ConfigDict(
        validate_assignment=True,
        frozen=False,  # Mutable for builder pattern
        arbitrary_types_allowed=True,
    )

    status_code: int = Field(default=200, description="HTTP status code")
    headers: FlextTypes.Core.Headers = Field(
        default_factory=lambda: {"content-type": "application/json"},
        description="HTTP headers",
    )
    data: FlextTypes.Core.Dict | FlextTypes.Core.List | str | bytes | None = Field(
        default_factory=lambda: {"message": "success"}, description="Response data"
    )
    elapsed_time: float = Field(default=0.5, description="Request elapsed time")
    request_id: str = Field(
        default_factory=FlextUtilities.Generators.generate_request_id,
        description="Request ID",
    )
    from_cache: bool = Field(default=False, description="Response from cache")

    def build(self) -> FlextApiModels.ApiResponse:
        """Build ApiResponse using current configuration."""
        return FlextApiModels.ApiResponse(
            status_code=self.status_code,
            headers=self.headers,
            data=self.data,
            elapsed_time=self.elapsed_time,
            request_id=self.request_id,
            from_cache=self.from_cache,
        )

    # Fluent interface methods
    def with_status_code(self, status_code: int) -> ApiResponseBuilder:
        self.status_code = status_code
        return self

    def with_headers(self, headers: FlextTypes.Core.Headers) -> ApiResponseBuilder:
        self.headers = headers
        return self

    def with_data(
        self, data: FlextTypes.Core.Dict | FlextTypes.Core.List | str | bytes | None
    ) -> ApiResponseBuilder:
        self.value = data
        return self

    def with_elapsed_time(self, elapsed_time: float) -> ApiResponseBuilder:
        self.elapsed_time = elapsed_time
        return self

    def with_request_id(self, request_id: str) -> ApiResponseBuilder:
        self.request_id = request_id
        return self

    def with_cache(self, from_cache: bool) -> ApiResponseBuilder:
        self.from_cache = from_cache
        return self


def create_flext_api_client_response(
    status_code: int = 200,
    headers: FlextTypes.Core.Headers | None = None,
    data: FlextTypes.Core.Dict | FlextTypes.Core.List | str | bytes | None = None,
    elapsed_time: float = 0.5,
    request_id: str | None = None,
    *,
    from_cache: bool = False,
) -> FlextApiModels.ApiResponse:
    """Create FlextApiModels.ApiResponse for testing - BACKWARD COMPATIBILITY."""
    builder = (
        ApiResponseBuilder()
        .with_status_code(status_code)
        .with_elapsed_time(elapsed_time)
        .with_cache(from_cache)
    )

    if headers is not None:
        builder = builder.with_headers(headers)
    if data is not None:
        builder = builder.with_data(data)
    if request_id is not None:
        builder = builder.with_request_id(request_id)

    return builder.build()


class ApiConfigBuilder(BaseModel):
    """Advanced Pydantic V2 builder for FlextApiConfig - eliminates ALL parameters."""

    model_config = ConfigDict(
        validate_assignment=True,
        frozen=False,  # Mutable for builder pattern
        arbitrary_types_allowed=True,
    )

    api_host: str = Field(default="localhost", description="API host")
    api_port: int = Field(default=8000, description="API port")
    default_timeout: int = Field(default=30, description="Default timeout")
    max_retries: int = Field(default=3, description="Maximum retries")
    enable_caching: bool = Field(default=True, description="Enable caching")
    cache_ttl: int = Field(default=300, description="Cache TTL")

    def build(self) -> FlextApiConfig:
        """Build FlextApiConfig using current configuration."""
        return FlextApiConfig.model_validate(
            {
                "api_host": self.api_host,
                "api_port": self.api_port,
                "default_timeout": self.default_timeout,
                "max_retries": self.max_retries,
                "enable_caching": self.enable_caching,
                "cache_ttl": self.cache_ttl,
            }
        )

    # Fluent interface methods
    def with_host(self, api_host: str) -> ApiConfigBuilder:
        self.api_host = api_host
        return self

    def with_port(self, api_port: int) -> ApiConfigBuilder:
        self.api_port = api_port
        return self

    def with_timeout(self, default_timeout: int) -> ApiConfigBuilder:
        self.default_timeout = default_timeout
        return self

    def with_retries(self, max_retries: int) -> ApiConfigBuilder:
        self.max_retries = max_retries
        return self

    def with_caching(
        self, enable_caching: bool, cache_ttl: int = 300
    ) -> ApiConfigBuilder:
        self.enable_caching = enable_caching
        self.cache_ttl = cache_ttl
        return self


def create_flext_api_config(
    api_host: str = "localhost",
    api_port: int = 8000,
    default_timeout: int = 30,
    max_retries: int = 3,
    *,
    enable_caching: bool = True,
    cache_ttl: int = 300,
) -> FlextApiConfig:
    """Create FlextApiConfig for testing - BACKWARD COMPATIBILITY."""
    return (
        ApiConfigBuilder()
        .with_host(api_host)
        .with_port(api_port)
        .with_timeout(default_timeout)
        .with_retries(max_retries)
        .with_caching(enable_caching, cache_ttl)
        .build()
    )


# =============================================================================
# MODERN BUILDER INTERFACE - ZERO PARAMETER COMPLEXITY
# =============================================================================

# Modern builder factories - PREFERRED usage
ApiRequest = Builder  # Use: ApiRequest().with_method("POST").build()
ApiResponse = ApiResponseBuilder  # Use: ApiResponse().with_status_code(201).build()
ApiConfig = ApiConfigBuilder  # Use: ApiConfig().with_host("api.example.com").build()

# Legacy function aliases for backward compatibility
FlextApiConfigFactory = create_flext_api_config
FlextFactory = create_flext_api_client_request
FlextApiResponseFactory = create_flext_api_client_response

# Export all modern builders
__all__ = [
    "ApiConfig",  # Alias for ApiConfigBuilder
    "ApiConfigBuilder",
    "ApiResponse",  # Alias for ApiResponseBuilder
    "ApiResponseBuilder",
    # Modern Builder Pattern (PREFERRED)
    "Builder",
    "FlextApiConfigFactory",
    "FlextApiResponseFactory",
    "FlextFactory",
    # Legacy compatibility functions
    "create_flext_api_client_request",
    "create_flext_api_client_response",
    "create_flext_api_config",
]
