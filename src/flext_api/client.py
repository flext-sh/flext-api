"""FLEXT API Client - HTTP client using flext-core foundation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator, Mapping
from contextlib import asynccontextmanager
from typing import Protocol

import httpx
from flext_core import FlextResult, FlextTypes

from flext_api.config import FlextApiConfig
from flext_api.constants import FlextApiConstants
from flext_api.models import FlextApiModels
from flext_api.protocol_impls.graphql import (
    GraphQLProtocolPlugin,
)
from flext_api.protocol_impls.http import (
    HttpProtocolPlugin,
)
from flext_api.protocol_impls.websocket import (
    WebSocketProtocolPlugin,
)
from flext_api.protocols import FlextApiProtocols
from flext_api.registry import FlextApiRegistry
from flext_api.typings import FlextApiTypes


class LifecycleError(Exception):
    """Exception raised for lifecycle management errors."""


class ResourceProtocol(Protocol):
    """Protocol for resources that can be managed by lifecycle manager."""

    def close(self) -> None:
        """Close the resource synchronously."""
        ...

    async def aclose(self) -> None:
        """Close the resource asynchronously."""
        ...

    def cleanup(self) -> None:
        """Cleanup the resource synchronously."""
        ...


class FlextApiClient:
    """Unified HTTP client orchestrator providing enterprise-grade HTTP operations.

    The FlextApiClient serves as the foundation HTTP client for the entire FLEXT
    providing comprehensive HTTP operations, connection management, and error handling
    through the FlextResult railway pattern. This is the MANDATORY HTTP client for all
    FLEXT projects - NO custom HTTP implementations allowed.
    """

    class ConfigurationManager:
        """Configuration management for FlextApiClient."""

        def __init__(self) -> None:
            """Initialize configuration manager."""
            self._config: FlextApiConfig | None = None

        def configure(
            self, config: FlextApiConfig | dict[str, object] | None = None
        ) -> FlextResult[None]:
            """Configure the HTTP client."""
            try:
                if config is None:
                    self._config = FlextApiConfig()
                elif isinstance(config, dict):
                    # Type-safe configuration - convert dict values to appropriate types
                    config_dict = {}
                    for key, value in config.items():
                        if key == "timeout" and isinstance(value, str):
                            try:
                                config_dict[key] = int(value)
                            except ValueError:
                                config_dict[key] = FlextApiConstants.DEFAULT_TIMEOUT
                        elif key == "max_retries" and isinstance(value, str):
                            try:
                                config_dict[key] = int(value)
                            except ValueError:
                                config_dict[key] = FlextApiConstants.DEFAULT_MAX_RETRIES
                        elif key in {
                            "log_requests",
                            "log_responses",
                            "json_output",
                            "include_source",
                        }:
                            config_dict[key] = (
                                bool(value)
                                if isinstance(value, (str, int, float))
                                else value
                            )
                        else:
                            config_dict[key] = value
                    self._config = FlextApiConfig(**config_dict)
                elif isinstance(config, FlextApiConfig):
                    self._config = config
                else:
                    return FlextResult[None].fail(
                        f"Invalid configuration type: {type(config)}"
                    )

                return self._validate_configuration()
            except Exception as e:
                return FlextResult[None].fail(f"Configuration failed: {e}")

        def _validate_configuration(self) -> FlextResult[None]:
            """Validate current configuration."""
            if self._config is None:
                return FlextResult[None].fail("No configuration set")

            if self._config.api_timeout <= 0:
                return FlextResult[None].fail("Timeout must be positive")

            if self._config.max_retries < 0:
                return FlextResult[None].fail("Max retries cannot be negative")

            return FlextResult[None].ok(None)

        def get_client_config(self) -> FlextResult[FlextApiModels.ClientConfig]:
            """Get client configuration."""
            if self._config is None:
                return FlextResult[FlextApiModels.ClientConfig].fail(
                    "No configuration set"
                )

            return FlextResult[FlextApiModels.ClientConfig].ok(
                FlextApiModels.ClientConfig(
                    base_url=self._config.base_url
                    or FlextApiConstants.DEFAULT_BASE_URL,
                    timeout=self._config.api_timeout,
                    headers=self._config.get_default_headers()
                    if hasattr(self._config, "get_default_headers")
                    else {},
                )
            )

    class HttpOperations:
        """HTTP operation methods extracted from FlextApiClient."""

        def get(
            self,
            url: str,
            *,
            params: FlextTypes.Dict | None = None,
            headers: FlextTypes.Dict | None = None,
            timeout: float | None = None,
            **kwargs: object,
        ) -> FlextResult[FlextApiTypes.JsonValue]:
            """Perform HTTP GET request.

            Args:
                url: Request URL path or full URL
                params: Query parameters
                headers: Additional headers
                timeout: Request timeout in seconds
                **kwargs: Additional request options

            Returns:
                FlextResult containing response data or error

            """
            return self._execute_request(
                "GET",
                url,
                params=params,
                headers=headers,
                timeout=timeout,
                **kwargs,
            )

        def post(
            self,
            url: str,
            data: FlextApiTypes.JsonValue | None = None,
            *,
            json: FlextApiTypes.JsonValue | None = None,
            params: FlextTypes.Dict | None = None,
            headers: FlextTypes.Dict | None = None,
            timeout: float | None = None,
            **kwargs: object,
        ) -> FlextResult[FlextApiTypes.JsonValue]:
            """Perform HTTP POST request.

            Args:
                url: Request URL path or full URL
                data: Request body data
                json: JSON data to send
                params: Query parameters
                headers: Additional headers
                timeout: Request timeout in seconds
                **kwargs: Additional request options

            Returns:
                FlextResult containing response data or error

            """
            if json is not None:
                data = json

            return self._execute_request(
                "POST",
                url,
                data=data,
                params=params,
                headers=headers,
                timeout=timeout,
                **kwargs,
            )

        def put(
            self,
            url: str,
            data: FlextApiTypes.JsonValue | None = None,
            *,
            json: FlextApiTypes.JsonValue | None = None,
            params: FlextTypes.Dict | None = None,
            headers: FlextTypes.Dict | None = None,
            timeout: float | None = None,
            **kwargs: object,
        ) -> FlextResult[FlextApiTypes.JsonValue]:
            """Perform HTTP PUT request.

            Args:
                url: Request URL path or full URL
                data: Request body data
                json: JSON data to send
                params: Query parameters
                headers: Additional headers
                timeout: Request timeout in seconds
                **kwargs: Additional request options

            Returns:
                FlextResult containing response data or error

            """
            if json is not None:
                data = json

            return self._execute_request(
                "PUT",
                url,
                data=data,
                params=params,
                headers=headers,
                timeout=timeout,
                **kwargs,
            )

        def patch(
            self,
            url: str,
            data: FlextApiTypes.JsonValue | None = None,
            *,
            json: FlextApiTypes.JsonValue | None = None,
            params: FlextTypes.Dict | None = None,
            headers: FlextTypes.Dict | None = None,
            timeout: float | None = None,
            **kwargs: object,
        ) -> FlextResult[FlextApiTypes.JsonValue]:
            """Perform HTTP PATCH request.

            Args:
                url: Request URL path or full URL
                data: Request body data
                json: JSON data to send
                params: Query parameters
                headers: Additional headers
                timeout: Request timeout in seconds
                **kwargs: Additional request options

            Returns:
                FlextResult containing response data or error

            """
            if json is not None:
                data = json

            return self._execute_request(
                "PATCH",
                url,
                data=data,
                params=params,
                headers=headers,
                timeout=timeout,
                **kwargs,
            )

        def delete(
            self,
            url: str,
            *,
            params: FlextTypes.Dict | None = None,
            headers: FlextTypes.Dict | None = None,
            timeout: float | None = None,
            **kwargs: object,
        ) -> FlextResult[FlextApiTypes.JsonValue]:
            """Perform HTTP DELETE request.

            Args:
                url: Request URL path or full URL
                params: Query parameters
                headers: Additional headers
                timeout: Request timeout in seconds
                **kwargs: Additional request options

            Returns:
                FlextResult containing response data or error

            """
            return self._execute_request(
                "DELETE",
                url,
                params=params,
                headers=headers,
                timeout=timeout,
                **kwargs,
            )

        def head(
            self,
            url: str,
            *,
            params: FlextTypes.Dict | None = None,
            headers: FlextTypes.Dict | None = None,
            timeout: float | None = None,
            **kwargs: object,
        ) -> FlextResult[FlextApiTypes.JsonValue]:
            """Perform HTTP HEAD request.

            Args:
                url: Request URL path or full URL
                params: Query parameters
                headers: Additional headers
                timeout: Request timeout in seconds
                **kwargs: Additional request options

            Returns:
                FlextResult containing response headers or error

            """
            return self._execute_request(
                "HEAD",
                url,
                params=params,
                headers=headers,
                timeout=timeout,
                **kwargs,
            )

        def options(
            self,
            url: str,
            *,
            params: FlextTypes.Dict | None = None,
            headers: FlextTypes.Dict | None = None,
            timeout: float | None = None,
            **kwargs: object,
        ) -> FlextResult[FlextApiTypes.JsonValue]:
            """Perform HTTP OPTIONS request.

            Args:
                url: Request URL path or full URL
                params: Query parameters
                headers: Additional headers
                timeout: Request timeout in seconds
                **kwargs: Additional request options

            Returns:
                FlextResult containing allowed methods or error

            """
            return self._execute_request(
                "OPTIONS",
                url,
                params=params,
                headers=headers,
                timeout=timeout,
                **kwargs,
            )

        def request(
            self,
            method: str,
            url: str,
            *,
            data: FlextApiTypes.JsonValue | None = None,
            json: FlextApiTypes.JsonValue | None = None,
            params: FlextTypes.Dict | None = None,
            headers: FlextTypes.Dict | None = None,
            timeout: float | None = None,
            **kwargs: object,
        ) -> FlextResult[FlextApiTypes.JsonValue]:
            """Perform generic HTTP request.

            Args:
                method: HTTP method (GET, POST, PUT, DELETE, etc.)
                url: Request URL path or full URL
                data: Request body data
                json: JSON data to send
                params: Query parameters
                headers: Additional headers
                timeout: Request timeout in seconds
                **kwargs: Additional request options

            Returns:
                FlextResult containing response data or error

            """
            if json is not None:
                data = json

            return self._execute_request(
                method,
                url,
                data=data,
                params=params,
                headers=headers,
                timeout=timeout,
                **kwargs,
            )

        def _execute_request(
            self,
            method: str,
            url: str,
            *,
            data: FlextApiTypes.JsonValue | None = None,
            params: FlextTypes.Dict | None = None,
            headers: FlextTypes.Dict | None = None,
            timeout: float | None = None,
            **kwargs: object,
        ) -> FlextResult[FlextApiTypes.JsonValue]:
            """Execute HTTP request (implemented by main client).

            This method should be implemented by the client class that inherits from HttpOperations.
            """
            # This will be implemented by the FlextApiClient class
            msg = "HTTP request execution must be implemented by client"
            raise NotImplementedError(msg)

    class LifecycleManager:
        """Lifecycle management for FlextApiClient initialization and cleanup."""

        def __init__(self) -> None:
            """Initialize lifecycle manager."""
            self._logger = logging.getLogger(__name__)
            self._initialized = False
            self._registry: FlextApiRegistry | None = None
            self._protocols: FlextApiProtocols | None = None
            self._resources: list[ResourceProtocol | object] = []

        @property
        def initialized(self) -> bool:
            """Check if lifecycle manager is initialized."""
            return self._initialized

        @property
        def registry(self) -> FlextApiRegistry | None:
            """Get the protocol registry."""
            return self._registry

        @property
        def protocols(self) -> FlextApiProtocols | None:
            """Get the protocols interface."""
            return self._protocols

        async def initialize(
            self, config: dict[str, object] | None = None
        ) -> FlextResult[None]:
            """Initialize the client lifecycle.

            Args:
                config: Optional initialization configuration

            Returns:
                FlextResult indicating success or failure

            """
            try:
                if self._initialized:
                    return FlextResult[None].ok(None)  # Already initialized

                # Initialize registry
                self._registry = FlextApiRegistry()
                await self._initialize_registry()

                # Initialize protocols
                self._protocols = FlextApiProtocols()
                await self._initialize_protocols()

                # Initialize other resources
                await self._initialize_resources(config)

                self._initialized = True
                return FlextResult[None].ok(None)

            except Exception as e:
                await self._cleanup_resources()
                return FlextResult[None].fail(f"Initialization failed: {e}")

        async def _initialize_registry(self) -> None:
            """Initialize the protocol registry."""
            if self._registry is None:
                return

            # Register core protocols
            try:
                # Register HTTP protocol
                if HttpProtocolPlugin is not None:
                    self._registry.register_protocol("http", HttpProtocolPlugin())

                # Try to register other protocols if available
                if GraphQLProtocolPlugin is not None:
                    try:
                        self._registry.register_protocol(
                            "graphql", GraphQLProtocolPlugin()
                        )
                    except (ImportError, AttributeError) as e:
                        self._logger.debug("GraphQL protocol not available: %s", e)

                if WebSocketProtocolPlugin is not None:
                    try:
                        self._registry.register_protocol(
                            "websocket", WebSocketProtocolPlugin()
                        )
                    except (ImportError, AttributeError) as e:
                        self._logger.debug("WebSocket protocol not available: %s", e)

            except Exception as e:
                # Continue without optional protocols
                self._logger.warning("Failed to initialize optional protocols: %s", e)

        async def _initialize_protocols(self) -> None:
            """Initialize protocol interfaces."""
            # Protocol interfaces are initialized on-demand

        async def _initialize_resources(
            self, config: dict[str, object] | None = None
        ) -> None:
            """Initialize additional resources."""
            # Initialize any additional resources needed

        async def shutdown(self) -> FlextResult[None]:
            """Shutdown the client lifecycle and cleanup resources.

            Returns:
                FlextResult indicating success or failure

            """
            try:
                if not self._initialized:
                    return FlextResult[None].ok(None)  # Not initialized

                # Cleanup resources
                await self._cleanup_resources()

                # Reset state
                self._registry = None
                self._protocols = None
                self._resources.clear()
                self._initialized = False

                return FlextResult[None].ok(None)

            except Exception as e:
                return FlextResult[None].fail(f"Shutdown failed: {e}")

        async def _cleanup_resources(self) -> None:
            """Cleanup all managed resources."""
            for resource in self._resources:
                try:
                    if hasattr(resource, "close"):
                        if asyncio.iscoroutinefunction(resource.close):
                            await resource.close()
                        else:
                            resource.close()
                    elif hasattr(resource, "cleanup"):
                        if asyncio.iscoroutinefunction(resource.cleanup):
                            await resource.cleanup()
                        else:
                            resource.cleanup()
                except Exception as e:
                    # Continue cleanup even if one resource fails
                    self._logger.warning("Failed to cleanup resource: %s", e)

            self._resources.clear()

        def add_resource(self, resource: ResourceProtocol | object) -> None:
            """Add a resource to be managed by the lifecycle.

            Args:
                resource: Resource with close() or cleanup() method

            """
            self._resources.append(resource)

        def remove_resource(self, resource: ResourceProtocol | object) -> None:
            """Remove a resource from lifecycle management.

            Args:
                resource: Resource to remove

            """
            if resource in self._resources:
                self._resources.remove(resource)

        @asynccontextmanager
        async def lifecycle_context(
            self, config: dict[str, object] | None = None
        ) -> AsyncIterator[FlextApiClient.LifecycleManager]:
            """Context manager for lifecycle management.

            Args:
                config: Optional initialization configuration

            Yields:
                LifecycleManager instance

            Raises:
                LifecycleError: If initialization fails

            """
            init_result = await self.initialize(config)
            if init_result.is_failure:
                msg = f"Failed to initialize lifecycle: {init_result.error}"
                raise LifecycleError(msg)

            try:
                yield self
            finally:
                shutdown_result = await self.shutdown()
                if shutdown_result.is_failure:
                    # Log error but don't raise to avoid masking original exceptions
                    pass

        def get_status(self) -> dict[str, object]:
            """Get lifecycle status for monitoring."""
            return {
                "initialized": self._initialized,
                "registry_available": self._registry is not None,
                "protocols_available": self._protocols is not None,
                "managed_resources": len(self._resources),
                "registry_protocols": (
                    getattr(self._registry, "list_protocols", list)()
                    if self._registry
                    else []
                ),
            }

        def health_check(self) -> FlextResult[bool]:
            """Perform health check on lifecycle components.

            Returns:
                FlextResult with health status

            """
            try:
                if not self._initialized:
                    return FlextResult[bool].fail("Lifecycle not initialized")

                # Check registry
                if self._registry is None:
                    return FlextResult[bool].fail("Registry not available")

                # Check protocols
                if self._protocols is None:
                    return FlextResult[bool].fail("Protocols not available")

                # Check resources
                unhealthy_resources = []
                for i, resource in enumerate(self._resources):
                    if hasattr(resource, "health_check"):
                        if asyncio.iscoroutinefunction(resource.health_check):
                            # For async health checks, assume healthy for now
                            pass
                        else:
                            try:
                                health = resource.health_check()
                                if not health:
                                    unhealthy_resources.append(f"resource_{i}")
                            except Exception as e:
                                unhealthy_resources.append(f"resource_{i}: {e}")

                if unhealthy_resources:
                    return FlextResult[bool].fail(
                        f"Unhealthy resources: {unhealthy_resources}"
                    )

                return FlextResult[bool].ok(True)

            except Exception as e:
                return FlextResult[bool].fail(f"Health check failed: {e}")

    def __init__(
        self,
        *,
        base_url: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> None:
        """Initialize FlextApiClient with configuration."""
        self._config_manager = self.ConfigurationManager()
        self._config_manager.configure({
            "base_url": base_url,
            "timeout": timeout,
            "max_retries": max_retries,
            "headers": dict[str, object](headers) if headers else {},
        })

    def request(
        self, request: FlextApiModels.HttpRequest
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Execute HTTP request."""
        config_result = self._config_manager.get_client_config()
        if config_result.is_failure:
            return FlextResult[FlextApiModels.HttpResponse].fail(config_result.error)

        try:
            with httpx.Client(timeout=config_result.unwrap().api_timeout) as client:
                # Handle request body properly for httpx
                content = None
                if request.body is not None:
                    if isinstance(request.body, bytes):
                        content = request.body
                    elif isinstance(request.body, str):
                        content = request.body.encode("utf-8")
                    else:
                        # Convert other types to string
                        content = str(request.body).encode("utf-8")

                response = client.request(
                    method=request.method,
                    url=f"{config_result.unwrap().base_url}{request.url}",
                    headers=request.headers,
                    content=content,
                )
                return FlextResult[FlextApiModels.HttpResponse].ok(
                    FlextApiModels.HttpResponse(
                        status_code=response.status_code,
                        headers=dict(response.headers),
                        body=response.content,
                    )
                )
        except Exception as e:
            return FlextResult[FlextApiModels.HttpResponse].fail(str(e))
