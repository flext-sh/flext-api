"""FLEXT API - Thin facade for HTTP foundation.

Single entry point exposing all flext-api functionality through domain modules.
NO logic in this facade - pure delegation to specialized classes.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_core import (
    FlextBus,
    FlextContainer,
    FlextContext,
    FlextDispatcher,
    FlextProcessors,
    FlextRegistry,
    FlextResult,
    FlextService,
)

import flext_api.client as client_module
from flext_api.app import FlextApiApp
from flext_api.client import FlextApiClient
from flext_api.config import FlextApiConfig
from flext_api.constants import FlextApiConstants
from flext_api.exceptions import FlextApiExceptions
from flext_api.models import FlextApiModels
from flext_api.protocols import FlextApiProtocols
from flext_api.typings import FlextApiTypes
from flext_api.utilities import FlextApiUtilities


class FlextApi(FlextService[FlextApiConfig]):
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
        client = FlextApi().client(base_url="https://api.example.com", timeout=30.0)
        # Integrates: FlextBus, Container, Context, Dispatcher,
        # FlextProcessors, FlextRegistry, FlextLogger

        # Create FastAPI app with event-driven lifecycle
        app = FlextApi().create_fastapi_app(title="My API", version="1.0.0")
        # Emits lifecycle events via FlextBus (startup, shutdown, requests)

        # Create storage with event emission and processing
        storage = FlextApi().storage()
        # Uses FlextProcessors for data validation and transformation
        # Emits events via FlextBus for all operations

        # Access domain modules
        status_code = FlextApi().constants.HTTP_OK
        request = FlextApi().models.HttpRequest(method="GET", url="/test")
        config = FlextApi().config_class()
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

    def __init__(self, config: FlextApiConfig | None = None) -> None:
        """Initialize FlextApi with FLEXT ecosystem integration.

        Args:
            config: API configuration. If None, uses global config.

        """
        super().__init__()
        self._config = config or FlextApiConfig()

        # Initialize FLEXT ecosystem components
        self._bus = FlextBus()
        self._container = FlextContainer.get_global()
        self._context = FlextContext()
        self._dispatcher = FlextDispatcher()
        self._processors = FlextProcessors()
        self._registry = FlextRegistry(dispatcher=self._dispatcher)

        # Register flext-api in global container
        self._container.register("flext_api", self)

    def execute(self) -> FlextResult[FlextApiConfig]:
        """Execute main API operation (FlextService interface).

        Returns:
            FlextResult containing current configuration.

        """
        return FlextResult[FlextApiConfig].ok(self._config)

    @property
    def config(self) -> FlextApiConfig:
        """Get API configuration."""
        return self._config

    # Domain module access properties
    @property
    def client(self) -> type[FlextApiClient]:
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
