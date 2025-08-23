"""Base service abstractions for FLEXT API library.

This module defines abstract base services for the FLEXT API library,
extending flext-core base classes and following SOLID principles.
All services implement proper dependency injection and error handling patterns.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Mapping
from typing import TypeVar, cast, override

from flext_core import FlextDomainService, FlextResult, get_logger
from pydantic import Field

from flext_api.client import FlextApiQueryBuilder, FlextApiResponseBuilder
from flext_api.models import ClientConfig
from flext_api.protocols import (
    FlextApiMiddlewareProtocol,
    FlextApiPluginProtocol,
    FlextApiQueryBuilderProtocol,
    FlextApiResponseBuilderProtocol,
)
from flext_api.typings import FlextTypes

logger = get_logger(__name__)
# Note: Protocols are used only for typing; no runtime aliasing required.
# Type variables for generic services
T = TypeVar("T")
TRequest = TypeVar("TRequest")
TResponse = TypeVar("TResponse")

# ==============================================================================
# BASE HTTP SERVICE
# ==============================================================================


class FlextApiBaseService(
    FlextDomainService[dict[str, object]],
    ABC,
):
    """Abstract base service for all API services.

    Extends FlextDomainService with API-specific lifecycle management
    and health checking capabilities. Follows Single Responsibility Principle.
    Implements FlextApiServiceProtocol interface.
    """

    service_name: str = Field(description="Service name for identification")
    service_version: str = Field(default="0.9.0", description="Service version")
    is_running: bool = Field(default=False, description="Service running state")

    async def start(self) -> FlextResult[None]:
        """Start the service with proper initialization."""
        try:
            logger.info("Starting service", service=self.service_name)

            # Validate configuration
            config_result = self.validate_config()
            if not config_result:
                return FlextResult[None].fail(
                    f"Configuration validation failed: {config_result.error}",
                )

            # Perform service-specific startup
            startup_result = await self._do_start()
            if not startup_result:
                return startup_result

            # Update state
            object.__setattr__(self, "is_running", True)

            logger.info("Service started successfully", service=self.service_name)
            return FlextResult[None].ok(None)
        except Exception as e:
            logger.exception("Failed to start service", service=self.service_name)
            return FlextResult[None].fail(f"Service startup failed: {e}")

    async def stop(self) -> FlextResult[None]:
        """Stop the service with proper cleanup."""
        try:
            logger.info("Stopping service", service=self.service_name)

            # Perform service-specific shutdown
            shutdown_result = await self._do_stop()
            if not shutdown_result:
                logger.warning(
                    "Service shutdown had issues",
                    service=self.service_name,
                    error=shutdown_result.error,
                )

            # Update state
            object.__setattr__(self, "is_running", False)

            logger.info("Service stopped", service=self.service_name)
            return FlextResult[None].ok(None)
        except Exception as e:
            logger.exception("Failed to stop service", service=self.service_name)
            return FlextResult[None].fail(f"Service shutdown failed: {e}")

    async def health_check(self) -> FlextResult[dict[str, object]]:
        """Check service health status."""
        try:
            # Basic health info
            health_info: dict[str, object] = {
                "service": self.service_name,
                "version": self.service_version,
                "status": "healthy" if self.is_running else "stopped",
                "is_running": self.is_running,
            }

            # Get service-specific health details using unwrap_or pattern
            details_result = await self._get_health_details()
            if details_result.is_failure:
                return FlextResult[dict[str, object]].fail(
                    details_result.error or "Health details failed"
                )
            health_info.update(details_result.unwrap_or({}))

            return FlextResult[dict[str, object]].ok(health_info)
        except Exception as e:
            logger.exception("Health check failed", service=self.service_name)
            return FlextResult[dict[str, object]].fail(f"Health check failed: {e}")

    @override
    def execute(self) -> FlextResult[dict[str, object]]:
        """Execute service operation (from FlextDomainService)."""
        return FlextResult[dict[str, object]].ok(
            {"service": self.service_name, "status": "executed"}
        )

    @abstractmethod
    async def _do_start(self) -> FlextResult[None]:
        """Perform service-specific startup logic."""

    @abstractmethod
    async def _do_stop(self) -> FlextResult[None]:
        """Perform service-specific shutdown logic."""

    async def _get_health_details(self) -> FlextResult[dict[str, object]]:
        """Get service-specific health details. Override in subclasses."""
        return FlextResult[dict[str, object]].ok({})


# ==============================================================================
# BASE HTTP CLIENT SERVICE
# ==============================================================================


class FlextApiBaseClientService(
    FlextApiBaseService,
    ABC,
):
    """Abstract base service for HTTP client implementations.

    Provides HTTP client functionality with proper error handling,
    retry logic, and plugin support.
    Implements FlextApiClientProtocol interface.
    """

    client_config: ClientConfig = Field(description="Client configuration")
    plugins: list[FlextApiPluginProtocol] = Field(
        default_factory=list[FlextApiPluginProtocol],
        description="Client plugins",
    )

    async def request(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        data: FlextTypes.Core.JsonDict | str | bytes | None = None,
        json: FlextTypes.Core.JsonDict | None = None,
        params: Mapping[str, str] | None = None,
    ) -> FlextResult[FlextTypes.Core.JsonDict]:
        """Make an HTTP request with plugin processing."""
        # Prepare headers - decorator handles exceptions
        request_headers = dict(headers) if headers else {}

        # Apply before_request plugins
        for plugin in self.plugins:
            # Create context for plugin with request information - type-safe dict creation
            request_context: dict[str, object] = {
                "method": str(method),
                "url": str(url),
                "headers": request_headers,
                "data": data if isinstance(data, dict) else {},
                "json": json or {},
                "params": dict(params) if params else {},
            }
            plugin_result = await plugin.before_request(
                request_context, request_context
            )
            if isinstance(plugin_result, FlextResult) and not plugin_result:
                error_msg = f"Plugin failed: {plugin_result.error or 'Unknown plugin error'}"
                raise RuntimeError(error_msg)

        # Execute request (implemented by subclass)
        response_result = await self._execute_request_with_timeout(
            method=method,
            url=url,
            headers=request_headers,
            data=data,
            json=json,
            params=params,
            timeout_seconds=None,
        )

        if not response_result:
            raise RuntimeError(response_result.error or "Request execution failed")

        # Apply after_response plugins - use modern FlextResult.value
        response_data: FlextTypes.Core.JsonDict = response_result.value
        for plugin in self.plugins:
            # Create context for plugin with response information - type-safe dict creation
            response_context: dict[str, object] = {
                "response": response_data,
                "method": str(method),
                "url": str(url),
            }
            after_plugin_result = await plugin.after_response(
                response_data, response_context
            )
            if (
                isinstance(after_plugin_result, FlextResult)
                and after_plugin_result
            ):
                # Type-safe extraction with explicit typing
                plugin_response: object = after_plugin_result.value
                if isinstance(plugin_response, dict):
                    # Type-safe dict iteration with explicit object typing
                    updated_response_data: dict[str, object] = {}
                    # Cast to specific types for PyRight type inference
                    dict_data = cast("dict[str, object]", plugin_response)
                    for response_key, response_value in dict_data.items():
                        if response_key is not None and isinstance(response_key, (str, int, float, bool)):
                            response_key_str: str = str(response_key)
                            updated_response_data[response_key_str] = response_value
                    response_data = updated_response_data
            elif isinstance(after_plugin_result, dict):
                # Direct dict response from plugin with type safety
                typed_response_data: dict[str, object] = {}
                # Cast to specific types for PyRight type inference
                dict_data = cast("dict[str, object]", after_plugin_result)
                for result_key, result_value in dict_data.items():
                    if result_key is not None and isinstance(result_key, (str, int, float, bool)):
                        result_key_str: str = str(result_key)
                        typed_response_data[result_key_str] = result_value
                response_data = typed_response_data

        # Manual FlextResult wrapper for type safety
        try:
            return FlextResult[FlextTypes.Core.JsonDict].ok(response_data)
        except Exception as e:
            logger.exception("Unexpected error in request processing", method=method, url=url)
            return FlextResult[FlextTypes.Core.JsonDict].fail(f"Request processing failed: {e}")

    async def close(self) -> None:
        """Close the client and cleanup resources."""
        await self.stop()

    @abstractmethod
    async def _execute_request(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        data: FlextTypes.Core.JsonDict | str | bytes | None,
        json: FlextTypes.Core.JsonDict | None,
        params: Mapping[str, str] | None,
    ) -> FlextResult[FlextTypes.Core.JsonDict]:
        """Execute the actual HTTP request. Implemented by subclasses."""

    async def _execute_request_with_timeout(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        data: FlextTypes.Core.JsonDict | str | bytes | None,
        json: FlextTypes.Core.JsonDict | None,
        params: Mapping[str, str] | None,
        timeout_seconds: float | None = None,
    ) -> FlextResult[FlextTypes.Core.JsonDict]:
        """Execute HTTP request with asyncio.timeout wrapper."""
        effective_timeout = (
            float(timeout_seconds)
            if timeout_seconds is not None
            else float(self.client_config.timeout)
        )
        async with asyncio.timeout(effective_timeout):
            return await self._execute_request(
                method=method,
                url=url,
                headers=headers,
                data=data,
                json=json,
                params=params,
            )


# ==============================================================================
# BASE AUTHENTICATION SERVICE
# ==============================================================================


class FlextApiBaseAuthService(
    FlextApiBaseService,
    ABC,
):
    """Abstract base service for authentication providers.

    Provides authentication functionality with token management
    and validation capabilities.
    Implements FlextApiAuthProtocol interface.
    """

    auth_config: FlextTypes.Core.JsonDict = Field(
        default_factory=dict,
        description="Authentication configuration",
    )

    async def authenticate(
        self,
        credentials: FlextTypes.Core.JsonDict,
    ) -> FlextResult[FlextTypes.Core.JsonDict]:
        """Authenticate with credentials."""
        try:
            # Validate credentials format
            validation_result = self._validate_credentials(credentials)
            if not validation_result:
                return FlextResult[FlextTypes.Core.JsonDict].fail(
                    validation_result.error or "Credential validation failed",
                )

            # Perform authentication (implemented by subclass)
            auth_result = await self._do_authenticate(credentials)
            if not auth_result:
                return auth_result

            # Create session
            # Use unwrap_or for cleaner default value handling
            auth_data = auth_result.unwrap_or({})
            session_result = await self._create_session(auth_data)
            if not session_result:
                return session_result

            logger.info("Authentication successful")
            return session_result
        except Exception as e:
            logger.exception("Authentication failed")
            return FlextResult[FlextTypes.Core.JsonDict].fail(
                f"Authentication failed: {e}"
            )

    async def validate_token(self, token: str) -> FlextResult[bool]:
        """Validate an authentication token."""
        try:
            # Basic validation: require non-empty token; policy specifics are delegated
            if not token:
                return FlextResult[bool].ok(False)  # noqa: FBT003

            # Perform token validation (implemented by subclass)
            return await self._do_validate_token(token)
        except Exception as e:
            logger.exception("Token validation failed")
            return FlextResult[bool].fail(f"Token validation failed: {e}")

    async def refresh_token(self, token: str) -> FlextResult[str]:
        """Refresh an authentication token."""
        try:
            # Validate current token - use unwrap_or for cleaner code
            if not (await self.validate_token(token)).unwrap_or(default=False):
                return FlextResult[str].fail("Invalid token")

            # Perform token refresh (implemented by subclass)
            return await self._do_refresh_token(token)
        except Exception as e:
            logger.exception("Token refresh failed")
            return FlextResult[str].fail(f"Token refresh failed: {e}")

    def _validate_credentials(
        self,
        credentials: FlextTypes.Core.JsonDict,
    ) -> FlextResult[None]:
        """Validate credentials format. Override in subclasses."""
        if not credentials:
            return FlextResult[None].fail("Credentials cannot be empty")
        return FlextResult[None].ok(None)

    @abstractmethod
    async def _do_authenticate(
        self,
        credentials: FlextTypes.Core.JsonDict,
    ) -> FlextResult[FlextTypes.Core.JsonDict]:
        """Perform actual authentication. Implemented by subclasses."""

    @abstractmethod
    async def _do_validate_token(self, token: str) -> FlextResult[bool]:
        """Perform actual token validation. Implemented by subclasses."""

    @abstractmethod
    async def _do_refresh_token(self, token: str) -> FlextResult[str]:
        """Perform actual token refresh. Implemented by subclasses."""

    async def _create_session(
        self,
        auth_data: FlextTypes.Core.JsonDict,
    ) -> FlextResult[FlextTypes.Core.JsonDict]:
        """Create session from authentication data. Override in subclasses."""
        return FlextResult[FlextTypes.Core.JsonDict].ok(auth_data)


# ==============================================================================
# BASE REPOSITORY SERVICE
# ==============================================================================


class FlextApiBaseRepositoryService(
    FlextApiBaseService,
    ABC,
):
    """Abstract base service for data repositories.

    Provides data access abstraction with CRUD operations
    following Repository Pattern.
    Implements FlextApiRepositoryProtocol interface.
    """

    entity_type: type = Field(description="Entity type for repository")

    async def find_by_id(self, entity_id: str) -> FlextResult[FlextTypes.Core.JsonDict]:
        """Find entity by ID."""
        try:
            if not entity_id:
                return FlextResult[FlextTypes.Core.JsonDict].fail(
                    "Entity ID cannot be empty"
                )

            # Perform lookup (implemented by subclass)
            return await self._do_find_by_id(entity_id)
        except Exception as e:
            logger.exception("Failed to find entity", entity_id=entity_id)
            return FlextResult[FlextTypes.Core.JsonDict].fail(
                f"Failed to find entity: {e}"
            )

    async def find_all(
        self,
        filters: FlextTypes.Core.JsonDict | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> FlextResult[list[FlextTypes.Core.JsonDict]]:
        """Find all entities matching criteria."""
        try:
            # Validate pagination parameters
            if limit is not None and limit <= 0:
                return FlextResult[list[FlextTypes.Core.JsonDict]].fail(
                    "Limit must be positive"
                )
            if offset is not None and offset < 0:
                return FlextResult[list[FlextTypes.Core.JsonDict]].fail(
                    "Offset must be non-negative"
                )

            # Perform query (implemented by subclass)
            return await self._do_find_all(filters, limit, offset)
        except Exception as e:
            logger.exception("Failed to find entities")
            return FlextResult[list[FlextTypes.Core.JsonDict]].fail(
                f"Failed to find entities: {e}"
            )

    async def save(
        self,
        entity: FlextTypes.Core.JsonDict,
    ) -> FlextResult[FlextTypes.Core.JsonDict]:
        """Save an entity."""
        try:
            if not entity:
                return FlextResult[FlextTypes.Core.JsonDict].fail(
                    "Entity cannot be None"
                )

            # Validate entity
            validation_result = self._validate_entity(entity)
            if not validation_result:
                return FlextResult[FlextTypes.Core.JsonDict].fail(
                    validation_result.error or "Entity validation failed",
                )

            # Perform save (implemented by subclass)
            return await self._do_save(entity)
        except Exception as e:
            logger.exception("Failed to save entity")
            return FlextResult[FlextTypes.Core.JsonDict].fail(
                f"Failed to save entity: {e}"
            )

    async def delete(self, entity_id: str) -> FlextResult[None]:
        """Delete an entity by ID."""
        try:
            if not entity_id:
                return FlextResult[None].fail("Entity ID cannot be empty")

            # Check entity exists
            exists_result = await self.find_by_id(entity_id)
            if not exists_result:
                return FlextResult[None].fail("Entity not found")

            # Perform delete (implemented by subclass)
            return await self._do_delete(entity_id)
        except Exception as e:
            logger.exception("Failed to delete entity", entity_id=entity_id)
            return FlextResult[None].fail(f"Failed to delete entity: {e}")

    def _validate_entity(self, _entity: FlextTypes.Core.JsonDict) -> FlextResult[None]:
        """Validate entity before save. Override in subclasses."""
        return FlextResult[None].ok(None)

    @abstractmethod
    async def _do_find_by_id(
        self,
        entity_id: str,
    ) -> FlextResult[FlextTypes.Core.JsonDict]:
        """Perform actual entity lookup. Implemented by subclasses."""

    @abstractmethod
    async def _do_find_all(
        self,
        filters: FlextTypes.Core.JsonDict | None,
        limit: int | None,
        offset: int | None,
    ) -> FlextResult[list[FlextTypes.Core.JsonDict]]:
        """Perform actual query. Implemented by subclasses."""

    @abstractmethod
    async def _do_save(
        self,
        entity: FlextTypes.Core.JsonDict,
    ) -> FlextResult[FlextTypes.Core.JsonDict]:
        """Perform actual save. Implemented by subclasses."""

    @abstractmethod
    async def _do_delete(self, entity_id: str) -> FlextResult[None]:
        """Perform actual delete. Implemented by subclasses."""


# ==============================================================================
# BASE HANDLER SERVICE
# ==============================================================================


class FlextApiBaseHandlerService(
    FlextApiBaseService,
    ABC,
):
    """Abstract base service for request handlers.

    Provides request handling with middleware support
    following Chain of Responsibility Pattern.
    Implements FlextApiHandlerProtocol interface.
    """

    middlewares: list[FlextApiMiddlewareProtocol] = Field(
        default_factory=list[FlextApiMiddlewareProtocol],
        description="Handler middlewares",
    )

    async def handle(
        self,
        request: FlextTypes.Core.JsonDict,
    ) -> FlextResult[FlextTypes.Core.JsonDict]:
        """Handle a request with middleware processing."""
        try:
            # Process request through middlewares
            processed_request = request
            for middleware in self.middlewares:
                middleware_result = await middleware.process_request(processed_request)
                if not middleware_result:
                    return middleware_result
                # Use unwrap_or for cleaner default handling
                processed_request = middleware_result.unwrap_or({})

            # Handle request (implemented by subclass)
            response_result = await self._do_handle(processed_request)
            if not response_result:
                return response_result

            # Process response through middlewares (reverse order)
            # Use unwrap_or for cleaner default handling
            processed_response = response_result.unwrap_or({})
            for middleware in reversed(self.middlewares):
                middleware_result = await middleware.process_response(
                    processed_response,
                )
                # Use unwrap_or to get value or keep current response
                processed_response = middleware_result.unwrap_or(processed_response)

            return FlextResult[FlextTypes.Core.JsonDict].ok(processed_response)
        except Exception as e:
            logger.exception("Request handling failed")
            return FlextResult[FlextTypes.Core.JsonDict].fail(
                f"Request handling failed: {e}"
            )

    @abstractmethod
    async def _do_handle(
        self,
        request: FlextTypes.Core.JsonDict,
    ) -> FlextResult[FlextTypes.Core.JsonDict]:
        """Perform actual request handling. Implemented by subclasses."""


# ==============================================================================
# BASE BUILDER SERVICE
# ==============================================================================


class FlextApiBaseBuilderService(
    FlextApiBaseService,
    ABC,
):
    """Abstract base service for builder implementations.

    Provides builder functionality for constructing
    queries and responses following Builder Pattern.
    """

    def for_query(self) -> FlextApiQueryBuilderProtocol:
        """Get query builder instance."""
        return cast("FlextApiQueryBuilderProtocol", FlextApiQueryBuilder())

    def for_response(self) -> FlextApiResponseBuilderProtocol:
        """Get response builder instance."""
        return cast("FlextApiResponseBuilderProtocol", FlextApiResponseBuilder())


# ==============================================================================
# BASE STREAMING SERVICE
# ==============================================================================


class FlextApiBaseStreamingService(
    FlextApiBaseService,
    ABC,
):
    """Abstract base service for streaming operations.

    Provides streaming functionality for large data transfers
    and real-time communication.
    """

    chunk_size: int = Field(default=8192, description="Stream chunk size in bytes")

    async def stream_data(
        self,
        source: FlextTypes.Core.JsonDict | str | bytes,
    ) -> AsyncIterator[bytes]:
        """Stream data from source."""
        # Validate source outside try to avoid TRY301
        validation_result = self._validate_source(source)
        if not validation_result:
            raise ValueError(validation_result.error)

        try:
            # Stream data (implemented by subclass)
            async for chunk in self._do_stream(source):
                yield chunk
        except Exception:
            logger.exception("Streaming failed")
            raise

    def _validate_source(
        self,
        _source: FlextTypes.Core.JsonDict | str | bytes,
    ) -> FlextResult[None]:
        """Validate stream source. Override in subclasses."""
        return FlextResult[None].ok(None)

    @abstractmethod
    async def _do_stream(
        self,
        source: FlextTypes.Core.JsonDict | str | bytes,
    ) -> AsyncIterator[bytes]:
        """Perform actual streaming. Implemented by subclasses."""
        yield b""  # pragma: no cover


# ==============================================================================
# EXPORTS
# ==============================================================================

__all__ = [
    "FlextApiBaseAuthService",
    "FlextApiBaseBuilderService",
    "FlextApiBaseClientService",
    "FlextApiBaseHandlerService",
    "FlextApiBaseRepositoryService",
    "FlextApiBaseService",
    "FlextApiBaseStreamingService",
]
