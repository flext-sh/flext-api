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

import httpx
from flext_core import FlextDomainService, FlextLogger, FlextResult, FlextUtilities
from pydantic import Field

from flext_api.constants import FlextApiConstants
from flext_api.typings import FlextApiTypes

logger = FlextLogger(__name__)


class FlextApiClient(FlextDomainService[dict[str, object]]):
    """REAL HTTP client using httpx with comprehensive FLEXT patterns integration."""

    base_url: str = Field(..., description="Base URL for HTTP requests")
    timeout: float = Field(default=30.0, description="Request timeout in seconds")
    headers: dict[str, str] = Field(default_factory=dict, description="Default headers")
    max_retries: int = Field(default=3, description="Maximum retry attempts")

    def __init__(self, **data: object) -> None:
        """Initialize REAL HTTP client with httpx and flext-core patterns."""
        super().__init__(**data)

        # REAL httpx client - will be initialized in start()
        self._client: httpx.AsyncClient | None = None
        self._session_started = False

        # Use FlextUtilities.Generators for request IDs
        self._client_id = FlextUtilities.Generators.generate_entity_id()

        logger.info(
            "HTTP client initialized", client_id=self._client_id, base_url=self.base_url
        )

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
        if not self._session_started or self._client is None:
            return FlextResult[FlextApiTypes.Response.JsonResponse].fail(
                "HTTP session not started. Call start() first."
            )

        # Generate request ID using FlextUtilities
        request_id = FlextUtilities.Generators.generate_request_id()
        url = FlextUtilities.TextProcessor.join_url_path(
            self.base_url, path.lstrip("/")
        )

        # Prepare request parameters
        request_kwargs = {
            "method": method,
            "url": url,
            "params": params,
        }

        if json_data is not None:
            request_kwargs["json"] = json_data
        elif data is not None:
            request_kwargs["content"] = data

        # Execute request with retries
        last_error: Exception | None = None

        for attempt in range(self.max_retries + 1):
            try:
                logger.debug(
                    "Making HTTP request",
                    request_id=request_id,
                    method=method,
                    url=url,
                    attempt=attempt + 1,
                )

                response = await self._client.request(**request_kwargs)

                # Parse response
                try:
                    if response.headers.get("content-type", "").startswith(
                        "application/json"
                    ):
                        response_data = response.json()
                    else:
                        response_data = {
                            "content": response.text,
                            "status_code": response.status_code,
                        }
                except Exception:
                    response_data = {
                        "content": response.text,
                        "status_code": response.status_code,
                    }

                # Check for HTTP errors
                if (
                    response.status_code
                    >= FlextApiConstants.Validation.CLIENT_ERROR_MIN
                ):
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                    logger.warning(
                        "HTTP request failed",
                        request_id=request_id,
                        status_code=response.status_code,
                        error=error_msg,
                    )

                    # Don't retry client errors (4xx), only server errors (5xx)
                    if (
                        response.status_code
                        < FlextApiConstants.Validation.SERVER_ERROR_MIN
                        or attempt == self.max_retries
                    ):
                        return FlextResult[FlextApiTypes.Response.JsonResponse].fail(
                            error_msg
                        )

                    # Wait before retry for server errors
                    await asyncio.sleep(2**attempt)
                    continue

                # Success
                logger.debug(
                    "HTTP request successful",
                    request_id=request_id,
                    status_code=response.status_code,
                )

                return FlextResult[FlextApiTypes.Response.JsonResponse].ok(
                    response_data
                )

            except httpx.TimeoutException as e:
                last_error = e
                logger.warning(
                    "HTTP request timeout",
                    request_id=request_id,
                    attempt=attempt + 1,
                    timeout=self.timeout,
                )

                if attempt == self.max_retries:
                    break

                # Exponential backoff for timeouts
                await asyncio.sleep(2**attempt)

            except httpx.RequestError as e:
                last_error = e
                logger.warning(
                    "HTTP request error",
                    request_id=request_id,
                    attempt=attempt + 1,
                    error=str(e),
                )

                if attempt == self.max_retries:
                    break

                # Exponential backoff for network errors
                await asyncio.sleep(2**attempt)

            except Exception as e:
                last_error = e
                logger.exception(
                    "Unexpected HTTP request error",
                    request_id=request_id,
                    attempt=attempt + 1,
                    error=str(e),
                )

                if attempt == self.max_retries:
                    break

                await asyncio.sleep(2**attempt)

        # All retries exhausted
        error_msg = (
            f"HTTP request failed after {self.max_retries + 1} attempts: {last_error}"
        )
        logger.error(
            "HTTP request retries exhausted",
            request_id=request_id,
            max_retries=self.max_retries,
            final_error=str(last_error),
        )

        return FlextResult[FlextApiTypes.Response.JsonResponse].fail(error_msg)


__all__ = ["FlextApiClient"]
