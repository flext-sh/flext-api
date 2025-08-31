"""API-related test factories using simple factory functions.

Provides factory functions for API objects and configurations.
"""

from __future__ import annotations

# Use FlextUtilities.generate_uuid() instead of manual uuid import
from flext_core import FlextUtilities

from flext_api import FlextApiModels
from flext_api.config import FlextApiConfig


def create_flext_api_client_request(
    method: str = "GET",
    url: str = "https://httpbin.org/get",
    headers: dict[str, str] | None = None,
    params: dict[str, object] | None = None,
    timeout: float = 30.0,
) -> FlextApiModels.ApiRequest:
    """Create FlextApiModels.ApiRequest for testing."""
    return FlextApiModels.ApiRequest(
        method=FlextApiModels.HttpMethod(method) if isinstance(method, str) else method,
        url=url,
        headers=headers or {},
        params=params or {},
        timeout=timeout,
    )


def create_flext_api_client_response(
    status_code: int = 200,
    headers: dict[str, str] | None = None,
    data: dict[str, object] | list[object] | str | bytes | None = None,
    elapsed_time: float = 0.5,
    request_id: str | None = None,
    *,
    from_cache: bool = False,
) -> FlextApiModels.ApiResponse:
    """Create FlextApiModels.ApiResponse for testing."""
    return FlextApiModels.ApiResponse(
        status_code=status_code,
        headers=headers or {"content-type": "application/json"},
        data=data or {"message": "success"},
        elapsed_time=elapsed_time,
        request_id=request_id or FlextUtilities.generate_uuid(),
        from_cache=from_cache,
    )


def create_flext_api_config(
    api_host: str = "localhost",
    api_port: int = 8000,
    default_timeout: int = 30,
    max_retries: int = 3,
    *,
    enable_caching: bool = True,
    cache_ttl: int = 300,
) -> FlextApiConfig:
    """Create FlextApiConfig for testing."""
    # Use Pydantic model_validate to create instance with values
    return FlextApiConfig.model_validate({
        "api_host": api_host,
        "api_port": api_port,
        "default_timeout": default_timeout,
        "max_retries": max_retries,
        "enable_caching": enable_caching,
        "cache_ttl": cache_ttl,
    })


# Legacy aliases for factory patterns
FlextApiConfigFactory = create_flext_api_config
FlextApiRequestFactory = create_flext_api_client_request
FlextApiResponseFactory = create_flext_api_client_response
