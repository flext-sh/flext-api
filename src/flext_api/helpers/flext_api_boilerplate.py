#!/usr/bin/env python3
"""FlextApi Boilerplate Reducers - Massive simplification for common patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Helpers, mixins, typedefs, and decorators that eliminate repetitive code.
Following SOLID, DRY, KISS principles with flext-core hierarchy.
"""

from __future__ import annotations

import asyncio
import functools
from collections.abc import Callable
from datetime import datetime
from typing import Any, TypedDict, TypeVar, Union

from flext_core import FlextResult, get_logger

logger = get_logger(__name__)

# ==============================================================================
# TYPEDDICTS - STANDARDIZED API STRUCTURES
# ==============================================================================

class FlextApiResponse(TypedDict):
    """Standard API response structure - eliminates manual dict creation."""

    success: bool
    data: Any
    status: int
    message: str
    timestamp: str


class FlextApiRequest(TypedDict):
    """Standard API request structure - eliminates manual validation."""

    endpoint: str
    method: str
    data: dict[str, Any]
    headers: dict[str, str]
    timeout: int


class FlextApiConfig(TypedDict):
    """Standard API configuration - eliminates config boilerplate."""

    base_url: str
    auth_token: str
    api_key: str
    timeout: int
    retries: int
    cache_enabled: bool
    cache_ttl: int


class FlextApiServiceCall(TypedDict):
    """Standard service call structure - eliminates microservice boilerplate."""

    service: str
    endpoint: str
    method: str
    data: dict[str, Any]
    key: str


class FlextApiHealthCheck(TypedDict):
    """Standard health check response - eliminates monitoring boilerplate."""

    service: str
    status: str
    response_time_ms: float
    cached: bool
    timestamp: str


class FlextApiMetrics(TypedDict):
    """Standard metrics structure - eliminates metrics boilerplate."""

    total_requests: int
    successful_requests: int
    failed_requests: int
    success_rate: float
    avg_response_time_ms: float
    cache_hit_rate: float


# ==============================================================================
# TYPE UNIONS - SIMPLIFIED TYPE HINTS
# ==============================================================================

FlextApiData = Union[dict[str, Any], list[Any], str, int, float, bool, None]
FlextApiHeaders = dict[str, str]
FlextApiParams = dict[str, Any]
FlextApiCallback = Callable[[FlextApiResponse], None]
FlextApiMiddleware = Callable[[FlextApiRequest], FlextApiRequest]
FlextApiValidator = Callable[[Any], bool]

T = TypeVar("T")
ResponseType = TypeVar("ResponseType", bound=dict[str, Any])

# ==============================================================================
# RESPONSE BUILDERS - ELIMINATE MANUAL DICT CONSTRUCTION
# ==============================================================================

def flext_api_success_dict(
    data: Any,
    message: str = "Success",
    status: int = 200
) -> FlextApiResponse:
    """Create success response dict - eliminates manual dict creation."""
    return FlextApiResponse(
        success=True,
        data=data,
        status=status,
        message=message,
        timestamp=datetime.now().isoformat()
    )


def flext_api_error_dict(
    message: str,
    status: int = 400,
    data: Any = None
) -> FlextApiResponse:
    """Create error response dict - eliminates manual error handling."""
    return FlextApiResponse(
        success=False,
        data=data,
        status=status,
        message=message,
        timestamp=datetime.now().isoformat()
    )


def flext_api_request_dict(
    endpoint: str,
    method: str = "GET",
    data: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    timeout: int = 30
) -> FlextApiRequest:
    """Create request dict - eliminates manual request construction."""
    return FlextApiRequest(
        endpoint=endpoint,
        method=method.upper(),
        data=data or {},
        headers=headers or {},
        timeout=timeout
    )


def flext_api_config_dict(
    base_url: str,
    auth_token: str = "",
    api_key: str = "",
    timeout: int = 30,
    retries: int = 3,
    cache_enabled: bool = True,
    cache_ttl: int = 300
) -> FlextApiConfig:
    """Create config dict - eliminates configuration boilerplate."""
    return FlextApiConfig(
        base_url=base_url,
        auth_token=auth_token,
        api_key=api_key,
        timeout=timeout,
        retries=retries,
        cache_enabled=cache_enabled,
        cache_ttl=cache_ttl
    )


# ==============================================================================
# DECORATORS - ELIMINATE COMMON PATTERNS
# ==============================================================================

def flext_api_with_retry(retries: int = 3, delay: float = 1.0):
    """Decorator to add retry logic - eliminates retry boilerplate."""
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None

            for attempt in range(retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < retries:
                        logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay}s: {e}")
                        await asyncio.sleep(delay)
                    else:
                        logger.exception(f"All {retries + 1} attempts failed")

            raise last_exception if last_exception else Exception("Retry failed")

        return wrapper
    return decorator


def flext_api_with_logging(log_args: bool = True, log_result: bool = True):
    """Decorator to add logging - eliminates logging boilerplate."""
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            if log_args:
                logger.info(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")

            start_time = datetime.now()
            try:
                result = await func(*args, **kwargs)
                duration = (datetime.now() - start_time).total_seconds() * 1000

                if log_result:
                    logger.info(f"{func.__name__} completed in {duration:.2f}ms")

                return result
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds() * 1000
                logger.exception(f"{func.__name__} failed after {duration:.2f}ms: {e}")
                raise

        return wrapper
    return decorator


def flext_api_with_cache(ttl: int = 300):
    """Decorator to add caching - eliminates cache boilerplate."""
    cache: dict[str, tuple[Any, datetime]] = {}

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"

            # Check cache
            if cache_key in cache:
                value, timestamp = cache[cache_key]
                if (datetime.now() - timestamp).total_seconds() < ttl:
                    logger.debug(f"Cache hit for {func.__name__}")
                    return value
                del cache[cache_key]

            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache[cache_key] = (result, datetime.now())
            logger.debug(f"Cached result for {func.__name__}")

            return result

        return wrapper
    return decorator


def flext_api_with_validation(validator: FlextApiValidator):
    """Decorator to add validation - eliminates validation boilerplate."""
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Validate first argument (usually the data)
            if args and not validator(args[0]):
                raise ValueError(f"Validation failed for {func.__name__}")

            return await func(*args, **kwargs)

        return wrapper
    return decorator


def flext_api_with_timeout(seconds: int = 30):
    """Decorator to add timeout - eliminates timeout boilerplate."""
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=seconds)
            except TimeoutError:
                logger.exception(f"{func.__name__} timed out after {seconds}s")
                raise

        return wrapper
    return decorator


# ==============================================================================
# MIXINS - REUSABLE FUNCTIONALITY
# ==============================================================================

class FlextApiCacheMixin:
    """Mixin for caching functionality - eliminates cache implementation."""

    def __init__(self) -> None:
        self._cache: dict[str, tuple[Any, datetime]] = {}
        self._cache_ttl = 300

    def cache_get(self, key: str) -> Any | None:
        """Get cached value if not expired."""
        if key in self._cache:
            value, timestamp = self._cache[key]
            if (datetime.now() - timestamp).total_seconds() < self._cache_ttl:
                return value
            del self._cache[key]
        return None

    def cache_set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set cached value with optional TTL."""
        self._cache[key] = (value, datetime.now())
        if ttl:
            self._cache_ttl = ttl

    def cache_clear(self) -> None:
        """Clear all cached values."""
        self._cache.clear()

    def cache_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        return {
            "total_entries": len(self._cache),
            "cache_size_bytes": sum(len(str(v)) for v, _ in self._cache.values()),
            "oldest_entry": min(t for _, t in self._cache.values()) if self._cache else None
        }


class FlextApiMetricsMixin:
    """Mixin for metrics functionality - eliminates metrics implementation."""

    def __init__(self) -> None:
        self._metrics = FlextApiMetrics(
            total_requests=0,
            successful_requests=0,
            failed_requests=0,
            success_rate=0.0,
            avg_response_time_ms=0.0,
            cache_hit_rate=0.0
        )
        self._response_times: list[float] = []
        self._cache_hits = 0

    def metrics_record_request(self, success: bool, response_time_ms: float, cached: bool = False) -> None:
        """Record request metrics."""
        self._metrics["total_requests"] += 1

        if success:
            self._metrics["successful_requests"] += 1
        else:
            self._metrics["failed_requests"] += 1

        self._response_times.append(response_time_ms)

        if cached:
            self._cache_hits += 1

        # Update calculated metrics
        total = self._metrics["total_requests"]
        self._metrics["success_rate"] = (self._metrics["successful_requests"] / total) * 100
        self._metrics["avg_response_time_ms"] = sum(self._response_times) / len(self._response_times)
        self._metrics["cache_hit_rate"] = (self._cache_hits / total) * 100

    def metrics_get(self) -> FlextApiMetrics:
        """Get current metrics."""
        return self._metrics

    def metrics_reset(self) -> None:
        """Reset all metrics."""
        self._metrics = FlextApiMetrics(
            total_requests=0,
            successful_requests=0,
            failed_requests=0,
            success_rate=0.0,
            avg_response_time_ms=0.0,
            cache_hit_rate=0.0
        )
        self._response_times.clear()
        self._cache_hits = 0


class FlextApiAuthMixin:
    """Mixin for authentication functionality - eliminates auth boilerplate."""

    def __init__(self) -> None:
        self._auth_token: str = ""
        self._api_key: str = ""
        self._auth_headers: dict[str, str] = {}

    def auth_set_token(self, token: str) -> None:
        """Set bearer token authentication."""
        self._auth_token = token
        self._auth_headers["Authorization"] = f"Bearer {token}"

    def auth_set_api_key(self, api_key: str, header_name: str = "X-API-Key") -> None:
        """Set API key authentication."""
        self._api_key = api_key
        self._auth_headers[header_name] = api_key

    def auth_get_headers(self) -> dict[str, str]:
        """Get authentication headers."""
        return self._auth_headers.copy()

    def auth_clear(self) -> None:
        """Clear all authentication."""
        self._auth_token = ""
        self._api_key = ""
        self._auth_headers.clear()


class FlextApiValidationMixin:
    """Mixin for validation functionality - eliminates validation boilerplate."""

    def __init__(self) -> None:
        self._validators: dict[str, FlextApiValidator] = {}

    def validation_add_rule(self, name: str, validator: FlextApiValidator) -> None:
        """Add validation rule."""
        self._validators[name] = validator

    def validation_check(self, name: str, data: Any) -> bool:
        """Check data against validation rule."""
        if name not in self._validators:
            return True
        return self._validators[name](data)

    def validation_check_all(self, data: Any) -> bool:
        """Check data against all validation rules."""
        return all(validator(data) for validator in self._validators.values())

    def validation_get_rules(self) -> list[str]:
        """Get list of validation rule names."""
        return list(self._validators.keys())


# ==============================================================================
# DICT HELPERS - ELIMINATE DATA TRANSFORMATION BOILERPLATE
# ==============================================================================

def flext_api_merge_dicts(*dicts: dict[str, Any]) -> dict[str, Any]:
    """Merge multiple dictionaries - eliminates manual merging."""
    result: dict[str, Any] = {}
    for d in dicts:
        result.update(d)
    return result


def flext_api_filter_dict(data: dict[str, Any], keys: list[str]) -> dict[str, Any]:
    """Filter dictionary by keys - eliminates manual filtering."""
    return {k: v for k, v in data.items() if k in keys}


def flext_api_rename_keys(data: dict[str, Any], mapping: dict[str, str]) -> dict[str, Any]:
    """Rename dictionary keys - eliminates manual renaming."""
    return {mapping.get(k, k): v for k, v in data.items()}


def flext_api_flatten_dict(data: dict[str, Any], separator: str = ".") -> dict[str, Any]:
    """Flatten nested dictionary - eliminates manual flattening."""
    result: dict[str, Any] = {}

    def _flatten(obj: Any, prefix: str = "") -> None:
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_key = f"{prefix}{separator}{key}" if prefix else key
                if isinstance(value, dict):
                    _flatten(value, new_key)
                else:
                    result[new_key] = value
        else:
            result[prefix] = obj

    _flatten(data)
    return result


def flext_api_pick_values(data: dict[str, Any], *keys: str) -> list[Any]:
    """Pick values from dictionary - eliminates manual extraction."""
    return [data.get(key) for key in keys]


def flext_api_transform_values(data: dict[str, Any], transformer: Callable[[Any], Any]) -> dict[str, Any]:
    """Transform dictionary values - eliminates manual transformation."""
    return {k: transformer(v) for k, v in data.items()}


def flext_api_group_by_key(data: list[dict[str, Any]], key: str) -> dict[str, list[dict[str, Any]]]:
    """Group list of dicts by key - eliminates manual grouping."""
    result: dict[str, list[dict[str, Any]]] = {}
    for item in data:
        group_key = str(item.get(key, "unknown"))
        if group_key not in result:
            result[group_key] = []
        result[group_key].append(item)
    return result


# ==============================================================================
# COMPOSITE HELPERS - ELIMINATE COMPLEX PATTERNS
# ==============================================================================

class FlextApiClientBuilder:
    """Builder for creating API clients with specific capabilities."""

    def __init__(self) -> None:
        self._base_url = ""
        self._auth_token = ""
        self._api_key = ""
        self._cache_enabled = False
        self._cache_ttl = 300
        self._metrics_enabled = False
        self._validation_enabled = False
        self._mixins: list[type] = []

    def with_base_url(self, url: str) -> FlextApiClientBuilder:
        """Set base URL for the client."""
        self._base_url = url.rstrip("/")
        return self

    def with_auth_token(self, token: str) -> FlextApiClientBuilder:
        """Enable token authentication."""
        self._auth_token = token
        self._mixins.append(FlextApiAuthMixin)
        return self

    def with_api_key(self, key: str) -> FlextApiClientBuilder:
        """Enable API key authentication."""
        self._api_key = key
        self._mixins.append(FlextApiAuthMixin)
        return self

    def with_caching(self, ttl: int = 300) -> FlextApiClientBuilder:
        """Enable caching with TTL."""
        self._cache_enabled = True
        self._cache_ttl = ttl
        self._mixins.append(FlextApiCacheMixin)
        return self

    def with_metrics(self) -> FlextApiClientBuilder:
        """Enable metrics tracking."""
        self._metrics_enabled = True
        self._mixins.append(FlextApiMetricsMixin)
        return self

    def with_validation(self) -> FlextApiClientBuilder:
        """Enable request/response validation."""
        self._validation_enabled = True
        self._mixins.append(FlextApiValidationMixin)
        return self

    def build(self) -> FlextApiApplicationClient:
        """Build the configured client."""
        # Deduplicate mixins
        unique_mixins = list(dict.fromkeys(self._mixins))

        # Create dynamic class with selected mixins
        if unique_mixins:
            client_class = type(
                "DynamicFlextApiClient",
                (*tuple(unique_mixins), FlextApiApplicationClient),
                {}
            )
        else:
            client_class = FlextApiApplicationClient

        client = client_class(self._base_url)

        # Configure client
        if self._auth_token and hasattr(client, "auth_set_token"):
            client.auth_set_token(self._auth_token)
        if self._api_key and hasattr(client, "auth_set_api_key"):
            client.auth_set_api_key(self._api_key)

        return client


class FlextApiApplicationClient:
    """Core application client without mixins - pure functionality."""

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    async def get(self, endpoint: str, **kwargs: Any) -> FlextApiResponse:
        """GET request using flext-core patterns."""
        return await self._execute_request("GET", endpoint, **kwargs)

    async def post(self, endpoint: str, data: dict[str, Any] | None = None, **kwargs: Any) -> FlextApiResponse:
        """POST request using flext-core patterns."""
        kwargs["data"] = data or {}
        return await self._execute_request("POST", endpoint, **kwargs)

    async def put(self, endpoint: str, data: dict[str, Any] | None = None, **kwargs: Any) -> FlextApiResponse:
        """PUT request using flext-core patterns."""
        kwargs["data"] = data or {}
        return await self._execute_request("PUT", endpoint, **kwargs)

    async def delete(self, endpoint: str, **kwargs: Any) -> FlextApiResponse:
        """DELETE request using flext-core patterns."""
        return await self._execute_request("DELETE", endpoint, **kwargs)

    async def _execute_request(self, method: str, endpoint: str, **kwargs: Any) -> FlextApiResponse:
        """Execute HTTP request with FlextResult pattern."""
        from flext_api.helpers.flext_api_quick import (
            flext_api_quick_get,
            flext_api_quick_post,
        )

        url = f"{self.base_url}{endpoint}"

        # Merge headers if auth mixin is available
        headers = kwargs.get("headers", {})
        if hasattr(self, "auth_get_headers"):
            headers = flext_api_merge_dicts(headers, self.auth_get_headers())
            kwargs["headers"] = headers

        # Check cache if cache mixin is available
        if hasattr(self, "cache_get"):
            cache_key = f"{method}:{url}:{hash(str(kwargs))}"
            cached = self.cache_get(cache_key)
            if cached:
                if hasattr(self, "metrics_record_request"):
                    self.metrics_record_request(True, 0, cached=True)
                return cached

        start_time = datetime.now()

        try:
            # Execute request based on method
            if method.upper() == "GET":
                result = await flext_api_quick_get(url, **kwargs)
            elif method.upper() == "POST":
                result = await flext_api_quick_post(url, kwargs.get("data", {}), **{k: v for k, v in kwargs.items() if k != "data"})
            else:
                return flext_api_error_dict(f"Method {method} not supported", 405)

            duration = (datetime.now() - start_time).total_seconds() * 1000

            # Convert to standard response format
            if result["success"]:
                response = flext_api_success_dict(result["data"], status=result["status"])

                # Cache successful responses if cache mixin available
                if hasattr(self, "cache_set"):
                    cache_key = f"{method}:{url}:{hash(str(kwargs))}"
                    self.cache_set(cache_key, response)
            else:
                response = flext_api_error_dict("Request failed", result.get("status", 400))

            # Record metrics if metrics mixin available
            if hasattr(self, "metrics_record_request"):
                self.metrics_record_request(result["success"], duration)

            return response

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000

            # Record failed metrics if available
            if hasattr(self, "metrics_record_request"):
                self.metrics_record_request(False, duration)

            logger.exception(f"Request failed: {method} {url}")
            return flext_api_error_dict(str(e), 500)


# ==============================================================================
# FACTORY FUNCTIONS - ELIMINATE SETUP BOILERPLATE
# ==============================================================================

def flext_api_create_application_client(base_url: str) -> FlextApiApplicationClient:
    """Create basic application client without mixins."""
    return FlextApiApplicationClient(base_url)


def flext_api_create_client_builder() -> FlextApiClientBuilder:
    """Create client builder for configuring capabilities."""
    return FlextApiClientBuilder()


def flext_api_create_full_client(
    base_url: str,
    auth_token: str = "",
    api_key: str = "",
    enable_cache: bool = True,
    enable_metrics: bool = True,
    enable_validation: bool = False
) -> FlextApiApplicationClient:
    """Create fully configured client - eliminates builder boilerplate."""
    builder = FlextApiClientBuilder().with_base_url(base_url)

    if auth_token:
        builder = builder.with_auth_token(auth_token)
    elif api_key:
        builder = builder.with_api_key(api_key)

    if enable_cache:
        builder = builder.with_caching()

    if enable_metrics:
        builder = builder.with_metrics()

    if enable_validation:
        builder = builder.with_validation()

    return builder.build()


def flext_api_create_microservice_client(base_url: str, service_name: str, auth_token: str = "") -> FlextApiApplicationClient:
    """Create client optimized for microservice communication."""
    builder = (FlextApiClientBuilder()
               .with_base_url(base_url)
               .with_caching(ttl=60)  # Short cache for microservices
               .with_metrics())

    if auth_token:
        builder = builder.with_auth_token(auth_token)

    client = builder.build()

    # Add service-specific validation if validation mixin is enabled
    if hasattr(client, "validation_add_rule"):
        client.validation_add_rule("service_response", lambda x: isinstance(x, dict))

    return client


def flext_api_create_service_calls(services: dict[str, str], endpoints: list[str]) -> list[FlextApiServiceCall]:
    """Create service call list - eliminates manual list creation."""
    calls: list[FlextApiServiceCall] = []
    for service in services:
        for endpoint in endpoints:
            calls.append(FlextApiServiceCall(
                service=service,
                endpoint=endpoint,
                method="GET",
                data={},
                key=f"{service}_{endpoint.replace('/', '_')}"
            ))
    return calls


# ==============================================================================
# APPLICATION PATTERNS - REAL-WORLD USE CASES
# ==============================================================================

class FlextApiApplicationMixin:
    """Mixin for common application patterns - eliminates repetitive app code."""

    def __init__(self) -> None:
        self._request_context: dict[str, Any] = {}
        self._default_headers: dict[str, str] = {
            "User-Agent": "FlextApi/1.0",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def app_set_context(self, key: str, value: Any) -> None:
        """Set application context for requests."""
        self._request_context[key] = value

    def app_get_context(self, key: str) -> Any:
        """Get application context value."""
        return self._request_context.get(key)

    def app_set_default_header(self, name: str, value: str) -> None:
        """Set default header for all requests."""
        self._default_headers[name] = value

    def app_get_default_headers(self) -> dict[str, str]:
        """Get default headers for requests."""
        return self._default_headers.copy()

    def app_create_request_headers(self, additional: dict[str, str] | None = None) -> dict[str, str]:
        """Create headers combining defaults with additional."""
        headers = self._default_headers.copy()
        if additional:
            headers.update(additional)

        # Add context headers
        if "correlation_id" in self._request_context:
            headers["X-Correlation-ID"] = str(self._request_context["correlation_id"])
        if "user_id" in self._request_context:
            headers["X-User-ID"] = str(self._request_context["user_id"])

        return headers


class FlextApiDataProcessingMixin:
    """Mixin for data processing patterns - eliminates data handling boilerplate."""

    def data_extract_field(self, data: dict[str, Any], field_path: str, default: Any = None) -> Any:
        """Extract nested field from data using dot notation."""
        keys = field_path.split(".")
        current = data

        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return default

    def data_transform_response(self, response: FlextApiResponse, transformer: Callable[[Any], Any]) -> FlextApiResponse:
        """Transform response data using provided function."""
        if response["success"] and response["data"]:
            try:
                transformed_data = transformer(response["data"])
                return flext_api_success_dict(transformed_data, response["message"], response["status"])
            except Exception as e:
                logger.exception("Data transformation failed")
                return flext_api_error_dict(f"Transformation failed: {e}", 500)
        return response

    def data_paginate_request(self, endpoint: str, page_size: int = 50, max_pages: int = 10) -> list[dict[str, Any]]:
        """Create paginated request configurations."""
        requests = []
        for page in range(1, max_pages + 1):
            requests.append({
                "endpoint": f"{endpoint}?page={page}&size={page_size}",
                "method": "GET",
                "key": f"page_{page}"
            })
        return requests


# ==============================================================================
# ENHANCED COMPOSITE CLIENT
# ==============================================================================

class FlextApiEnhancedClient(FlextApiApplicationMixin, FlextApiDataProcessingMixin, FlextApiApplicationClient):
    """Enhanced client with application and data processing mixins."""

    def __init__(self, base_url: str) -> None:
        FlextApiApplicationClient.__init__(self, base_url)
        FlextApiApplicationMixin.__init__(self)
        FlextApiDataProcessingMixin.__init__(self)

    async def app_request(self, endpoint: str, method: str = "GET", transform: Callable[[Any], Any] | None = None, **kwargs: Any) -> FlextApiResponse:
        """Application-level request with context and transformation."""
        # Add application headers
        headers = kwargs.get("headers", {})
        app_headers = self.app_create_request_headers(headers)
        kwargs["headers"] = app_headers

        # Execute request
        response = await self._execute_request(method, endpoint, **kwargs)

        # Apply transformation if provided
        if transform and response["success"]:
            response = self.data_transform_response(response, transform)

        return response


def flext_api_create_enhanced_client(base_url: str, **config: Any) -> FlextApiEnhancedClient:
    """Create enhanced client with application patterns."""
    client = FlextApiEnhancedClient(base_url)

    # Configure client with provided settings
    if "user_id" in config:
        client.app_set_context("user_id", config["user_id"])
    if "correlation_id" in config:
        client.app_set_context("correlation_id", config["correlation_id"])
    if "service_name" in config:
        client.app_set_default_header("X-Service-Name", config["service_name"])

    return client
