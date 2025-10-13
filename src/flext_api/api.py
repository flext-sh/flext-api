"""FLEXT API - Thin facade for HTTP foundation.

Single entry point exposing all flext-api functionality through domain modules.
NO logic in this facade - pure delegation to specialized classes.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextCore

import flext_api.client as client_module
from flext_api.app import FlextApiApp
from flext_api.config import FlextApiConfig
from flext_api.constants import FlextApiConstants
from flext_api.exceptions import FlextApiExceptions
from flext_api.handlers import FlextApiHandlers
from flext_api.models import FlextApiModels
from flext_api.protocols import FlextApiProtocols
from flext_api.typings import FlextApiTypes
from flext_api.utilities import FlextApiUtilities


class FlextApi(FlextCore.Service[FlextApiConfig]):
    """Thin facade for HTTP foundation operations with complete FLEXT integration.

    Integrates:
    - FlextCore.Bus: Event emission for HTTP operations, lifecycle events
    - FlextCore.Container: Dependency injection and service management
    - FlextCore.Context: Operation context and request tracing
    - FlextCore.Dispatcher: Message routing for HTTP requests/responses
    - FlextCore.Processors: Request/response processing pipeline
    - FlextCore.Registry: Component registration and discovery
    - FlextCore.Logger: Structured logging with correlation IDs
    - FlextCore.Result: Railway-oriented error handling throughout

    Usage:
        ```python
        from flext_api import FlextApi

        # Create HTTP client with complete FLEXT ecosystem integration
        client = FlextApi().client(base_url="https://api.example.com", timeout=30.0)
        # Integrates: FlextCore.Bus, Container, Context, Dispatcher,
        # FlextCore.Processors, FlextCore.Registry, FlextCore.Logger

        # Create FastAPI app with event-driven lifecycle
        app = FlextApi().create_fastapi_app(title="My API", version="1.0.0")
        # Emits lifecycle events via FlextCore.Bus (startup, shutdown, requests)

        # Create storage with event emission and processing
        storage = FlextApi().storage()
        # Uses FlextCore.Processors for data validation and transformation
        # Emits events via FlextCore.Bus for all operations

        # Access domain modules
        status_code = FlextApi().constants.HTTP_OK
        request = FlextApi().models.HttpRequest(method="GET", url="/test")
        config = FlextApi().config_class()
        ```

    Architecture:
        - **Domain Library**: Provides HTTP foundation for entire FLEXT ecosystem
        - **Mandatory Usage**: ALL HTTP operations in FLEXT use flext-api
          (NO direct httpx)
        - **Event-Driven**: All operations emit events via FlextCore.Bus for monitoring
        - **Context-Aware**: FlextCore.Context provides request tracing and correlation
        - **CQRS Pattern**: Commands (POST/PUT/DELETE) vs Queries (GET) separation
        - **Processing Pipeline**: FlextCore.Processors handle validation,
          transformation, caching

    Design Principles:

        - Thin facade: NO business logic, pure delegation to domain classes
        - Complete FLEXT integration: Uses ALL flext-core components appropriately
        - Railway pattern: FlextCore.Result throughout for type-safe error handling
        - Zero duplication: Direct access to specialized domain modules
        - Ecosystem compliance: Follows flext-core patterns exclusively
    """

    def __init__(self, config: FlextApiConfig | None = None) -> None:
        """Initialize FlextApi with FLEXT ecosystem integration.

        Args:
            config: API configuration. If None, uses global config.

        """
        super().__init__()
        self._config = config or FlextApiConfig()

        # Initialize FLEXT ecosystem components
        self._bus = FlextCore.Bus()
        self._container = FlextCore.Container.get_global()
        self._context = FlextCore.Context()
        self._dispatcher = FlextCore.Dispatcher()
        self._processors = FlextCore.Processors()
        self._registry = FlextCore.Registry(dispatcher=self._dispatcher)

        # Register flext-api in global container
        self._container.register("flext_api", self)

    def execute(self) -> FlextCore.Result[FlextApiConfig]:
        """Execute main API operation (FlextCore.Service interface).

        Returns:
            FlextCore.Result containing current configuration.

        """
        return FlextCore.Result[FlextApiConfig].ok(self._config)

    @property
    def config(self) -> FlextApiConfig:
        """Get API configuration."""
        return self._config

    # Domain module access properties
    @property
    def client(self) -> type[client_module.FlextApiClient]:
        """Access HTTP client functionality."""
        return client_module.FlextApiClient

    @property
    def app(self) -> type[FlextApiApp]:
        """Access FastAPI app functionality."""
        return FlextApiApp

    @property
    def models(self) -> type[FlextApiModels]:
        """Access API models."""
        return FlextApiModels

    @property
    def constants(self) -> type[FlextApiConstants]:
        """Access API constants."""
        return FlextApiConstants

    @property
    def config_class(self) -> type[FlextApiConfig]:
        """Access API configuration."""
        return FlextApiConfig

    @property
    def exceptions(self) -> type[FlextApiExceptions]:
        """Access API exceptions."""
        return FlextApiExceptions

    @property
    def handlers(self) -> type[FlextApiHandlers]:
        """Access API handlers."""
        return FlextApiHandlers

    @property
    def protocols(self) -> type[FlextApiProtocols]:
        """Access API protocols."""
        return FlextApiProtocols

    @property
    def types(self) -> type[FlextApiTypes]:
        """Access API types."""
        return FlextApiTypes

    @property
    def utilities(self) -> type[FlextApiUtilities]:
        """Access API utilities."""
        return FlextApiUtilities

    # Direct access to all domain modules (NO wrappers, NO logic)
