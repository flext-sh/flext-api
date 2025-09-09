"""Advanced HTTP Client for FLEXT API - Real Web API Data Retrieval Library.

This is the core module of flext-api containing a SINGLE advanced HTTP client class
that provides comprehensive web API data retrieval functionality using ONLY existing
flext-api modules extensively. Uses real httpx and aiohttp with flext-core patterns,
Python 3.13+ features, Pydantic 2.11, and SOLID principles.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import asyncio
import base64
import json
import ssl
import time
import types
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Self, TypeVar
from urllib.parse import urljoin

import aiohttp
import httpx
from aiofiles import open as aio_open
from flext_core import FlextContainer, FlextLogger, FlextResult, FlextTypes

from flext_api.constants import FlextApiConstants
from flext_api.models import FlextApiModels
from flext_api.typings import FlextApiTypes
from flext_api.utilities import FlextApiUtilities

# Type variables for generic functionality
ResponseT = TypeVar("ResponseT", bound=FlextApiModels.HttpResponse)

# Module logger using flext-core pattern
logger = FlextLogger(__name__)

# Get dependency injection container
container = FlextContainer.get_global()


class FlextApiClient:
    """SINGLE advanced HTTP client for comprehensive web API data retrieval.

    This is the ONLY class in this module that provides enterprise-grade HTTP client
    functionality using ALL existing flext-api modules extensively:
    - FlextApiModels for configuration and data models
    - FlextApiConstants for all constants and configurations
    - FlextApiUtilities for validation, response building, and utilities
    - FlextApiProtocols for type safety and contracts
    - Real httpx and aiohttp for HTTP operations
    - FlextResult for railway-oriented programming
    - Advanced Python 3.13+ features and patterns
    """

    def __init__(
        self,
        config: FlextApiModels.ClientConfig | FlextTypes.Core.Dict | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize the advanced HTTP client using existing flext-api models."""
        # Use existing FlextApiModels.ClientConfig for configuration
        self.config = self._normalize_config(config, kwargs)

        # HTTP clients (lazy initialized)
        self._httpx_client: httpx.AsyncClient | None = None
        self._aiohttp_session: aiohttp.ClientSession | None = None

        # Advanced features using existing models and constants
        self._cache: dict[str, tuple[object, float]] = {}
        self._rate_limit_tokens = (
            float(self.config.rate_burst_size) if self.config.enable_rate_limit else 0.0
        )
        self._rate_limit_last_refill = time.time()
        self._circuit_breaker_state = "closed"  # closed | open | half_open
        self._circuit_failure_count = 0
        self._circuit_last_failure = 0.0
        self._request_metrics: list[FlextApiTypes.Core.Dict] = []

        logger.info(
            "FlextApiClient initialized with advanced features",
            base_url=self.config.base_url,
            features={
                "caching": self.config.enable_caching,
                "rate_limiting": self.config.enable_rate_limit,
                "circuit_breaker": self.config.enable_circuit_breaker,
                "retry": self.config.enable_retry,
                "auth": self.config.auth_type,
            },
        )

    @staticmethod
    def _normalize_config(
        config: FlextApiModels.ClientConfig | FlextTypes.Core.Dict | None,
        kwargs: FlextTypes.Core.Dict,
    ) -> FlextApiModels.ClientConfig:
        """Normalize configuration using existing FlextApiModels."""
        if config is None:
            base = (
                dict(kwargs)
                if kwargs
                else {
                    "base_url": "",
                    "timeout": FlextApiConstants.Client.DEFAULT_TIMEOUT,
                    "max_retries": FlextApiConstants.Client.MAX_RETRIES,
                    "headers": {},
                }
            )
            return FlextApiModels.ClientConfig.model_validate(base)
        if isinstance(config, dict):
            merged = {**config, **kwargs}
            return FlextApiModels.ClientConfig.model_validate(merged)
        return config

    @classmethod
    def create(
        cls, config: FlextTypes.Core.Dict | FlextApiModels.ClientConfig
    ) -> FlextResult[FlextApiClient]:
        """Factory method using existing protocols and returning FlextResult."""
        try:
            cfg_model = (
                config
                if isinstance(config, FlextApiModels.ClientConfig)
                else FlextApiModels.ClientConfig.model_validate(config)
            )

            # Use existing FlextApiUtilities for URL validation
            if cfg_model.base_url:
                url_validation = FlextApiUtilities.validate_url(cfg_model.base_url)
                if not url_validation.success:
                    return FlextResult[FlextApiClient].fail(
                        f"Invalid base URL: {url_validation.error}"
                    )

            client = cls(cfg_model)
            return FlextResult[FlextApiClient].ok(client)
        except Exception as e:
            return FlextResult[FlextApiClient].fail(
                f"Failed to create client: {e}"
            )

    @property
    def base_url(self) -> str:
        """Get base URL from configuration."""
        return self.config.base_url

    @property
    def timeout(self) -> float:
        """Get timeout from configuration."""
        return self.config.timeout

    @property
    def max_retries(self) -> int:
        """Get max retries from configuration."""
        return self.config.max_retries

    @property
    def httpx_client(self) -> httpx.AsyncClient:
        """Get or create httpx client with advanced configuration."""
        if self._httpx_client is None:
            # Build SSL context
            ssl_context = None
            if self.config.verify_ssl:
                ssl_context = ssl.create_default_context()

            # Configure limits using constants
            limits = httpx.Limits(
                max_connections=FlextApiConstants.Client.CONNECTION_POOL_SIZE,
                max_keepalive_connections=20,
                keepalive_expiry=5.0,
            )

            # Configure timeout
            timeout = httpx.Timeout(
                connect=10.0,
                read=self.config.timeout,
                write=self.config.timeout,
                pool=5.0,
            )

            self._httpx_client = httpx.AsyncClient(
                base_url=self.config.base_url,
                timeout=timeout,
                limits=limits,
                verify=ssl_context or True,
                headers=self._build_headers(),
                cookies=httpx.Cookies(),
                http2=True,  # Enable HTTP/2 for performance
            )

        return self._httpx_client

    @property
    def aiohttp_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session with advanced configuration."""
        if self._aiohttp_session is None:
            # Build connector with advanced settings
            connector = aiohttp.TCPConnector(
                limit=FlextApiConstants.Client.CONNECTION_POOL_SIZE,
                limit_per_host=20,
                keepalive_timeout=5.0,
                use_dns_cache=True,
                ttl_dns_cache=300,
            )

            # Configure timeout
            timeout = aiohttp.ClientTimeout(
                total=self.config.timeout,
                connect=10.0,
                sock_read=self.config.timeout,
            )

            self._aiohttp_session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers=self._build_headers(),
                cookie_jar=aiohttp.CookieJar(),
            )

        return self._aiohttp_session

    def _build_headers(self) -> FlextApiTypes.HttpHeaders:
        """Build headers with authentication using existing constants and models."""
        headers = {
            "User-Agent": FlextApiConstants.Client.DEFAULT_USER_AGENT,
            **FlextApiConstants.Client.DEFAULT_HEADERS,
            **self.config.headers,
        }

        # Add authentication using existing auth patterns
        if self.config.auth_type == "bearer" and self.config.auth_token:
            headers["Authorization"] = f"Bearer {self.config.auth_token}"
        elif (
            self.config.auth_type == "basic"
            and self.config.auth_username
            and self.config.auth_password
        ):
            creds = f"{self.config.auth_username}:{self.config.auth_password}".encode()
            headers["Authorization"] = f"Basic {base64.b64encode(creds).decode()}"

        return headers

    def _generate_cache_key(
        self, method: str, url: str, params: FlextApiTypes.QueryParameters | None = None
    ) -> str:
        """Generate cache key for request."""
        key_parts = [method.upper(), url]
        if params:
            sorted_params = sorted(params.items())
            params_str = "&".join(f"{k}={v}" for k, v in sorted_params)
            key_parts.append(params_str)
        return "|".join(key_parts)

    async def _check_rate_limit(self) -> FlextResult[None]:
        """Check rate limiting using token bucket algorithm."""
        if not self.config.enable_rate_limit:
            return FlextResult.ok(None)

        now = time.time()
        elapsed = now - self._rate_limit_last_refill

        # Refill tokens
        refill_rate = self.config.rate_calls_per_second
        self._rate_limit_tokens = min(
            self.config.rate_burst_size, self._rate_limit_tokens + elapsed * refill_rate
        )
        self._rate_limit_last_refill = now

        if self._rate_limit_tokens >= 1.0:
            self._rate_limit_tokens -= 1.0
            return FlextResult.ok(None)

        return FlextResult.fail("Rate limit exceeded")

    async def _check_circuit_breaker(self) -> FlextResult[None]:
        """Check circuit breaker state using existing configuration."""
        if not self.config.enable_circuit_breaker:
            return FlextResult.ok(None)

        now = time.time()

        if self._circuit_breaker_state == "open":
            if now - self._circuit_last_failure > self.config.circuit_recovery_timeout:
                self._circuit_breaker_state = "half_open"
            else:
                return FlextResult.fail("Circuit breaker is open")

        return FlextResult.ok(None)

    def _record_circuit_success(self) -> None:
        """Record successful circuit breaker operation."""
        if self.config.enable_circuit_breaker:
            if self._circuit_breaker_state in {"half_open", "open"}:
                self._circuit_breaker_state = "closed"
            self._circuit_failure_count = max(0, self._circuit_failure_count - 1)

    def _record_circuit_failure(self) -> None:
        """Record failed circuit breaker operation."""
        if self.config.enable_circuit_breaker:
            self._circuit_failure_count += 1
            self._circuit_last_failure = time.time()

            if self._circuit_failure_count >= self.config.circuit_failure_threshold:
                self._circuit_breaker_state = "open"

    def _calculate_retry_delay(self, attempt: int) -> float:
        """Calculate retry delay with exponential backoff."""
        base_delay = 1.0
        max_delay = 60.0
        delay = base_delay * (self.config.retry_backoff_factor**attempt)
        return min(delay, max_delay)

    async def request(
        self,
        method: str,
        url: str,
        *,
        params: FlextApiTypes.QueryParameters | None = None,
        headers: FlextApiTypes.HttpHeaders | None = None,
        data: bytes | str | None = None,
        json_data: dict[str, object] | list[object] | None = None,
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Make HTTP request with all advanced features using existing modules."""
        # Validate HTTP method using existing utilities
        method_validation = FlextApiUtilities.HttpValidator.validate_http_method(method)
        if not method_validation.success:
            return FlextResult.fail(method_validation.error or "Invalid HTTP method")

        validated_method = method_validation.value
        request_start = datetime.now(UTC)

        # Build full URL
        if self.config.base_url and not url.startswith(("http://", "https://")):
            full_url = urljoin(self.config.base_url.rstrip("/") + "/", url.lstrip("/"))
        else:
            full_url = url

        # Validate full URL using existing utilities
        url_validation = FlextApiUtilities.validate_url(full_url)
        if not url_validation.success:
            return FlextResult.fail(f"Invalid URL: {url_validation.error}")

        validated_url = url_validation.value

        # Check cache for GET requests
        cache_key = ""
        if self.config.enable_caching and validated_method == "GET":
            cache_key = self._generate_cache_key(
                validated_method, validated_url, params
            )
            if cache_key in self._cache:
                cached_data, cache_time = self._cache[cache_key]
                if time.time() - cache_time < self.config.cache_ttl:
                    logger.info("Request served from cache", url=validated_url)
                    # Type assertion - cached_data should be HttpResponse
                    if isinstance(cached_data, FlextApiModels.HttpResponse):
                        return FlextResult.ok(cached_data)
                    # If not proper type, remove from cache and continue
                del self._cache[cache_key]

        # Apply rate limiting
        rate_limit_result = await self._check_rate_limit()
        if not rate_limit_result.success:
            return FlextResult.fail(rate_limit_result.error or "Rate limit exceeded")

        # Check circuit breaker
        circuit_result = await self._check_circuit_breaker()
        if not circuit_result.success:
            return FlextResult.fail(circuit_result.error or "Circuit breaker open")

        # Retry loop with exponential backoff
        last_exception: Exception | None = None
        for attempt in range(self.config.max_retries + 1):
            try:
                if self.config.log_requests:
                    logger.info(
                        "Making HTTP request",
                        method=validated_method,
                        url=validated_url,
                        attempt=attempt,
                    )

                # Choose HTTP client engine (prefer httpx for HTTP/2 support)
                response_result = await self._make_httpx_request(
                    validated_method,
                    validated_url,
                    params=params,
                    headers=headers,
                    data=data,
                    json_data=json_data,
                )

                if response_result.success:
                    response = response_result.value

                    # Record success metrics
                    request_end = datetime.now(UTC)
                    duration_ms = (request_end - request_start).total_seconds() * 1000

                    self._request_metrics.append(
                        {
                            "method": validated_method,
                            "url": validated_url,
                            "status_code": response.status_code,
                            "duration_ms": duration_ms,
                            "attempt": attempt,
                            "from_cache": False,
                            "timestamp": request_end.isoformat(),
                        }
                    )

                    # Record circuit breaker success
                    self._record_circuit_success()

                    # Cache successful GET responses
                    if (
                        self.config.enable_caching
                        and cache_key
                        and validated_method == "GET"
                        and FlextApiConstants.HttpStatusRanges.SUCCESS_MIN
                        <= response.status_code
                        <= FlextApiConstants.HttpStatusRanges.SUCCESS_MAX
                    ):
                        if len(self._cache) >= self.config.cache_max_size:
                            # Simple LRU eviction
                            oldest_key = next(iter(self._cache))
                            del self._cache[oldest_key]
                        self._cache[cache_key] = (response, time.time())

                    if self.config.log_responses:
                        logger.info(
                            "HTTP request successful",
                            status_code=response.status_code,
                            duration_ms=duration_ms,
                        )

                    return FlextResult.ok(response)

                # Request failed, check if we should retry
                last_exception = Exception(response_result.error)

                if attempt < self.config.max_retries:
                    delay = self._calculate_retry_delay(attempt)
                    logger.warning(
                        "Request failed, retrying",
                        attempt=attempt,
                        delay=delay,
                        error=response_result.error,
                    )
                    await asyncio.sleep(delay)
                    continue
                break

            except Exception as e:
                last_exception = e
                logger.exception(
                    "Request attempt failed", attempt=attempt, error=str(e)
                )

                if attempt < self.config.max_retries:
                    delay = self._calculate_retry_delay(attempt)
                    await asyncio.sleep(delay)
                    continue
                break

        # All retries failed
        error_msg = f"Request failed after {self.config.max_retries + 1} attempts"
        if last_exception:
            error_msg += f": {last_exception}"

        # Record circuit breaker failure
        self._record_circuit_failure()

        if self.config.log_errors:
            logger.error("HTTP request failed", error=error_msg)

        return FlextResult.fail(error_msg)

    async def _make_httpx_request(
        self,
        method: str,
        url: str,
        *,
        params: FlextApiTypes.QueryParameters | None = None,
        headers: FlextApiTypes.HttpHeaders | None = None,
        data: bytes | str | None = None,
        json_data: dict[str, object] | list[object] | None = None,
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Make request using httpx with proper error handling."""
        try:
            # Merge headers
            request_headers = {**self._build_headers()}
            if headers:
                request_headers.update(headers)

            # Use asyncio.timeout context manager instead of timeout parameter
            async with asyncio.timeout(self.config.timeout):
                # Normaliza params para tipos aceitos por httpx
                normalized_params: (
                    dict[str, str | int | float | bool | list[str]] | None
                ) = None
                if params is not None:
                    norm: dict[str, str | int | float | bool | list[str]] = {}
                    for k, v in params.items():
                        if isinstance(v, (str, int, float, bool)) or (
                            isinstance(v, list) and all(isinstance(i, str) for i in v)
                        ):
                            norm[k] = v
                        else:
                            norm[k] = str(v)
                    normalized_params = norm

                # Create typed request parameters for httpx
                if json_data is not None:
                    response = await self.httpx_client.request(
                        method=method,
                        url=url,
                        params=normalized_params,
                        headers=request_headers,
                        json=json_data,
                        follow_redirects=True,
                    )
                elif data is not None:
                    response = await self.httpx_client.request(
                        method=method,
                        url=url,
                        params=normalized_params,
                        headers=request_headers,
                        content=data,
                        follow_redirects=True,
                    )
                else:
                    response = await self.httpx_client.request(
                        method=method,
                        url=url,
                        params=normalized_params,
                        headers=request_headers,
                        follow_redirects=True,
                    )

            # Parse response body
            content_type = response.headers.get("content-type", "")
            if "application/json" in content_type:
                try:
                    body = response.json()
                except json.JSONDecodeError:
                    body = response.text
            else:
                body = response.text

            # Create response using existing models
            flext_response = FlextApiModels.HttpResponse(
                status_code=response.status_code,
                body=body,
                headers=dict(response.headers),
                url=str(response.url),
                method=method.upper(),
            )

            return FlextResult.ok(flext_response)

        except httpx.TimeoutException as e:
            return FlextResult.fail(f"Request timeout: {e}")
        except httpx.NetworkError as e:
            return FlextResult.fail(f"Network error: {e}")
        except httpx.HTTPStatusError as e:
            # Still return response for non-2xx status codes
            flext_response = FlextApiModels.HttpResponse(
                status_code=e.response.status_code,
                body=e.response.text,
                headers=dict(e.response.headers),
                url=str(e.response.url),
                method=method.upper(),
            )
            return FlextResult.ok(flext_response)
        except Exception as e:
            return FlextResult.fail(f"Unexpected error: {e}")

    # HTTP verb convenience methods
    async def get(
        self,
        url: str,
        headers: FlextApiTypes.HttpHeaders | None = None,
        params: FlextApiTypes.QueryParameters | None = None,
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Perform HTTP GET request."""
        return await self.request(
            "GET",
            url,
            headers=headers,
            params=params,
        )

    async def post(
        self,
        url: str,
        data: dict[str, object] | list[object] | bytes | str | None = None,
        headers: FlextApiTypes.HttpHeaders | None = None,
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Perform HTTP POST request."""
        if isinstance(data, (dict, list)):
            return await self.request("POST", url, json_data=data, headers=headers)
        return await self.request("POST", url, data=data, headers=headers)

    async def put(
        self,
        url: str,
        data: dict[str, object] | list[object] | bytes | str | None = None,
        headers: FlextApiTypes.HttpHeaders | None = None,
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Perform HTTP PUT request."""
        if isinstance(data, (dict, list)):
            return await self.request("PUT", url, json_data=data, headers=headers)
        return await self.request("PUT", url, data=data, headers=headers)

    async def delete(
        self,
        url: str,
        headers: FlextApiTypes.HttpHeaders | None = None,
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Perform HTTP DELETE request."""
        return await self.request(
            "DELETE",
            url,
            headers=headers,
        )

    @asynccontextmanager
    async def stream(
        self,
        method: str,
        url: str,
        *,
        params: FlextApiTypes.QueryParameters | None = None,
        headers: FlextApiTypes.HttpHeaders | None = None,
    ) -> AsyncIterator[FlextResult[AsyncIterator[bytes]]]:
        """Stream response data for large downloads."""
        try:
            async with self.httpx_client.stream(
                method, url, params=params, headers=headers
            ) as response:
                yield FlextResult.ok(response.aiter_bytes(chunk_size=8192))
        except Exception as e:
            yield FlextResult.fail(f"Streaming failed: {e}")

    async def download_file(
        self,
        url: str,
        file_path: Path,
        *,
        params: FlextApiTypes.QueryParameters | None = None,
        headers: FlextApiTypes.HttpHeaders | None = None,
    ) -> FlextResult[Path]:
        """Download file with streaming support."""
        try:
            async with self.stream(
                "GET", url, params=params, headers=headers
            ) as stream_result:
                if not stream_result.success:
                    return FlextResult.fail(stream_result.error or "Stream failed")

                stream = stream_result.value

                async with aio_open(file_path, "wb") as f:
                    async for chunk in stream:
                        await f.write(chunk)

                logger.info(
                    "File downloaded successfully", url=url, path=str(file_path)
                )
                return FlextResult.ok(file_path)

        except Exception as e:
            logger.exception(
                "File download failed", url=url, path=str(file_path), error=str(e)
            )
            return FlextResult.fail(f"Download failed: {e}")

    def get_metrics(self) -> list[FlextApiTypes.Core.Dict]:
        """Get request metrics for observability."""
        return self._request_metrics.copy()

    def clear_cache(self) -> None:
        """Clear response cache."""
        self._cache.clear()
        logger.info("Response cache cleared")

    def health_check(self) -> FlextTypes.Core.Dict:
        """Health check using existing response building utilities."""
        try:
            # Use existing FlextApiUtilities for response building
            health_data = {
                "status": "healthy",
                "cache_size": len(self._cache),
                "circuit_breaker_state": self._circuit_breaker_state,
                "total_requests": len(self._request_metrics),
                "configuration": {
                    "base_url": self.config.base_url,
                    "timeout": self.config.timeout,
                    "max_retries": self.config.max_retries,
                    "features": {
                        "caching": self.config.enable_caching,
                        "rate_limiting": self.config.enable_rate_limit,
                        "circuit_breaker": self.config.enable_circuit_breaker,
                        "retry": self.config.enable_retry,
                    },
                },
            }

            # Use existing utilities to build success response
            response_result = FlextApiUtilities.ResponseBuilder.build_success_response(
                data=health_data,
                message="HTTP Client is healthy",
                status_code=FlextApiConstants.HttpStatus.OK,
            )

            if response_result.success:
                return response_result.value
            return {"status": "error", "message": "Health check failed"}

        except Exception as e:
            logger.exception("Health check failed", error=str(e))
            return {"status": "error", "message": f"Health check failed: {e}"}

    async def close(self) -> FlextResult[None]:
        """Close HTTP sessions and cleanup resources."""
        try:
            if self._httpx_client:
                await self._httpx_client.aclose()
                self._httpx_client = None

            if self._aiohttp_session:
                await self._aiohttp_session.close()
                self._aiohttp_session = None

            self.clear_cache()
            logger.info("HTTP client closed successfully")
            return FlextResult.ok(None)

        except Exception as e:
            logger.exception("Error closing HTTP client", error=str(e))
            return FlextResult.fail(f"Close failed: {e}")

    # Protocol compatibility methods
    async def start(self) -> FlextResult[None]:
        """Start the HTTP client (already initialized, no-op)."""
        return FlextResult.ok(None)

    async def stop(self) -> FlextResult[None]:
        """Stop the HTTP client (delegates to close)."""
        return await self.close()

    # Async context manager support
    async def __aenter__(self) -> Self:
        """Async context manager entry."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None:
        """Async context manager exit."""
        await self.close()


__all__ = ["FlextApiClient"]
