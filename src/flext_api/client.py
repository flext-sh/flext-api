"""FLEXT API Client - HTTP client using flext-core foundation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Self

import httpx
from pydantic import ConfigDict
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from flext_api.app import FlextApiApp
from flext_api.config import FlextApiConfig
from flext_api.constants import FlextApiConstants
from flext_api.models import FlextApiModels
from flext_core import (
    FlextContainer,
    FlextDomainService,
    FlextLogger,
    FlextResult,
    FlextTypes,
)

# Avoiding circular import - import inside method when needed


class FlextApiClient(FlextDomainService[object]):
    """Unified HTTP client using flext-core foundation with zero duplication.

    This client provides a streamlined HTTP interface using flext-core patterns
    and httpx for async HTTP operations. It follows SOLID principles with
    single responsibility for HTTP requests and extensibility through composition.

    The client supports:
    - Async HTTP operations (GET, POST, PUT, DELETE)
    - Automatic retry logic with exponential backoff
    - Flexible configuration through multiple input types
    - Context manager support for resource management
    - Health monitoring and metrics tracking

    Attributes:
        base_url: The base URL for all HTTP requests.
        timeout: Request timeout in seconds.
        max_retries: Maximum number of retry attempts.
        config: Complete client configuration object.

    Example:
        >>> client = FlextApiClient("https://api.example.com")
        >>> async with client:
        ...     response = await client.get("/users")
        ...     if response.is_success:
        ...         data = response.unwrap()
        ...         print(f"Status: {data.status_code}")

    """

    # Override frozen behavior for FlextApiClient to allow nested class assignment
    model_config = ConfigDict(
        frozen=False,  # Allow attribute assignment for nested classes
        validate_assignment=True,
        extra="forbid",
        arbitrary_types_allowed=True,
    )

    def __init__(
        self,
        config: FlextApiModels.ClientConfig
        | FlextApiConfig
        | Mapping[str, str | int | float | bool | dict[str, str] | None]
        | str
        | None = None,
        **kwargs: str | float | bool | dict[str, str] | None,
    ) -> None:
        """Initialize HTTP client with streamlined configuration.

        Creates a new HTTP client instance with the provided configuration.
        Supports multiple configuration input types for flexibility.

        Args:
            config: Client configuration in one of the following formats:
                - FlextApiModels.ClientConfig: Complete configuration object
                - FlextApiConfig: FLEXT API configuration object
                - Mapping[str, object]: Dictionary-like configuration
                - str: Base URL string for simple setup
                - None: Use default configuration
            **kwargs: Configuration overrides including:
                - base_url: Base URL for requests
                - timeout: Request timeout in seconds
                - max_retries: Maximum retry attempts
                - headers: Default headers dictionary
                - auth_token: Authentication token
                - api_key: API key for authentication

        Example:
            >>> # Simple base URL
            >>> client = FlextApiClient("https://api.example.com")
            >>>
            >>> # With overrides
            >>> client = FlextApiClient(
            ...     "https://api.example.com",
            ...     timeout=30.0,
            ...     max_retries=3,
            ...     headers={"User-Agent": "MyApp/1.0"},
            ... )

        """
        super().__init__()

        # Use flext-core container and logger
        self._container = FlextContainer.get_global()
        self._logger = FlextLogger(__name__)

        # Type annotation for proper Pyright inference
        self._client_config: FlextApiModels.ClientConfig

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
            # Handle arbitrary config objects or None (including Mapping types)
            base_url, timeout, max_retries, headers, auth_token, api_key = (
                self._extract_client_config_params(kwargs)
            )

            # Explicit config extraction - FLEXT pattern with clear type handling
            config_base_url: str | None = None
            if config is not None:
                # Check for dictionary-like access (Mapping types) - explicit checking
                if hasattr(config, "get") and callable(getattr(config, "get", None)):
                    raw_base_url = config.get("api_base_url") or config.get("base_url")
                    if raw_base_url is not None:
                        config_base_url = str(raw_base_url)

                # If no dictionary access, try attribute access (for object types)
                if config_base_url is None:
                    if hasattr(config, "api_base_url"):
                        raw_attr = getattr(config, "api_base_url", None)
                        if raw_attr is not None:
                            config_base_url = str(raw_attr)
                    elif hasattr(config, "base_url"):
                        raw_attr = getattr(config, "base_url", None)
                        if raw_attr is not None:
                            config_base_url = str(raw_attr)

            # Ensure base_url is a string for ClientConfig - explicit type conversion
            final_base_url: str
            if base_url is not None and isinstance(base_url, str):
                final_base_url = base_url
            elif config_base_url is not None:
                final_base_url = config_base_url
            else:
                final_base_url = FlextApiConstants.DEFAULT_BASE_URL

            self._client_config = FlextApiModels.ClientConfig(
                base_url=final_base_url,
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
            self._client_config.base_url,
            self._client_config.timeout,
        )

        # Simple metrics tracking
        self._request_count = 0
        self._error_count = 0

        # Initialize nested classes for organized functionality
        self.http = self._HttpOperations(self)
        self.lifecycle = self._LifecycleManager(self)
        self.config = self._ConfigurationManager(self)

    # Compatibility properties removed - use direct values

    class _HttpOperations:
        """Nested class for HTTP operations - reduces public method count."""

        def __init__(self, client: FlextApiClient) -> None:
            self._client = client

        async def request(
            self,
            method: str,
            url: str,
            **kwargs: str | float | bool | dict[str, str] | None,
        ) -> FlextResult[FlextApiModels.HttpResponse]:
            """Make HTTP request with specified method.

            Performs an HTTP request with the specified method and returns
            the response wrapped in a FlextResult.

            Args:
                method: HTTP method (GET, POST, PUT, DELETE, etc.).
                url: URL endpoint to request (relative to base_url if not absolute).
                **kwargs: Additional request parameters:
                    - params: Query parameters dictionary
                    - headers: Additional headers dictionary
                    - json: JSON data to send
                    - data: Form data to send
                    - files: File upload data
                    - timeout: Override default timeout

            Returns:
                FlextResult containing HttpResponse or error details.

            Example:
                >>> response = await client.http.request(
                ...     "GET", "/users", params={"page": 1}
                ... )
                >>> if response.is_success:
                ...     data = response.unwrap()
                ...     print(f"Status: {data.status_code}")

            """
            return await self._client.make_request(method, url, **kwargs)

        async def get(
            self,
            url: str,
            **kwargs: str | float | bool | dict[str, str] | None,
        ) -> FlextResult[FlextApiModels.HttpResponse]:
            """Make GET request.

            Performs a GET request to the specified URL with optional parameters.

            Args:
                url: URL endpoint to request (relative to base_url if not absolute).
                **kwargs: Additional request parameters (params, headers, timeout).

            Returns:
                FlextResult containing HttpResponse or error details.

            Example:
                >>> response = await client.http.get("/users", params={"page": 1})
                >>> if response.is_success:
                ...     users = response.unwrap().data

            """
            return await self.request("GET", url, **kwargs)

        async def post(
            self,
            url: str,
            **kwargs: str | float | bool | dict[str, str] | None,
        ) -> FlextResult[FlextApiModels.HttpResponse]:
            """Make POST request.

            Performs a POST request to the specified URL with optional data.

            Args:
                url: URL endpoint to request (relative to base_url if not absolute).
                **kwargs: Additional request parameters (json, data, headers, timeout).

            Returns:
                FlextResult containing HttpResponse or error details.

            Example:
                >>> response = await client.http.post("/users", json={"name": "John"})
                >>> if response.is_success:
                ...     user = response.unwrap().data

            """
            return await self.request("POST", url, **kwargs)

        async def put(
            self,
            url: str,
            **kwargs: str | float | bool | dict[str, str] | None,
        ) -> FlextResult[FlextApiModels.HttpResponse]:
            """Make PUT request.

            Performs a PUT request to the specified URL with optional data.

            Args:
                url: URL endpoint to request (relative to base_url if not absolute).
                **kwargs: Additional request parameters (json, data, headers, timeout).

            Returns:
                FlextResult containing HttpResponse or error details.

            Example:
                >>> response = await client.http.put("/users/1", json={"name": "Jane"})
                >>> if response.is_success:
                ...     user = response.unwrap().data

            """
            return await self.request("PUT", url, **kwargs)

        async def delete(
            self,
            url: str,
            **kwargs: str | float | bool | dict[str, str] | None,
        ) -> FlextResult[FlextApiModels.HttpResponse]:
            """Make DELETE request.

            Performs a DELETE request to the specified URL.

            Args:
                url: URL endpoint to request (relative to base_url if not absolute).
                **kwargs: Additional request parameters (headers, timeout).

            Returns:
                FlextResult containing HttpResponse or error details.

            Example:
                >>> response = await client.http.delete("/users/1")
                >>> if response.is_success:
                ...     print("User deleted successfully")

            """
            return await self.request("DELETE", url, **kwargs)

    class _LifecycleManager:
        """Nested class for lifecycle management - reduces public method count."""

        def __init__(self, client: FlextApiClient) -> None:
            self._client = client

        async def start(self) -> FlextResult[None]:
            """Start the HTTP client.

            Initializes the underlying HTTP client and prepares it for requests.
            This method should be called before making any HTTP requests.

            Returns:
                FlextResult indicating success or failure.

            Example:
                >>> result = await client.lifecycle.start()
                >>> if result.is_success:
                ...     print("Client started successfully")

            """
            return await self._client.start_client()

        async def stop(self) -> FlextResult[None]:
            """Stop the HTTP client.

            Closes the underlying HTTP client and cleans up resources.
            This method should be called when the client is no longer needed.

            Returns:
                FlextResult indicating success or failure.

            Example:
                >>> result = await client.lifecycle.stop()
                >>> if result.is_success:
                ...     print("Client stopped successfully")

            """
            return await self._client.stop_client()

        async def close(self) -> FlextResult[None]:
            """Close the HTTP client.

            Alias for stop() method for context manager compatibility.

            Returns:
                FlextResult indicating success or failure.

            """
            return await self.stop()

    class _ConfigurationManager:
        """Nested class for configuration management - reduces public method count."""

        def __init__(self, client: FlextApiClient) -> None:
            self._client = client

        def configure(self, config: dict[str, object]) -> FlextResult[None]:
            """Configure the client with new settings.

            Updates the client configuration with the provided settings.
            This method allows runtime configuration changes.

            Args:
                config: Dictionary containing configuration updates.

            Returns:
                FlextResult indicating success or failure.

            Example:
                >>> result = client.config.configure({"timeout": 60.0})
                >>> if result.is_success:
                ...     print("Configuration updated")

            """
            return self._client.update_configuration(config)

        def get_config(self) -> dict[str, object]:
            """Get current client configuration.

            Returns the current configuration as a dictionary.

            Returns:
                Dictionary containing current configuration.

            Example:
                >>> config = client.config.get_config()
                >>> print(f"Timeout: {config['timeout']}")

            """
            return self._client.get_configuration_dict()

        def health_check(self) -> FlextTypes.Core.Dict:
            """Perform health check on the client.

            Checks the health status of the HTTP client and returns
            diagnostic information.

            Returns:
                Dictionary containing health check results.

            Example:
                >>> health = client.config.health_check()
                >>> print(f"Status: {health['status']}")

            """
            return self._client.perform_health_check()

    def create_flext_api_app(self, **kwargs: object) -> object:
        """Create FastAPI application with configuration.

        Creates a FastAPI application instance using the provided configuration
        parameters with proper validation and defaults.

        Args:
            **kwargs: Application configuration parameters:
                - title: Application title (default: "FlextAPI")
                - version: Application version (default: "0.9.0")
                - description: Application description (default: "FlextAPI Application")

        Returns:
            FastAPI application instance.

        Example:
            >>> app = client.create_flext_api_app(
            ...     title="My API", version="1.0.0", description="My custom API"
            ... )

        """
        # Extract and validate string parameters
        title = kwargs.get("title", "FlextAPI")
        if not isinstance(title, str):
            title = str(title)

        app_version = kwargs.get("version", "0.9.0")
        if not isinstance(app_version, str):
            app_version = str(app_version)

        description = kwargs.get("description", "FlextAPI Application")
        if not isinstance(description, str):
            description = str(description)

        # Create app configuration with proper field names
        app_config = FlextApiModels.AppConfig(
            title=title,
            app_version=app_version,  # Correct field name
            description=description,
        )

        return FlextApiApp.create_fastapi_app(app_config)

    def _extract_client_config_params(
        self,
        kwargs: Mapping[str, str | int | float | bool | dict[str, str] | None],
    ) -> tuple[
        str | None,
        float | None,
        int | None,
        dict[str, str] | None,
        str | None,
        str | None,
    ]:
        """Extract and convert ClientConfig parameters from kwargs.

        Processes keyword arguments to extract and validate configuration
        parameters for the HTTP client.

        Args:
            kwargs: Dictionary of keyword arguments to process.

        Returns:
            Tuple containing extracted parameters:
                - base_url: Base URL string or None
                - timeout: Timeout value in seconds or None
                - max_retries: Maximum retry count or None
                - headers: Headers dictionary or None
                - auth_token: Authentication token or None
                - api_key: API key or None

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
        """Manages HTTP connections with single responsibility.

        Handles the lifecycle of httpx.AsyncClient instances including
        initialization, connection management, and cleanup.
        """

        def __init__(self, base_url: str, timeout: float) -> None:
            """Initialize connection manager with base URL and timeout.

            Args:
                base_url: Base URL for HTTP requests.
                timeout: Request timeout in seconds.

            """
            self._base_url = base_url
            self._timeout = timeout
            self._client: httpx.AsyncClient | None = None

        async def ensure_client(self) -> httpx.AsyncClient:
            """Ensure HTTP client is initialized and ready.

            Creates a new httpx.AsyncClient if one doesn't exist,
            or returns the existing client.

            Returns:
                Initialized httpx.AsyncClient instance.

            """
            if self._client is None:
                self._client = httpx.AsyncClient(
                    base_url=self._base_url,
                    timeout=self._timeout,
                )
            return self._client

        async def close(self) -> None:
            """Close HTTP client and clean up resources.

            Properly closes the httpx.AsyncClient and sets it to None
            to allow for proper resource cleanup.
            """
            if self._client:
                await self._client.aclose()
                self._client = None

        @property
        def client(self) -> httpx.AsyncClient | None:
            """Get current HTTP client instance.

            Returns:
                Current httpx.AsyncClient instance or None if not initialized.

            """
            return self._client

    # =============================================================================
    # Essential Methods Only
    # =============================================================================

    def _get_headers(self, additional: dict[str, str] | None = None) -> dict[str, str]:
        """Get headers from config with optional additions.

        Combines default headers from configuration with any additional
        headers provided.

        Args:
            additional: Optional additional headers to include.

        Returns:
            Combined headers dictionary.

        """
        headers = self._client_config.get_default_headers()
        if additional:
            headers.update(additional)
        return headers

    # HTTP operations moved to self.http nested class

    # =============================================================================
    # FlextDomainService Implementation
    # =============================================================================

    def execute(self) -> FlextResult[object]:
        """Execute the main domain service operation.

        Returns diagnostic information about the HTTP client state
        including configuration and connection status.

        Returns:
            FlextResult containing client diagnostic information or error details.

        Example:
            >>> result = client.execute()
            >>> if result.is_success:
            ...     info = result.unwrap()
            ...     print(f"Client status: {info['status']}")

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

    # Lifecycle methods moved to self.lifecycle nested class

    # Configuration methods moved to self.config nested class

    # =============================================================================
    # Public API - HTTP Methods
    # =============================================================================

    # HTTP methods moved to self.http nested class

    # =============================================================================
    # Private Methods for Nested Classes
    # =============================================================================

    async def make_request(
        self,
        method: str,
        url: str,
        **kwargs: str | float | bool | dict[str, str] | None,
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Internal method for making HTTP requests.

        Returns:
            FlextResult containing HttpResponse or error details.

        """
        return await self._request(method, url, **kwargs)

    async def start_client(self) -> FlextResult[None]:
        """Internal method for starting the client.

        Returns:
            FlextResult indicating success or failure.

        """
        try:
            await self._connection_manager.ensure_client()
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Failed to start HTTP client: {e}")

    async def stop_client(self) -> FlextResult[None]:
        """Internal method for stopping the client.

        Returns:
            FlextResult indicating success or failure.

        """
        try:
            await self._connection_manager.close()
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Failed to stop HTTP client: {e}")

    def update_configuration(self, config: dict[str, object]) -> FlextResult[None]:
        """Internal method for updating configuration.

        Returns:
            FlextResult indicating success or failure.

        """
        try:
            current_config = self._client_config.model_dump()
            current_config.update(config)
            self._client_config = FlextApiModels.ClientConfig(**current_config)
            self._connection_manager = self._ConnectionManager(
                self._client_config.base_url,
                self._client_config.timeout,
            )
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Configuration failed: {e}")

    def get_configuration_dict(self) -> dict[str, object]:
        """Internal method for getting configuration.

        Returns:
            Dictionary containing current configuration.

        """
        return self._client_config.model_dump()

    def perform_health_check(self) -> FlextTypes.Core.Dict:
        """Internal method for health check.

        Returns:
            Dictionary containing health check information.

        """
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

    # =============================================================================
    # Essential Properties Only
    # =============================================================================

    @property
    def base_url(self) -> str:
        """Get base URL from configuration.

        Returns:
            The configured base URL for HTTP requests.

        """
        return self._client_config.base_url

    @property
    def timeout(self) -> float:
        """Get timeout setting from configuration.

        Returns:
            The configured timeout value in seconds.

        """
        return self._client_config.timeout

    @property
    def max_retries(self) -> int:
        """Get maximum retry count from configuration.

        Returns:
            The configured maximum number of retry attempts.

        """
        return self._client_config.max_retries

    @property
    def config(self) -> FlextApiModels.ClientConfig:
        """Get complete client configuration object.

        Returns:
            The FlextApiModels.ClientConfig object containing all settings.

        """
        return self._client_config

    # =============================================================================
    # Context Manager Support
    # =============================================================================

    async def __aenter__(self) -> Self:
        """Async context manager entry.

        Initializes the HTTP client when entering the context.

        Returns:
            Self for method chaining.

        """
        await self._connection_manager.ensure_client()
        return self

    async def __aexit__(
        self,
        exc_type: object,
        exc_val: object,
        exc_tb: object,
    ) -> None:
        """Async context manager exit.

        Closes the HTTP client when exiting the context.

        Args:
            exc_type: Exception type if an exception occurred.
            exc_val: Exception value if an exception occurred.
            exc_tb: Exception traceback if an exception occurred.

        """
        await self._connection_manager.close()

    async def close(self) -> FlextResult[None]:
        """Close HTTP client and clean up resources.

        Properly closes the HTTP client connection and cleans up
        all associated resources.

        Returns:
            FlextResult indicating success or failure.

        Example:
            >>> result = await client.close()
            >>> if result.is_success:
            ...     print("Client closed successfully")

        """
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
        cls,
        config_data: dict[str, str | int | float | bool | None]
        | FlextApiModels.ClientConfig,
    ) -> FlextResult[FlextApiClient]:
        """Create HTTP client from configuration data.

        Factory method for creating FlextApiClient instances with
        proper configuration validation.

        Args:
            config_data: Configuration data as dictionary or ClientConfig object.

        Returns:
            FlextResult containing FlextApiClient instance or error details.

        Example:
            >>> config = {"base_url": "https://api.example.com", "timeout": 30.0}
            >>> result = FlextApiClient.create(config)
            >>> if result.is_success:
            ...     client = result.unwrap()
            ...     print(f"Created client for: {client.base_url}")

        """
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
        """Build complete URL from base URL and endpoint.

        Combines the base URL with the endpoint, handling absolute
        URLs and proper path joining.

        Args:
            endpoint: Endpoint path or absolute URL.

        Returns:
            Complete URL string.

        Example:
            >>> client._build_url("/users")  # Returns "https://api.example.com/users"
            >>> client._build_url(
            ...     "https://other.com/data"
            ... )  # Returns "https://other.com/data"

        """
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

    class _RetryHelper:
        """Helper class for HTTP retry logic using tenacity.

        Provides retry configuration for HTTP requests with exponential
        backoff and proper exception handling.
        """

        @staticmethod
        def create_retry_config(max_retries: int) -> AsyncRetrying:
            """Create tenacity async retry configuration.

            Creates a retry configuration with exponential backoff
            for HTTP-related exceptions.

            Args:
                max_retries: Maximum number of retry attempts.

            Returns:
                Configured AsyncRetrying instance.

            """
            return AsyncRetrying(
                stop=stop_after_attempt(max_retries),
                wait=wait_exponential(multiplier=1, min=1, max=10),
                retry=retry_if_exception_type(
                    (httpx.HTTPError, httpx.TimeoutException, httpx.ConnectError),
                ),
                reraise=True,
            )

    async def _request(
        self,
        method: str,
        url: str,
        **kwargs: str | float | bool | dict[str, str] | None,
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Make HTTP request using flext-core HttpRequestConfig.

        Internal method that handles the actual HTTP request execution
        with retry logic and proper error handling.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE).
            url: URL endpoint to request.
            **kwargs: Additional request parameters:
                - headers: Additional headers dictionary
                - params: Query parameters dictionary
                - json: JSON data to send
                - data: Form data to send
                - files: File upload data
                - timeout: Override default timeout

        Returns:
            FlextResult containing HttpResponse or error details.

        """
        try:
            # Extract headers safely
            headers_obj = kwargs.get("headers")
            additional_headers = headers_obj if isinstance(headers_obj, dict) else None

            # Use flext-api HttpRequestConfig with streamlined config
            request_config = FlextApiModels.Http.HttpRequestConfig(
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

            # Execute HTTP request with retry logic if configured
            response: httpx.Response | None = None
            if self._client_config.max_retries > 0:
                retry_config = self._RetryHelper.create_retry_config(
                    self._client_config.max_retries,
                )
                async for attempt in retry_config:
                    with attempt:
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
                        break  # Success, exit retry loop
            else:
                # No retry - single attempt
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

            # Ensure response was obtained
            if response is None:
                return FlextResult[FlextApiModels.HttpResponse].fail(
                    "Failed to get response after retry attempts",
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
                f"HTTP request failed: {e}",
            )
        except Exception as e:
            return FlextResult[FlextApiModels.HttpResponse].fail(
                f"Unexpected error: {e}",
            )

    @classmethod
    def create_client(
        cls,
        config: FlextApiModels.ClientConfig
        | FlextApiConfig
        | Mapping[str, str | int | float | bool | None]
        | str
        | None = None,
        **kwargs: str | float | bool | None,
    ) -> FlextResult[FlextApiClient]:
        """Create FlextApiClient instance with the given configuration.

        Factory method for creating FlextApiClient instances with
        flexible configuration input types.

        Args:
            config: Client configuration in various formats:
                - FlextApiModels.ClientConfig: Complete configuration object
                - FlextApiConfig: FLEXT API configuration object
                - Mapping[str, object]: Dictionary-like configuration
                - str: Base URL string
                - None: Use default configuration
            **kwargs: Additional configuration overrides.

        Returns:
            FlextResult containing FlextApiClient instance or error details.

        Example:
            >>> result = FlextApiClient.create_client("https://api.example.com")
            >>> if result.is_success:
            ...     client = result.unwrap()
            ...     print(f"Created client: {client.base_url}")

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
            return FlextResult[FlextApiClient].ok(client)
        except Exception as e:
            return FlextResult[FlextApiClient].fail(f"Client creation failed: {e}")

    @classmethod
    def create_flext_api(
        cls,
        config_dict: Mapping[str, str | int | float | bool | dict[str, str] | None]
        | None = None,
    ) -> FlextApiClient:
        """Create FlextApiClient instances.

        Creates a FlextApiClient with the provided configuration,
        handling type conversion and validation.

        Args:
            config_dict: Optional configuration dictionary containing:
                - base_url: Base URL for requests
                - timeout: Request timeout in seconds
                - max_retries: Maximum retry attempts
                - headers: Default headers dictionary

        Returns:
            FlextApiClient instance with the specified configuration.

        Example:
            >>> client = FlextApiClient.create_flext_api({
            ...     "base_url": "https://api.example.com",
            ...     "timeout": 30.0,
            ...     "max_retries": 3,
            ... })
            >>> print(f"Client base URL: {client.base_url}")

        """
        if config_dict is None:
            # Create with default configuration
            return cls()

        # Create a config dict with proper defaults and type conversion
        processed_config: dict[
            str,
            str | int | float | bool | dict[str, str] | None,
        ] = {}

        # Handle base_url
        base_url = config_dict.get("base_url")
        if base_url is not None:
            if isinstance(base_url, str):
                processed_config["base_url"] = base_url
            else:
                processed_config["base_url"] = str(base_url)

        # Handle timeout with type conversion
        timeout = config_dict.get("timeout")
        if timeout is not None and isinstance(timeout, (int, float)):
            processed_config["timeout"] = float(timeout)
        # Invalid timeout types are ignored, will use defaults

        # Handle max_retries with type conversion
        max_retries = config_dict.get("max_retries")
        if max_retries is not None:
            if isinstance(max_retries, int):
                processed_config["max_retries"] = max_retries
            elif isinstance(max_retries, float):
                processed_config["max_retries"] = int(max_retries)
            # Invalid max_retries types are ignored, will use defaults

        # Handle headers
        headers = config_dict.get("headers")
        if headers is not None and isinstance(headers, dict):
            processed_config["headers"] = headers
            # Invalid headers types are ignored, will use defaults

        # Pass the processed config dict directly to constructor
        return cls(config=processed_config)

    @classmethod
    def create_flext_api_app_with_settings(cls) -> FlextResult[object]:
        """Create a FlextAPI app with default settings.

        Creates a FastAPI application instance with sensible defaults
        for common use cases.

        Returns:
            FlextResult containing FastAPI application instance or error details.

        Example:
            >>> result = FlextApiClient.create_flext_api_app_with_settings()
            >>> if result.is_success:
            ...     app = result.unwrap()
            ...     print("Created FlextAPI app successfully")

        """
        try:
            app_config = FlextApiModels.AppConfig(
                title="FlextAPI App",
                app_version="1.0.0",
                description="FlextAPI application with default settings",
            )

            app = FlextApiApp.create_fastapi_app(app_config)
            return FlextResult[object].ok(app)
        except Exception as e:
            return FlextResult[object].fail(f"Failed to create FlextAPI app: {e}")

    class _Factory:
        """Nested factory class for FLEXT compliance - no loose functions.

        Provides factory methods for creating FlextApiClient instances
        following FLEXT architectural patterns.
        """

        @staticmethod
        def create_flext_api(
            config_dict: Mapping[str, str | int | float | bool | None] | None = None,
        ) -> FlextApiClient:
            """Create FlextApiClient instances.

            Creates a FlextApiClient with the provided configuration,
            handling type conversion and validation.

            Args:
                config_dict: Optional configuration dictionary.

            Returns:
                FlextApiClient instance with the specified configuration.

            """
            return FlextApiClient.create_flext_api(config_dict)


# Removed module-level function alias - use FlextApiClient.create_flext_api() directly
# This follows FLEXT unified class pattern - no loose functions at module level


__all__ = [
    "FlextApiClient",
    # Removed create_flext_api module-level alias - use FlextApiClient.create_flext_api() instead
]
