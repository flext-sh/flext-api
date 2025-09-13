"""FLEXT API Client - HTTP client using flext-core foundation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Self

import httpx
from flext_core import (
    FlextContainer,
    FlextDomainService,
    FlextLogger,
    FlextModels,
    FlextResult,
    FlextTypes,
)

from .constants import FlextApiConstants
from .models import FlextApiModels


class FlextApiClient(FlextDomainService[object]):
    """Unified HTTP client using flext-core extensively - ZERO DUPLICATION.

    Single Responsibility: HTTP requests only
    Open/Closed: Extensible through composition
    Dependency Inversion: Uses abstractions from flext-core
    """

    def __init__(
        self,
        config: FlextApiModels.ClientConfig | str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize HTTP client with streamlined configuration.

        Args:
            config: ClientConfig object or base_url string
            **kwargs: Override config values (base_url, timeout, max_retries, etc.)

        """
        super().__init__()

        # Use flext-core container and logger
        self._container = FlextContainer.get_global()
        self._logger = FlextLogger(__name__)

        # Create configuration from input
        if isinstance(config, str):
            # Base URL string provided - validate properly
            converted_kwargs = self._convert_kwargs_to_client_config_kwargs(kwargs)
            self._client_config = FlextApiModels.ClientConfig(
                base_url=config,
                **converted_kwargs,  # type: ignore[misc]
            )
        elif isinstance(config, FlextApiModels.ClientConfig):
            # Config object provided - apply any overrides
            config_dict = config.model_dump()
            converted_kwargs = self._convert_kwargs_to_client_config_kwargs(kwargs)
            config_dict.update(converted_kwargs)
            self._client_config = FlextApiModels.ClientConfig(**config_dict)
        else:
            # Handle None config - use defaults
            base_url = FlextApiConstants.DEFAULT_BASE_URL  # Default fallback

            converted_kwargs = self._convert_kwargs_to_client_config_kwargs(kwargs)
            self._client_config = FlextApiModels.ClientConfig(
                base_url=base_url,
                **converted_kwargs,  # type: ignore[misc]
            )

        # Store minimal state - everything comes from config
        self._connection_manager = self._ConnectionManager(
            self._client_config.base_url, self._client_config.timeout
        )

        # Simple metrics tracking
        self._request_count = 0
        self._error_count = 0

    def _convert_kwargs_to_client_config_kwargs(
        self, kwargs: dict[str, object]
    ) -> dict[str, str | int | float | dict[str, str] | None]:
        """Convert kwargs to properly typed ClientConfig parameters."""
        # Valid ClientConfig field names and their expected types
        valid_fields = {
            "base_url": str,
            "timeout": (int, float),
            "max_retries": int,
            "headers": dict,
            "auth_token": (str, type(None)),
            "api_key": (str, type(None)),
        }

        converted_kwargs: dict[str, str | int | float | dict[str, str] | None] = {}

        for key, value in kwargs.items():
            if key not in valid_fields:
                # Skip invalid fields instead of raising error
                continue

            expected_type = valid_fields[key]

            # Handle type conversion
            try:
                if expected_type is str:
                    if isinstance(value, str):
                        converted_kwargs[key] = value
                elif expected_type is (str, type(None)):
                    if isinstance(value, str) or value is None:
                        converted_kwargs[key] = value
                elif expected_type is (int, float):
                    if isinstance(value, (int, float)):
                        converted_kwargs[key] = float(value)
                elif expected_type is int:
                    if isinstance(value, int):
                        converted_kwargs[key] = value
                elif expected_type is dict and isinstance(value, dict):
                    # Ensure headers dict has string values
                    if key == "headers":
                        converted_kwargs[key] = {k: str(v) for k, v in value.items()}
                    else:
                        converted_kwargs[key] = value
            except (ValueError, TypeError):
                # Skip invalid values instead of raising error
                continue

        return converted_kwargs

    # =============================================================================
    # STREAMLINED HELPER METHODS - Reduced bloat
    # =============================================================================

    class _ConnectionManager:
        """Manages HTTP connections - single responsibility."""

        def __init__(self, base_url: str, timeout: float) -> None:
            """Initialize the instance."""
            self._base_url = base_url
            self._timeout = timeout
            self._client: httpx.AsyncClient | None = None

        async def ensure_client(self) -> httpx.AsyncClient:
            """Ensure HTTP client is initialized."""
            if self._client is None:
                self._client = httpx.AsyncClient(
                    base_url=self._base_url, timeout=self._timeout
                )
            return self._client

        async def close(self) -> None:
            """Close HTTP client."""
            if self._client:
                await self._client.aclose()
                self._client = None

        @property
        def client(self) -> httpx.AsyncClient | None:
            """Get current client."""
            return self._client

    # =============================================================================
    # Essential Methods Only
    # =============================================================================

    def _get_headers(self, additional: dict[str, str] | None = None) -> dict[str, str]:
        """Get headers from config with optional additions."""
        headers = self._client_config.get_default_headers()
        if additional:
            headers.update(additional)
        return headers

    async def request(
        self, method: str, url: str, **kwargs: object
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Make HTTP request - alias for _request."""
        return await self._request(method, url, **kwargs)

    # =============================================================================
    # FlextDomainService Implementation
    # =============================================================================

    def execute(self) -> FlextResult[object]:
        """Execute the main domain service operation."""
        try:
            test_response = FlextApiModels.HttpResponse(
                status_code=200,
                body="HTTP client ready",
                headers={"Content-Type": "application/json"},
                url=self._client_config.base_url,
                method="GET",
            )
            return FlextResult[object].ok(test_response)
        except Exception as e:
            return FlextResult[object].fail(f"HTTP client execution failed: {e}")

    async def start(self) -> FlextResult[None]:
        """Start the HTTP client service."""
        try:
            await self._connection_manager.ensure_client()
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Failed to start HTTP client: {e}")

    async def stop(self) -> FlextResult[None]:
        """Stop the HTTP client service."""
        try:
            await self._connection_manager.close()
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Failed to stop HTTP client: {e}")

    def health_check(self) -> FlextTypes.Core.Dict:
        """Health check for the HTTP client service."""
        return {
            "status": "healthy"
            if self._connection_manager.client is not None
            else "stopped",
            "base_url": self._client_config.base_url,
            "timeout": self._client_config.timeout,
            "max_retries": self._client_config.max_retries,
            "request_count": self._request_count,
            "error_count": self._error_count,
            "message": "HTTP client is operational",
            "status_code": 200,
        }

    def configure(self, config: FlextTypes.Core.Dict) -> FlextResult[None]:
        """Configure the HTTP client with new settings."""
        try:
            # Update client config with new values
            current_config = self._client_config.model_dump()
            current_config.update(config)
            self._client_config = FlextApiModels.ClientConfig(**current_config)

            # Recreate connection manager with new config
            self._connection_manager = self._ConnectionManager(
                self._client_config.base_url, self._client_config.timeout
            )
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Configuration failed: {e}")

    def get_config(self) -> FlextTypes.Core.Dict:
        """Get current configuration."""
        return self._client_config.model_dump()

    # =============================================================================
    # Public API - HTTP Methods
    # =============================================================================

    async def get(
        self, url: str, **kwargs: object
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Make GET request."""
        return await self._request("GET", url, **kwargs)

    async def post(
        self, url: str, **kwargs: object
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Make POST request."""
        return await self._request("POST", url, **kwargs)

    async def put(
        self, url: str, **kwargs: object
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Make PUT request."""
        return await self._request("PUT", url, **kwargs)

    async def delete(
        self, url: str, **kwargs: object
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Make DELETE request."""
        return await self._request("DELETE", url, **kwargs)

    # =============================================================================
    # Essential Properties Only
    # =============================================================================

    @property
    def base_url(self) -> str:
        """Get base URL from config."""
        return self._client_config.base_url

    @property
    def timeout(self) -> float:
        """Get timeout from config."""
        return self._client_config.timeout

    @property
    def max_retries(self) -> int:
        """Get max retries from config."""
        return self._client_config.max_retries

    @property
    def config(self) -> FlextApiModels.ClientConfig:
        """Get client configuration object."""
        return self._client_config

    # =============================================================================
    # Context Manager Support
    # =============================================================================

    async def __aenter__(self) -> Self:
        """Async context manager entry."""
        await self._connection_manager.ensure_client()
        return self

    async def __aexit__(
        self, exc_type: object, exc_val: object, exc_tb: object
    ) -> None:
        """Async context manager exit."""
        await self._connection_manager.close()

    async def close(self) -> FlextResult[None]:
        """Close HTTP client."""
        try:
            await self._connection_manager.close()
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Failed to close HTTP client: {e}")

    # =============================================================================
    # Essential Factory Methods Only
    # =============================================================================

    @classmethod
    def create(
        cls, config_data: dict[str, object] | FlextApiModels.ClientConfig
    ) -> FlextResult[FlextApiClient]:
        """Create HTTP client from configuration data - streamlined."""
        try:
            if isinstance(config_data, FlextApiModels.ClientConfig):
                client = cls(config_data)
            else:
                # Convert dict to ClientConfig for validation
                client_config = FlextApiModels.ClientConfig.model_validate(config_data)
                client = cls(client_config)
            return FlextResult[FlextApiClient].ok(client)
        except Exception as e:
            return FlextResult[FlextApiClient].fail(f"Failed to create client: {e}")

    # =============================================================================
    # Simple Helper Methods
    # =============================================================================

    def _build_url(self, endpoint: str) -> str:
        """Build complete URL from base URL and endpoint."""
        if endpoint.startswith(("http://", "https://")):
            return endpoint
        if not self._client_config.base_url:
            return endpoint
        base = self._client_config.base_url.rstrip("/")
        endpoint = endpoint.lstrip("/")
        return f"{base}/{endpoint}" if endpoint else base

    # Removed duplicate header method - using _get_headers() instead

    # =============================================================================
    # Internal Implementation
    # =============================================================================

    async def _request(
        self, method: str, url: str, **kwargs: object
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Make HTTP request using flext-core HttpRequestConfig."""
        try:
            # Extract headers safely
            headers_obj = kwargs.get("headers")
            additional_headers = headers_obj if isinstance(headers_obj, dict) else None

            # Use flext-core HttpRequestConfig with streamlined config
            request_config = FlextModels.Http.HttpRequestConfig(
                url=self._build_url(url),
                method=method,
                timeout=int(self._client_config.timeout),
                retries=self._client_config.max_retries,
                headers=self._get_headers(additional_headers),
            )

            client = await self._connection_manager.ensure_client()

            # Simple httpx call using config values with safe parameter extraction
            params_obj = kwargs.get("params")
            params = params_obj if isinstance(params_obj, dict) else None

            json_obj = kwargs.get("json")
            json_data = json_obj if json_obj is not None else None

            data_obj = kwargs.get("data")
            data = (
                data_obj
                if data_obj is not None and isinstance(data_obj, dict)
                else None
            )

            files_obj = kwargs.get("files")
            files = (
                files_obj
                if files_obj is not None and isinstance(files_obj, dict)
                else None
            )

            response = await client.request(
                method=request_config.method,
                url=request_config.url,
                headers=request_config.headers,
                timeout=request_config.timeout,
                params=params,
                json=json_data,
                data=data,
                files=files,
            )

            # Simple response processing
            api_response = FlextApiModels.HttpResponse(
                status_code=response.status_code,
                body=response.text,
                headers=dict(response.headers),
                url=str(response.url),
                method=method,
            )

            return FlextResult[FlextApiModels.HttpResponse].ok(api_response)

        except httpx.HTTPError as e:
            return FlextResult[FlextApiModels.HttpResponse].fail(
                f"HTTP request failed: {e}"
            )
        except Exception as e:
            return FlextResult[FlextApiModels.HttpResponse].fail(
                f"Unexpected error: {e}"
            )
