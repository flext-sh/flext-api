"""FLEXT API - Thin facade for HTTP foundation.

Single entry point exposing all flext-api functionality through domain modules.
NO logic in this facade - pure delegation to specialized classes.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_api.app import FlextApiApp
from flext_api.client import FlextApiClient
from flext_api.config import FlextApiConfig
from flext_api.constants import FlextApiConstants
from flext_api.exceptions import FlextApiExceptions
from flext_api.models import FlextApiModels
from flext_api.protocols import FlextApiProtocols
from flext_api.storage import FlextApiStorage
from flext_api.typings import FlextApiTypes
from flext_api.utilities import FlextApiUtilities
from flext_core import FlextConstants

__all__ = ["FlextApi"]


class FlextApi:
    """Thin facade providing unified access to all flext-api functionality.

    This is the main entry point for the flext-api HTTP foundation library.
    All functionality is accessed through domain modules - NO wrappers, NO logic.

    Usage:
        ```python
        from flext_api import FlextApi

        # Create HTTP client with flext-core integration
        client = FlextApi.Client(base_url="https://api.example.com")
        # Client integrates: FlextService, FlextBus, FlextContainer,
        # FlextContext, FlextRegistry, FlextLogger

        # Create FastAPI app with lifecycle events
        app = FlextApi.create_fastapi_app(title="My API")
        # App emits events via FlextBus for app lifecycle

        # Create storage with event emission
        storage = FlextApi.Storage()
        # Storage emits events via FlextBus for operations

        # Access constants and models
        status_code = FlextApi.Constants.HTTP_OK
        request = FlextApi.Models.HttpRequest(method="GET", url="/test")
        config = FlextApi.Config()
        ```

    flext-core Integration:
        - FlextService: Client, Storage, App extend FlextService
        - FlextBus: Event emission for storage, app lifecycle, HTTP operations
        - FlextContainer: Dependency injection in client
        - FlextContext: Execution context management in client
        - FlextRegistry: Service and backend registration
        - FlextLogger: Structured logging throughout
        - FlextResult: Railway-oriented error handling everywhere

    Design Principles:
        - Thin facade: NO logic, only references to domain classes
        - Direct access: All domain modules exposed as class attributes
        - Zero duplication: Delegates to specialized domain classes
        - FLEXT compliance: Follows flext-core patterns exclusively
    """

    # Direct access to all domain modules (NO wrappers, NO logic)
    App = FlextApiApp
    Client = FlextApiClient
    Config = FlextApiConfig
    Constants = FlextApiConstants
    Exceptions = FlextApiExceptions
    Models = FlextApiModels
    Protocols = FlextApiProtocols
    Storage = FlextApiStorage
    Types = FlextApiTypes
    Utilities = FlextApiUtilities

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
        headers: dict[str, str] | None = None,
        **kwargs: FlextApiTypes.Core.ConfigValue,
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
        **kwargs: FlextApiTypes.Core.ConfigValue,
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
        **kwargs: FlextApiTypes.Core.ConfigValue,
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
        data: FlextApiTypes.Core.JsonValue = None,
        message: str = "",
        status: str = "success",
    ) -> dict[str, FlextApiTypes.Core.JsonValue]:
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
    ) -> dict[str, FlextApiTypes.Core.JsonValue]:
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
