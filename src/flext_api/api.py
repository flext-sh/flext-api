"""FLEXT API - Thin facade for HTTP foundation.

Single entry point exposing all flext-api functionality through domain modules.
NO logic in this facade - pure delegation to specialized classes.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import (
    FlextBus,
    FlextConstants,
    FlextContainer,
    FlextContext,
    FlextDispatcher,
    FlextHandlers,
    FlextLogger,
    FlextProcessors,
    FlextRegistry,
    FlextTypes,
)

from flext_api.app import FlextApiApp
from flext_api.client import FlextApiClient
from flext_api.config import FlextApiConfig
from flext_api.constants import FlextApiConstants
from flext_api.exceptions import FlextApiExceptions
from flext_api.handlers import FlextApiHandlers
from flext_api.models import FlextApiModels
from flext_api.protocols import FlextApiProtocols
from flext_api.storage import FlextApiStorage
from flext_api.typings import FlextApiTypes
from flext_api.utilities import FlextApiUtilities


class FlextApi:
    """Thin facade for HTTP foundation operations with complete FLEXT integration.

    Integrates:
    - FlextBus: Event emission for HTTP operations, lifecycle events
    - FlextContainer: Dependency injection and service management
    - FlextContext: Operation context and request tracing
    - FlextDispatcher: Message routing for HTTP requests/responses
    - FlextProcessors: Request/response processing pipeline
    - FlextRegistry: Component registration and discovery
    - FlextLogger: Structured logging with correlation IDs
    - FlextResult: Railway-oriented error handling throughout

    Usage:
        ```python
        from flext_api import FlextApi

        # Create HTTP client with complete FLEXT ecosystem integration
        client = FlextApi.Client(base_url="https://api.example.com", timeout=30.0)
        # Integrates: FlextBus, FlextContainer, FlextContext, FlextDispatcher,
        # FlextProcessors, FlextRegistry, FlextLogger

        # Create FastAPI app with event-driven lifecycle
        app = FlextApi.create_fastapi_app(title="My API", version="1.0.0")
        # Emits lifecycle events via FlextBus (startup, shutdown, requests)

        # Create storage with event emission and processing
        storage = FlextApi.Storage()
        # Uses FlextProcessors for data validation and transformation
        # Emits events via FlextBus for all operations

        # Access domain modules
        status_code = FlextApi.Constants.HTTP_OK
        request = FlextApi.Models.HttpRequest(method="GET", url="/test")
        config = FlextApi.Config()
        ```

    Architecture:
        - **Domain Library**: Provides HTTP foundation for entire FLEXT ecosystem
        - **Mandatory Usage**: ALL HTTP operations in FLEXT use flext-api
          (NO direct httpx)
        - **Event-Driven**: All operations emit events via FlextBus for monitoring
        - **Context-Aware**: FlextContext provides request tracing and correlation
        - **CQRS Pattern**: Commands (POST/PUT/DELETE) vs Queries (GET) separation
        - **Processing Pipeline**: FlextProcessors handle validation,
          transformation, caching

    Design Principles:
        - Thin facade: NO business logic, pure delegation to domain classes
        - Complete FLEXT integration: Uses ALL flext-core components appropriately
        - Railway pattern: FlextResult throughout for type-safe error handling
        - Zero duplication: Direct access to specialized domain modules
        - Ecosystem compliance: Follows flext-core patterns exclusively
    """

    # Direct access to all domain modules (NO wrappers, NO logic)
    App = FlextApiApp
    Client = FlextApiClient
    Config = FlextApiConfig
    Constants = FlextApiConstants
    Exceptions = FlextApiExceptions
    Handlers = FlextApiHandlers
    Models = FlextApiModels
    Protocols = FlextApiProtocols
    Storage = FlextApiStorage
    Types = FlextApiTypes
    Utilities = FlextApiUtilities

    @classmethod
    def initialize_flext_integration(cls) -> FlextTypes.Dict:
        """Initialize and return FLEXT ecosystem components for integration.

        Returns:
            Dictionary containing initialized FLEXT components

        """
        return {
            "container": FlextContainer.get_global(),
            "context": FlextContext(),
            "bus": FlextBus(),
            "dispatcher": FlextDispatcher(),
            "processors": FlextProcessors(),
            "registry": FlextRegistry(dispatcher=FlextDispatcher()),
            "logger": FlextLogger(__name__),
        }

    # Constant shortcuts for convenience (direct references only)
    HttpMethod = FlextConstants.Http.Method
    ClientStatus = FlextApiConstants.ClientStatus
    RequestStatus = FlextApiConstants.RequestStatus
    ServiceStatus = FlextApiConstants.ServiceStatus
    ContentType = FlextConstants.Http.ContentType
    StorageBackend = FlextApiConstants.StorageBackend
    AuthenticationType = FlextApiConstants.AuthenticationType
    CacheStrategy = FlextApiConstants.CacheStrategy
    LoggingConstants = FlextApiConstants.LoggingConstants

    # Functional factory methods for common operations
    @staticmethod
    def create_client(
        base_url: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        headers: FlextTypes.StringDict | None = None,
        **kwargs: FlextApiTypes.ConfigValue,
    ) -> FlextApiClient:
        """Create HTTP client with configuration.

        Args:
            base_url: Base URL for HTTP requests
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            headers: Default headers
            **kwargs: Additional configuration

        Returns:
            Configured FlextApiClient instance

        """
        return FlextApiClient(
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            headers=headers,
            **kwargs,
        )

    @staticmethod
    def create_fastapi_app(
        title: str = "FLEXT API Service",
        version: str = "1.0.0",
        description: str = "Enterprise API built on FLEXT foundation",
        **kwargs: FlextApiTypes.ConfigValue,
    ) -> object:
        """Create FastAPI application with FLEXT patterns.

        Args:
            title: Application title
            version: Application version
            description: Application description
            **kwargs: Additional FastAPI configuration

        Returns:
            Configured FastAPI application instance

        """
        config = FlextApiModels.AppConfig(
            title=title,
            app_version=version,
            description=description,
            **kwargs,
        )
        return FlextApiApp.create_fastapi_app(config)

    @staticmethod
    def create_storage(
        backend: str = "memory",
        namespace: str = "flext_api",
        **kwargs: FlextApiTypes.ConfigValue,
    ) -> FlextApiStorage:
        """Create storage backend with configuration.

        Args:
            backend: Storage backend type
            namespace: Storage namespace
            **kwargs: Additional storage configuration

        Returns:
            Configured FlextApiStorage instance

        """
        config = FlextApiModels.StorageConfig(
            backend=backend,
            namespace=namespace,
            **kwargs,
        )
        return FlextApiStorage(config=config)

    @staticmethod
    def build_response(
        data: FlextApiTypes.JsonValue = None,
        message: str = "",
        status: str = "success",
    ) -> dict[str, FlextApiTypes.JsonValue]:
        """Build structured API response.

        Args:
            data: Response data
            message: Response message
            status: Response status

        Returns:
            Structured response dictionary

        """
        builder = FlextApiModels.Builder()
        if status == "success":
            return builder.success(data=data, message=message)
        return builder.error(message=message, code=status)

    @staticmethod
    def build_error_response(
        message: str,
        code: str = "error",
    ) -> dict[str, FlextApiTypes.JsonValue]:
        """Build error response.

        Args:
            message: Error message
            code: Error code

        Returns:
            Error response dictionary

        """
        builder = FlextApiModels.Builder()
        return builder.error(message=message, code=code)

    # Convenience access to utility functions
    @staticmethod
    def create_cqrs_client(
        base_url: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        headers: FlextTypes.StringDict | None = None,
        **kwargs: FlextApiTypes.ConfigValue,
    ) -> FlextApiClient:
        """Create HTTP client optimized for CQRS operations.

        Creates a client configured for command/query separation with
        enhanced logging and error handling for CQRS patterns.

        Args:
            base_url: Base URL for HTTP requests
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            headers: Default headers
            **kwargs: Additional configuration

        Returns:
            Configured FlextApiClient with CQRS-optimized settings

        """
        # CQRS-optimized configuration
        cqrs_headers = {
            "X-Request-Type": "cqrs-operation",
            **(headers or {}),
        }

        return FlextApiClient(
            base_url=base_url,
            timeout=timeout or FlextConstants.Defaults.TIMEOUT,
            max_retries=max_retries or FlextConstants.Reliability.MAX_RETRY_ATTEMPTS,
            headers=cqrs_headers,
            **kwargs,
        )

    @staticmethod
    def create_processing_client(
        base_url: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        headers: FlextTypes.StringDict | None = None,
        **kwargs: FlextApiTypes.ConfigValue,
    ) -> FlextApiClient:
        """Create HTTP client with processing pipeline optimizations.

        Creates a client configured for data processing operations with
        enhanced timeouts and retry logic for batch operations.

        Args:
            base_url: Base URL for HTTP requests
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            headers: Default headers
            **kwargs: Additional configuration

        Returns:
            Configured FlextApiClient with processing optimizations

        """
        # Processing-optimized configuration
        processing_headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            **(headers or {}),
        }

        return FlextApiClient(
            base_url=base_url,
            timeout=timeout
            or (FlextConstants.Defaults.TIMEOUT * 2),  # Longer timeout for processing
            max_retries=max_retries
            or (FlextConstants.Reliability.MAX_RETRY_ATTEMPTS + 2),  # More retries
            headers=processing_headers,
            **kwargs,
        )

    @staticmethod
    def create_event_driven_client(
        base_url: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        headers: FlextTypes.StringDict | None = None,
        **kwargs: FlextApiTypes.ConfigValue,
    ) -> FlextApiClient:
        """Create HTTP client for event-driven architectures.

        Creates a client optimized for event-driven patterns with
        correlation ID support and structured event emission.

        Args:
            base_url: Base URL for HTTP requests
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            headers: Default headers
            **kwargs: Additional configuration

        Returns:
            Configured FlextApiClient with event-driven optimizations

        """
        # Event-driven configuration
        event_headers = {
            "X-Event-Driven": "true",
            "X-Correlation-ID": FlextContext().get("correlation_id", "unknown"),
            **(headers or {}),
        }

        return FlextApiClient(
            base_url=base_url,
            timeout=timeout or FlextConstants.Defaults.TIMEOUT,
            max_retries=max_retries or FlextConstants.Reliability.MAX_RETRY_ATTEMPTS,
            headers=event_headers,
            **kwargs,
        )

    @staticmethod
    def create_http_request_handler(
        config: FlextApiConfig | None = None,
    ) -> FlextApiHandlers.HttpOperationHandlers.HttpRequestHandler:
        """Create HTTP request handler for CQRS operations.

        Args:
            config: API configuration instance

        Returns:
            Configured HTTP request handler instance

        """
        return FlextApiHandlers.HttpOperationHandlers.HttpRequestHandler(
            config=config or FlextApiConfig()
        )

    @staticmethod
    def create_resource_command_handlers(
        config: FlextApiConfig | None = None,
    ) -> dict[str, FlextHandlers]:
        """Create resource command handlers (create, update, delete).

        Args:
            config: API configuration instance

        Returns:
            Dictionary mapping operation names to handler instances

        """
        config_instance = config or FlextApiConfig()
        return {
            "create": FlextApiHandlers.HttpCommandHandlers.CreateResourceHandler(
                config=config_instance
            ),
            "update": FlextApiHandlers.HttpCommandHandlers.UpdateResourceHandler(
                config=config_instance
            ),
            "delete": FlextApiHandlers.HttpCommandHandlers.DeleteResourceHandler(
                config=config_instance
            ),
        }

    @staticmethod
    def create_resource_query_handlers(
        config: FlextApiConfig | None = None,
    ) -> dict[str, FlextHandlers]:
        """Create resource query handlers (get, list, search).

        Args:
            config: API configuration instance

        Returns:
            Dictionary mapping operation names to handler instances

        """
        config_instance = config or FlextApiConfig()
        return {
            "get": FlextApiHandlers.HttpQueryHandlers.GetResourceHandler(
                config=config_instance
            ),
            "list": FlextApiHandlers.HttpQueryHandlers.ListResourcesHandler(
                config=config_instance
            ),
            "search": FlextApiHandlers.HttpQueryHandlers.SearchResourcesHandler(
                config=config_instance
            ),
        }

    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format.

        Args:
            url: URL to validate

        Returns:
            True if valid, False otherwise

        """
        result = FlextApiModels.create_validated_http_url(url)
        return result.is_success

    @staticmethod
    def parse_url(url: str) -> FlextApiModels.UrlModel | None:
        """Parse URL into components.

        Args:
            url: URL to parse

        Returns:
            UrlModel with parsed components or None if invalid

        """
        try:
            return FlextApiModels.UrlModel(raw_url=url)
        except Exception:
            return None


__all__ = ["FlextApi"]
