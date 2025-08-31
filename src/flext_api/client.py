"""FlextApiClient - Single HTTP client class following FLEXT patterns.

Single consolidated HTTP client class that inherits from FlextDomainService,
uses FlextResult for all operations, and integrates with the global container.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from urllib.parse import urljoin

import aiohttp
from flext_core import (
    FlextContainer,
    FlextLogger,
    FlextModels,
    FlextResult,
)
from pydantic import Field

from flext_api.typings import FlextApiTypes

# Type aliases for cleaner code
ClientConfigDict = FlextApiTypes.Client.ClientConfigDict
RequestData = FlextApiTypes.Api.RequestData
Response = FlextApiTypes.Response.JsonResponse
Result = dict[str, object]

logger = FlextLogger(__name__)


class FlextApiClient(FlextModels.BaseConfig):
    """Single HTTP client class following FLEXT architectural patterns.

    Provides comprehensive HTTP client functionality with:
    - Inherits from FlextModels.BaseConfig for type safety
    - FlextResult for all operations - zero exceptions
    - Global dependency injection container
    - Type-safe configuration
    - Async/await support
    - Plugin system support
    """

    base_url: str = Field(..., description="Base URL for HTTP requests")
    timeout: float = Field(default=30.0, description="Request timeout in seconds")
    headers: dict[str, str] = Field(default_factory=dict, description="Default headers")
    max_retries: int = Field(default=3, description="Maximum retry attempts")

    def __init__(self, **data: object) -> None:
        """Initialize HTTP client with flext-core patterns."""
        super().__init__(**data)

        # Get global container - NO local containers
        self._container = FlextContainer.get_global()

        # Register self in global container
        self._container.register("flext_api_client", self)

        # Internal state
        self._session: aiohttp.ClientSession | None = None
        self._plugins: list[object] = []

        logger.info("FlextApiClient initialized", base_url=self.base_url)

    @property
    def plugins(self) -> list[object]:
        """Get list of registered plugins."""
        return self._plugins

    def get_info(self) -> FlextResult[Result]:
        """Get client information - returns FlextResult, never raises."""
        return FlextResult[Result].ok({
            "client": "FlextApiClient",
            "base_url": self.base_url,
            "status": "ready",
            "has_session": self._session is not None,
        })

    async def get(self, path: str) -> FlextResult[Response]:
        """Perform HTTP GET request - returns FlextResult, never raises."""
        url = ""  # Initialize for error handling
        try:
            url = urljoin(self.base_url, path)

            if not self._session:
                session_result = await self._create_session()
                if session_result.is_failure:
                    return FlextResult[Response].fail(
                        f"Session creation failed: {session_result.error}"
                    )

            if self._session is None:  # Should not happen, but safety check
                return FlextResult[Response].fail(
                    "Session not initialized"
                )
            async with self._session.get(url) as response:
                if response.content_type == "application/json":
                    data = await response.json()
                else:
                    data = await response.text()

                return FlextResult[Response].ok({
                    "status_code": response.status,
                    "data": data,
                    "headers": dict(response.headers),
                    "url": str(response.url),
                })

        except Exception as e:
            logger.exception(
                "HTTP GET failed", error=str(e), url=url if "url" in locals() else path
            )
            return FlextResult[Response].fail(f"HTTP GET failed: {e}")

    async def post(
        self,
        path: str,
        data: RequestData | None = None,
    ) -> FlextResult[Response]:
        """Perform HTTP POST request - returns FlextResult, never raises."""
        url = ""  # Initialize for error handling
        try:
            url = urljoin(self.base_url, path)

            if not self._session:
                session_result = await self._create_session()
                if session_result.is_failure:
                    return FlextResult[Response].fail(
                        f"Session creation failed: {session_result.error}"
                    )

            if self._session is None:  # Should not happen, but safety check
                return FlextResult[Response].fail(
                    "Session not initialized"
                )
            async with self._session.post(url, json=data) as response:
                if response.content_type == "application/json":
                    response_data = await response.json()
                else:
                    response_data = await response.text()

                return FlextResult[Response].ok({
                    "status_code": response.status,
                    "data": response_data,
                    "headers": dict(response.headers),
                    "url": str(response.url),
                })

        except Exception as e:
            logger.exception(
                "HTTP POST failed", error=str(e), url=url if "url" in locals() else path
            )
            return FlextResult[Response].fail(f"HTTP POST failed: {e}")

    async def put(
        self,
        path: str,
        data: RequestData | None = None,
    ) -> FlextResult[Response]:
        """Perform HTTP PUT request - returns FlextResult, never raises."""
        url = ""  # Initialize for error handling
        try:
            url = urljoin(self.base_url, path)

            if not self._session:
                session_result = await self._create_session()
                if session_result.is_failure:
                    return FlextResult[Response].fail(
                        f"Session creation failed: {session_result.error}"
                    )

            if self._session is None:  # Should not happen, but safety check
                return FlextResult[Response].fail(
                    "Session not initialized"
                )
            async with self._session.put(url, json=data) as response:
                if response.content_type == "application/json":
                    response_data = await response.json()
                else:
                    response_data = await response.text()

                return FlextResult[Response].ok({
                    "status_code": response.status,
                    "data": response_data,
                    "headers": dict(response.headers),
                    "url": str(response.url),
                })

        except Exception as e:
            logger.exception(
                "HTTP PUT failed", error=str(e), url=url if "url" in locals() else path
            )
            return FlextResult[Response].fail(f"HTTP PUT failed: {e}")

    async def delete(self, path: str) -> FlextResult[Response]:
        """Perform HTTP DELETE request - returns FlextResult, never raises."""
        url = ""  # Initialize for error handling
        try:
            url = urljoin(self.base_url, path)

            if not self._session:
                session_result = await self._create_session()
                if session_result.is_failure:
                    return FlextResult[Response].fail(
                        f"Session creation failed: {session_result.error}"
                    )

            if self._session is None:  # Should not happen, but safety check
                return FlextResult[Response].fail(
                    "Session not initialized"
                )
            async with self._session.delete(url) as response:
                if response.content_type == "application/json":
                    response_data = await response.json()
                else:
                    response_data = await response.text()

                return FlextResult[Response].ok({
                    "status_code": response.status,
                    "data": response_data,
                    "headers": dict(response.headers),
                    "url": str(response.url),
                })

        except Exception as e:
            logger.exception(
                "HTTP DELETE failed",
                error=str(e),
                url=url if "url" in locals() else path,
            )
            return FlextResult[Response].fail(f"HTTP DELETE failed: {e}")

    async def _create_session(self) -> FlextResult[None]:
        """Create aiohttp session - internal helper."""
        try:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout), headers=self.headers
            )
            logger.debug("HTTP session created", timeout=self.timeout)
            return FlextResult[None].ok(None)

        except Exception as e:
            logger.exception("Failed to create HTTP session", error=str(e))
            return FlextResult[None].fail(f"Failed to create session: {e}")

    async def close(self) -> FlextResult[None]:
        """Close HTTP session - returns FlextResult, never raises."""
        try:
            if self._session:
                await self._session.close()
                self._session = None

            logger.info("FlextApiClient closed")
            return FlextResult[None].ok(None)

        except Exception as e:
            logger.exception("Failed to close HTTP client", error=str(e))
            return FlextResult[None].fail(f"Failed to close: {e}")


__all__ = ["FlextApiClient"]
