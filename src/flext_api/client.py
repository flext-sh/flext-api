"""FLEXT API Client - HTTP client using flext-core foundation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping
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

from flext_api.app import create_fastapi_app
from flext_api.config import FlextApiConfig
from flext_api.constants import FlextApiConstants
from flext_api.models import FlextApiModels


class FlextApiClient(FlextDomainService[object]):
    """Unified HTTP client using flext-core extensively - ZERO DUPLICATION.

    Single Responsibility: HTTP requests only
    Open/Closed: Extensible through composition
    Dependency Inversion: Uses abstractions from flext-core
    """

    def __init__(
        self,
        config: FlextApiModels.ClientConfig
        | FlextApiConfig
        | Mapping[str, object]
        | str
        | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize HTTP client with streamlined configuration.

        Args:
            config: ClientConfig object, FlextApiConfig object, or base_url string
            **kwargs: Override config values (base_url, timeout, max_retries, etc.)

        """
        super().__init__()

        # Use flext-core container and logger
        self._container = FlextContainer.get_global()
        self._logger = FlextLogger(__name__)

        # Create configuration from input
        if isinstance(config, str):
            # Base URL string provided - validate properly
            base_url, timeout, max_retries, headers, auth_token, api_key = (
                self._extract_client_config_params(kwargs)
            )
            self._client_config = FlextApiModels.ClientConfig(
                base_url=config,
                timeout=timeout
                if timeout is not None
                else FlextApiConstants.DEFAULT_TIMEOUT,
                max_retries=max_retries
                if max_retries is not None
                else FlextApiConstants.DEFAULT_RETRIES,
                headers=headers if headers is not None else {},
                auth_token=auth_token,
                api_key=api_key,
            )
        elif isinstance(config, FlextApiModels.ClientConfig):
            # Config object provided - apply any overrides
            base_url, timeout, max_retries, headers, auth_token, api_key = (
                self._extract_client_config_params(kwargs)
            )
            self._client_config = FlextApiModels.ClientConfig(
                base_url=base_url or config.base_url,
                timeout=timeout if timeout is not None else config.timeout,
                max_retries=max_retries
                if max_retries is not None
                else config.max_retries,
                headers=headers if headers is not None else config.headers,
                auth_token=auth_token if auth_token is not None else config.auth_token,
                api_key=api_key if api_key is not None else config.api_key,
            )
        elif isinstance(config, FlextApiConfig):
            # FlextApiConfig provided - extract relevant fields
            base_url, timeout, max_retries, headers, auth_token, api_key = (
                self._extract_client_config_params(kwargs)
            )
            self._client_config = FlextApiModels.ClientConfig(
                base_url=base_url or config.api_base_url,
                timeout=timeout if timeout is not None else config.api_timeout,
                max_retries=max_retries
                if max_retries is not None
                else config.max_retries,
                headers=headers if headers is not None else {},
                auth_token=auth_token,
                api_key=api_key,
            )
        else:
            # Handle arbitrary config objects or None
            base_url, timeout, max_retries, headers, auth_token, api_key = (
                self._extract_client_config_params(kwargs)
            )

            # Try to extract api_base_url from config object if it exists
            config_base_url = None
            if config is not None and hasattr(config, "api_base_url"):
                config_base_url = getattr(config, "api_base_url")
            elif config is not None and hasattr(config, "base_url"):
                config_base_url = getattr(config, "base_url")

            self._client_config = FlextApiModels.ClientConfig(
                base_url=base_url if base_url is not None else (config_base_url if config_base_url is not None else FlextApiConstants.DEFAULT_BASE_URL),
                timeout=timeout
                if timeout is not None
                else FlextApiConstants.DEFAULT_TIMEOUT,
                max_retries=max_retries
                if max_retries is not None
                else FlextApiConstants.DEFAULT_RETRIES,
                headers=headers if headers is not None else {},
                auth_token=auth_token,
                api_key=api_key,
            )

        # Store minimal state - everything comes from config
        self._connection_manager = self._ConnectionManager(
            self._client_config.base_url, self._client_config.timeout
        )

        # Simple metrics tracking
        self._request_count = 0
        self._error_count = 0

    @property
    def service_name(self) -> str:
        """Get service name for compatibility."""
        return "flext-api"

    @property
    def service_version(self) -> str:
        """Get service version for compatibility."""
        return "0.9.0"

    @staticmethod
    def create_flext_api_app(**kwargs: object) -> object:
        """Create FastAPI app for compatibility."""
        return create_flext_api(dict(kwargs))

    def _extract_client_config_params(
        self, kwargs: dict[str, object]
    ) -> tuple[
        str | None,
        float | None,
        int | None,
        dict[str, str] | None,
        str | None,
        str | None,
    ]:
        """Extract and convert ClientConfig parameters from kwargs.

        Returns:
            Tuple of (base_url, timeout, max_retries, headers, auth_token, api_key)

        """
        base_url: str | None = None
        timeout: float | None = None
        max_retries: int | None = None
        headers: dict[str, str] | None = None
        auth_token: str | None = None
        api_key: str | None = None

        for key, value in kwargs.items():
            if key == "base_url" and isinstance(value, str):
                base_url = value
            elif key == "timeout" and isinstance(value, (int, float)):
                timeout = float(value)
            elif key == "max_retries" and isinstance(value, int):
                max_retries = value
            elif key == "headers" and isinstance(value, dict):
                headers = {k: str(v) for k, v in value.items()}
            elif key == "auth_token" and (isinstance(value, str) or value is None):
                auth_token = value
            elif key == "api_key" and (isinstance(value, str) or value is None):
                api_key = value

        return base_url, timeout, max_retries, headers, auth_token, api_key

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
        """Execute the main domain service operation.

        Returns a lightweight diagnostic dictionary to align with tests.
        """
        try:
            info: FlextTypes.Core.Dict = {
                "client_type": "httpx.AsyncClient",
                "base_url": self._client_config.base_url,
                "timeout": self._client_config.timeout,
                "session_started": self._connection_manager.client is not None,
                "status": "active",
            }
            return FlextResult[object].ok(info)
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
        started = self._connection_manager.client is not None
        return {
            "status": "healthy" if started else "stopped",
            "base_url": self._client_config.base_url,
            "timeout": self._client_config.timeout,
            "max_retries": self._client_config.max_retries,
            "request_count": self._request_count,
            "error_count": self._error_count,
            "client_ready": started,
            "session_started": started,
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

    @classmethod
    def create_client(
        cls,
        config: FlextApiModels.ClientConfig
        | FlextApiConfig
        | Mapping[str, object]
        | str
        | None = None,
        **kwargs: object,
    ) -> FlextResult[FlextApiClient]:
        """Create FlextApiClient instance with the given configuration.

        Args:
            config: Client configuration or base URL
            **kwargs: Additional configuration overrides

        Returns:
            FlextResult containing FlextApiClient instance

        """
        try:
            if isinstance(config, dict):
                cfg_obj = FlextApiModels.ClientConfig.model_validate(config)
                client = cls(config=cfg_obj, **kwargs)
            elif (
                config is not None
                and hasattr(config, "keys")
                and hasattr(config, "__getitem__")
            ):
                # Convert mapping-like object to dict
                if isinstance(config, Mapping):
                    cfg_dict = dict(config.items())
                    cfg_obj = FlextApiModels.ClientConfig.model_validate(cfg_dict)
                    client = cls(config=cfg_obj, **kwargs)
                else:
                    client = cls(config=config, **kwargs)
            else:
                client = cls(config=config, **kwargs)
            return FlextResult["FlextApiClient"].ok(client)
        except Exception as e:
            return FlextResult["FlextApiClient"].fail(f"Client creation failed: {e}")

    @classmethod
    def create_flext_api_app_with_settings(cls) -> FlextResult[object]:
        """Create a FlextAPI app with default settings."""
        try:
            app_config = FlextApiModels.AppConfig(
                title="FlextAPI App",
                app_version="1.0.0",
                description="FlextAPI application with default settings",
            )

            app = create_fastapi_app(app_config)
            return FlextResult[object].ok(app)
        except Exception as e:
            return FlextResult[object].fail(f"Failed to create FlextAPI app: {e}")


# Factory
def create_flext_api(
    config_dict: Mapping[str, object] | None = None,
) -> FlextApiClient:
    """Create and return a new FlextApiClient instance.

    Args:
        config_dict: Optional configuration dictionary

    Returns:
        FlextApiClient: A configured HTTP client instance.

    """
    if config_dict is None:
        client_config = FlextApiModels.ClientConfig(base_url="https://api.example.com")
        return FlextApiClient(config=client_config)

    # Create config with provided base_url
    base_url = config_dict.get("base_url", FlextApiConstants.DEFAULT_BASE_URL)
    timeout = config_dict.get("timeout", FlextApiConstants.DEFAULT_TIMEOUT)
    max_retries = config_dict.get("max_retries", FlextApiConstants.DEFAULT_RETRIES)
    headers = config_dict.get("headers", {})

    # Type-safe conversion with proper checks
    base_url_str = (
        str(base_url) if base_url is not None else FlextApiConstants.DEFAULT_BASE_URL
    )
    timeout_val = (
        float(timeout)
        if isinstance(timeout, (int, float))
        else FlextApiConstants.DEFAULT_TIMEOUT
    )
    max_retries_val = (
        int(max_retries)
        if isinstance(max_retries, int)
        else FlextApiConstants.DEFAULT_RETRIES
    )
    headers_dict = dict(headers) if isinstance(headers, dict) else {}

    # Create client config that matches the provided settings
    client_config = FlextApiModels.ClientConfig(
        base_url=base_url_str,
        timeout=timeout_val,
        max_retries=max_retries_val,
        headers=headers_dict,
    )

    return FlextApiClient(config=client_config)


__all__ = [
    "FlextApiClient",
    "create_flext_api",
]
