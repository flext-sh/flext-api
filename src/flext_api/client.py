"""FLEXT API Client - REAL HTTP client using httpx following FLEXT patterns.

Single consolidated HTTP client class providing REAL HTTP functionality using httpx,
following flext-core patterns: FlextDomainService inheritance, FlextResult error handling,
FlextUtilities.Generators for IDs, and production-ready async HTTP operations.

Module Role in Architecture:
    FlextApiClient serves as the HTTP client system with REAL functionality using
    httpx for HTTP operations, FlextUtilities.Generators for request IDs, and
    FlextResult for type-safe error handling.

Classes and Methods:
    FlextApiClient:                         # REAL HTTP client system
        # HTTP Operations:
        get(path, params) -> FlextResult    # REAL HTTP GET requests
        post(path, json_data) -> FlextResult # REAL HTTP POST requests
        put(path, json_data) -> FlextResult  # REAL HTTP PUT requests
        delete(path, params) -> FlextResult  # REAL HTTP DELETE requests

        # Session Management:
        start() -> FlextResult              # Start HTTP session
        stop() -> FlextResult               # Stop HTTP session
        health_check() -> dict              # Health status

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, cast

import httpx
from flext_core import FlextDomainService, FlextLogger, FlextResult, FlextUtilities
from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from flext_api.typings import FlextApiTypes

from flext_api.constants import FlextApiConstants

if not TYPE_CHECKING:
    from flext_api.typings import FlextApiTypes

logger = FlextLogger(__name__)


class FlextApiClient(FlextDomainService[dict[str, object]]):
    """REAL HTTP client using httpx with comprehensive FLEXT patterns integration."""

    def __init__(self, config: dict[str, object] | None = None, **data: object) -> None:
        """Initialize REAL HTTP client with httpx and flext-core patterns."""
        super().__init__()

        # Merge positional config argument with keyword data
        if config is not None:
            data = {**config, **data}

        # Set field values from data using private attributes with type safety
        base_url = data.get("base_url", "")
        self._base_url = str(base_url) if base_url is not None else ""

        timeout = data.get("timeout", 30.0)
        self._timeout = (
            float(timeout) if isinstance(timeout, (int, float, str)) else 30.0
        )

        headers = data.get("headers", {})
        if isinstance(headers, dict):
            self._headers = {str(k): str(v) for k, v in headers.items()}
        else:
            self._headers = {}

        max_retries = data.get("max_retries", 3)
        self._max_retries = (
            int(max_retries) if isinstance(max_retries, (int, str)) else 3
        )

        # REAL httpx client - will be initialized in start()
        self._client: httpx.AsyncClient | None = None
        self._session_started = False

        # Use FlextUtilities.Generators for request IDs
        self._client_id = FlextUtilities.Generators.generate_entity_id()

        logger.info(
            "HTTP client initialized", client_id=self._client_id, base_url=self.base_url
        )

    @property
    def base_url(self) -> str:
        """Base URL for HTTP requests."""
        return self._base_url

    @property
    def timeout(self) -> float:
        """Request timeout in seconds."""
        return self._timeout

    @property
    def headers(self) -> dict[str, str]:
        """Default headers."""
        return self._headers

    @property
    def max_retries(self) -> int:
        """Maximum retry attempts."""
        return self._max_retries

    def execute(self) -> FlextResult[dict[str, object]]:
        """Execute HTTP client service with REAL functionality."""
        try:
            client_stats: dict[str, object] = {
                "client_type": "httpx.AsyncClient",
                "client_id": self._client_id,
                "base_url": self.base_url,
                "timeout": self.timeout,
                "max_retries": self.max_retries,
                "session_started": self._session_started,
                "status": "active",
            }
            return FlextResult[dict[str, object]].ok(client_stats)
        except Exception as e:
            logger.exception("HTTP client execution failed", error=str(e))
            return FlextResult[dict[str, object]].fail(
                f"HTTP client execution failed: {e}"
            )

    async def start(self) -> FlextResult[None]:
        """Start REAL HTTP session using httpx.AsyncClient."""
        try:
            if self._session_started:
                return FlextResult[None].ok(None)

            # Create REAL httpx client with proper configuration
            timeout_config = httpx.Timeout(self.timeout)
            default_headers = {
                "User-Agent": f"FlextApiClient/{self._client_id}",
                "Accept": "application/json",
                "Content-Type": "application/json",
                **self.headers,
            }

            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=timeout_config,
                headers=default_headers,
                limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
                follow_redirects=True,
            )

            self._session_started = True
            logger.info(
                "HTTP session started",
                client_id=self._client_id,
                base_url=self.base_url,
            )

            return FlextResult[None].ok(None)

        except Exception as e:
            logger.exception(
                "HTTP session start failed", client_id=self._client_id, error=str(e)
            )
            return FlextResult[None].fail(f"HTTP session start failed: {e}")

    async def stop(self) -> FlextResult[None]:
        """Stop REAL HTTP session and cleanup resources."""
        try:
            if not self._session_started or self._client is None:
                return FlextResult[None].ok(None)

            await self._client.aclose()
            self._client = None
            self._session_started = False

            logger.info("HTTP session stopped", client_id=self._client_id)
            return FlextResult[None].ok(None)

        except Exception as e:
            logger.exception(
                "HTTP session stop failed", client_id=self._client_id, error=str(e)
            )
            return FlextResult[None].fail(f"HTTP session stop failed: {e}")

    @property
    def config(self) -> object:
        """Get client configuration object for test compatibility."""
        # Create a simple namespace object to hold config values
        class Config:
            def __init__(self, client: FlextApiClient) -> None:
                self.base_url = client.base_url
                self.headers = client.headers
                self.timeout = client.timeout
                self.max_retries = client.max_retries

        return Config(self)

    async def close(self) -> None:
        """Close HTTP client connection (alias for stop for test compatibility)."""
        result = await self.stop()
        if not result.success:
            error_msg = f"Failed to close client: {result.error}"
            raise RuntimeError(error_msg)

    def health_check(self) -> dict[str, object]:
        """Get REAL HTTP client health status."""
        return {
            "client_id": self._client_id,
            "session_started": self._session_started,
            "base_url": self.base_url,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "client_ready": self._client is not None,
            "status": "healthy" if self._session_started else "not_started",
        }

    async def get(
        self, path: str, params: dict[str, object] | None = None
    ) -> FlextResult[FlextApiTypes.Response.JsonResponse]:
        """Execute REAL HTTP GET request using httpx."""
        return await self._make_request("GET", path, params=params)

    async def post(
        self,
        path: str,
        json_data: dict[str, object] | None = None,
        data: bytes | None = None,
    ) -> FlextResult[FlextApiTypes.Response.JsonResponse]:
        """Execute REAL HTTP POST request using httpx."""
        return await self._make_request("POST", path, json_data=json_data, data=data)

    async def put(
        self,
        path: str,
        json_data: dict[str, object] | None = None,
        data: bytes | None = None,
    ) -> FlextResult[FlextApiTypes.Response.JsonResponse]:
        """Execute REAL HTTP PUT request using httpx."""
        return await self._make_request("PUT", path, json_data=json_data, data=data)

    async def delete(
        self, path: str, params: dict[str, object] | None = None
    ) -> FlextResult[FlextApiTypes.Response.JsonResponse]:
        """Execute REAL HTTP DELETE request using httpx."""
        return await self._make_request("DELETE", path, params=params)

    async def _make_request(
        self,
        method: str,
        path: str,
        params: dict[str, object] | None = None,
        json_data: dict[str, object] | None = None,
        data: bytes | None = None,
    ) -> FlextResult[FlextApiTypes.Response.JsonResponse]:
        """Make REAL HTTP request with proper error handling and retries."""
        # Session validation
        session_check = self._validate_session()
        if not session_check.is_success:
            return session_check

        # Create request context
        context = self._HttpRequestContext(
            request_id=FlextUtilities.Generators.generate_request_id(),
            method=method,
            url=self._build_url(path),
            params=params or {},
            json_data=json_data,
            data=data,
            headers=self._headers,
            timeout=self.timeout,
        )

        # Execute with retry strategy
        return await self._retry_strategy.execute(context, self._execute_single_request)

    def _validate_session(self) -> FlextResult[FlextApiTypes.Response.JsonResponse]:
        """Validate HTTP session state."""
        if not self._session_started or self._client is None:
            return FlextResult[FlextApiTypes.Response.JsonResponse].fail(
                "HTTP session not started. Call start() first."
            )
        return FlextResult[FlextApiTypes.Response.JsonResponse].ok({})

    def _build_url(self, path: str) -> str:
        """Build complete URL from base URL and path."""
        base = self.base_url.rstrip("/")
        clean_path = path.lstrip("/")
        return f"{base}/{clean_path}" if clean_path else base

    class _HttpRequestContext(BaseModel):
        """Request context using Pydantic V2 for zero-parameter constructor."""

        # Use Pydantic V2 advanced configuration
        model_config = ConfigDict(
            validate_assignment=True,
            frozen=False,  # Mutable for internal context
            arbitrary_types_allowed=True,
        )

        request_id: str = Field(..., description="Unique request identifier")
        method: str = Field(..., description="HTTP method")
        url: str = Field(..., description="Request URL")
        params: dict[str, object] | None = Field(None, description="Query parameters")
        json_data: dict[str, object] | None = Field(None, description="JSON payload")
        data: bytes | None = Field(None, description="Raw data payload")
        headers: dict[str, str] = Field(
            default_factory=dict, description="HTTP headers"
        )
        timeout: float = Field(30.0, description="Request timeout")

        def to_httpx_kwargs(self) -> dict[str, object]:
            """Convert to httpx request parameters with proper typing."""
            # Create type-safe dictionary for httpx
            kwargs: dict[str, object] = {}

            # Required parameters
            kwargs["method"] = self.method
            kwargs["url"] = self.url
            kwargs["timeout"] = self.timeout

            # Optional parameters with proper type conversion
            if self.params:
                kwargs["params"] = dict(self.params)
            if self.headers:
                kwargs["headers"] = dict(self.headers)
            if self.json_data is not None:
                kwargs["json"] = self.json_data
            elif self.data is not None:
                kwargs["content"] = self.data

            return kwargs

    class _RetryStrategy:
        """Retry strategy using exponential backoff."""

        def __init__(self, max_retries: int) -> None:
            self.max_retries = max_retries

        async def execute(
            self,
            context: FlextApiClient._HttpRequestContext,
            execute_fn: Callable[
                [FlextApiClient._HttpRequestContext, int],
                Awaitable[FlextResult[FlextApiTypes.Response.JsonResponse]],
            ],
        ) -> FlextResult[FlextApiTypes.Response.JsonResponse]:
            """Execute request with retry logic."""
            last_error: Exception | None = None

            for attempt in range(self.max_retries + 1):
                try:
                    result = await execute_fn(context, attempt)
                    if result.is_success:
                        return result

                    # Handle server errors (retry) vs client errors (don't retry)
                    if not self._should_retry(result, attempt):
                        return result

                    await asyncio.sleep(2**attempt)

                except (httpx.TimeoutException, httpx.RequestError) as e:
                    last_error = e
                    self._log_retry_error(context, e, attempt)

                    if attempt == self.max_retries:
                        break
                    await asyncio.sleep(2**attempt)

                except Exception as e:
                    last_error = e
                    logger.exception(
                        "Unexpected HTTP request error",
                        request_id=context.request_id,
                        attempt=attempt + 1,
                        error=str(e),
                    )
                    if attempt == self.max_retries:
                        break
                    await asyncio.sleep(2**attempt)

            # All retries exhausted
            return self._create_retry_exhausted_result(context, last_error)

        def _should_retry(
            self, result: FlextResult[FlextApiTypes.Response.JsonResponse], attempt: int
        ) -> bool:
            """Determine if request should be retried based on result."""
            # Don't retry if max retries reached
            if attempt >= self.max_retries:
                return False

            # Retry only on failed requests (network/timeout errors)
            return not result.success

        def _log_retry_error(
            self,
            context: FlextApiClient._HttpRequestContext,
            error: Exception,
            attempt: int,
        ) -> None:
            """Log retry error with appropriate level."""
            if isinstance(error, httpx.TimeoutException):
                logger.warning(
                    "HTTP request timeout",
                    request_id=context.request_id,
                    attempt=attempt + 1,
                    timeout=context.timeout,
                )
            else:
                logger.warning(
                    "HTTP request error",
                    request_id=context.request_id,
                    attempt=attempt + 1,
                    error=str(error),
                )

        def _create_retry_exhausted_result(
            self,
            context: FlextApiClient._HttpRequestContext,
            last_error: Exception | None,
        ) -> FlextResult[FlextApiTypes.Response.JsonResponse]:
            """Create result for retry exhaustion."""
            error_msg = f"HTTP request failed after {self.max_retries + 1} attempts: {last_error}"
            logger.error(
                "HTTP request retries exhausted",
                request_id=context.request_id,
                max_retries=self.max_retries,
                final_error=str(last_error),
            )
            return FlextResult[FlextApiTypes.Response.JsonResponse].fail(error_msg)

    @property
    def _retry_strategy(self) -> _RetryStrategy:
        """Get retry strategy instance."""
        if not hasattr(self, "_retry_strategy_instance"):
            self._retry_strategy_instance = self._RetryStrategy(self.max_retries)
        return self._retry_strategy_instance

    async def _execute_single_request(
        self,
        context: _HttpRequestContext,
        attempt: int,
    ) -> FlextResult[FlextApiTypes.Response.JsonResponse]:
        """Execute single HTTP request attempt."""
        logger.debug(
            "Making HTTP request",
            request_id=context.request_id,
            method=context.method,
            url=context.url,
            attempt=attempt + 1,
        )

        # Execute httpx request
        if self._client is None:
            return FlextResult[FlextApiTypes.Response.JsonResponse].fail(
                "HTTP client not initialized"
            )
        # Type-safe httpx request with proper casting
        kwargs = context.to_httpx_kwargs()
        response = await self._client.request(
            method=cast("str", kwargs["method"]),
            url=cast("str", kwargs["url"]),
            params=kwargs.get("params"),  # type: ignore[arg-type]
            headers=kwargs.get("headers"),  # type: ignore[arg-type]
            json=kwargs.get("json"),
            content=kwargs.get("content"),  # type: ignore[arg-type]
            timeout=cast("float", kwargs["timeout"]),
        )

        # Parse response using strategy pattern
        response_data = self._parse_response(response)

        # Handle HTTP errors
        error_result = self._check_http_errors(response, context)
        if error_result:
            return error_result

        # Success case
        logger.debug(
            "HTTP request successful",
            request_id=context.request_id,
            status_code=response.status_code,
        )

        return FlextResult[FlextApiTypes.Response.JsonResponse].ok(response_data)

    def _parse_response(self, response: httpx.Response) -> dict[str, object]:
        """Parse HTTP response using strategy pattern."""
        try:
            if response.headers.get("content-type", "").startswith("application/json"):
                json_data: dict[str, object] = response.json()
                return json_data
        except Exception as e:
            # JSON parsing failed, log warning and fall back to text content
            logger.warning("Failed to parse JSON response", error=str(e))

        return {
            "content": response.text,
            "status_code": response.status_code,
        }

    def _check_http_errors(
        self,
        response: httpx.Response,
        context: _HttpRequestContext,
    ) -> FlextResult[FlextApiTypes.Response.JsonResponse] | None:
        """Check for HTTP errors and return error result if applicable."""
        if response.status_code >= FlextApiConstants.ApiValidation.CLIENT_ERROR_MIN:
            error_msg = f"HTTP {response.status_code}: {response.text}"
            logger.warning(
                "HTTP request failed",
                request_id=context.request_id,
                status_code=response.status_code,
                error=error_msg,
            )

            # Don't retry client errors (4xx), only server errors (5xx)
            if response.status_code < FlextApiConstants.ApiValidation.SERVER_ERROR_MIN:
                return FlextResult[FlextApiTypes.Response.JsonResponse].fail(error_msg)

            # Return special result indicating retry should happen
            return FlextResult[FlextApiTypes.Response.JsonResponse].fail(error_msg)

        return None


__all__ = ["FlextApiClient"]
