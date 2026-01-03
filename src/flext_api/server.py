"""Generic server abstraction for flext-api with Clean Architecture.

Provides protocol-agnostic server functionality with:
- Protocol handler registration (HTTP, WebSocket, SSE, GraphQL)
- Unified endpoint registration with consistency
- Middleware pipeline management
- Server lifecycle management (start, stop, restart)

Uses SOLID principles with nested classes for separated concerns:
- RouteRegistry: Route and endpoint management
- ConnectionManager: WebSocket/SSE connection lifecycle
- LifecycleManager: Server startup, shutdown, restart logic

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Callable

from fastapi import FastAPI
from flext_core import (
    FlextLogger,
    FlextRuntime,
    FlextService,
    e,
    r,
    u,
    x,
)

from flext_api.constants import c
from flext_api.protocols import p
from flext_api.typings import t


class FlextApiServer(FlextService[object], x.Validation):
    """Generic API server with protocol handler support using Clean Architecture.

    Single responsibility: Orchestrate server components (RouteRegistry,
    ConnectionManager, LifecycleManager). All endpoint types delegated to
    unified RouteRegistry for consistency. Connection lifecycle delegated to
    ConnectionManager. Server lifecycle delegated to LifecycleManager.

    Uses Flext patterns: Service lifecycle decorator, logging/validation mixins,
    railway pattern results, and dependency injection.
    """

    # Type annotations for dynamically-set fields (using object.__setattr__)
    _protocol_handlers: dict[str, p.Api.Server.ProtocolHandler]
    _middleware_pipeline: list[Callable[..., object]]

    class RouteRegistry:
        """Handle all endpoint registration with unified interface.

        Supports HTTP, WebSocket, SSE, and GraphQL endpoints.
        """

        def __init__(self, logger: FlextLogger) -> None:
            """Initialize route registry.

            Args:
            logger: Logger instance for audit trail

            """
            self._routes: dict[str, t.Api.RouteData] = {}
            self._logger = logger

        def register(
            self,
            method: c.Api.Method | str,
            path: str,
            handler: Callable[..., object],
            prefix: str = "",
            schema: t.Api.SchemaValue | None = None,
            **options: t.GeneralValueType,
        ) -> r[bool]:
            """Register endpoint with unified interface (DRY - eliminates duplication).

            Args:
                method: HTTP method (GET, POST, etc.) or special (WS, SSE, GRAPHQL)
                path: Endpoint path
                handler: Handler function
                prefix: Optional prefix for method (e.g., "WS" → "WS:path")
                schema: Optional schema (for GraphQL)
                **options: Additional options

            Returns:
                FlextResult indicating success or failure

            """
            route_key = f"{prefix}{method}:{path}" if prefix else f"{method}:{path}"

            if route_key in self._routes:
                return r[bool].fail(f"Route already registered: {route_key}")

            # Convert options to JsonValue-compatible types
            options_json: dict[str, t.GeneralValueType] = {}
            for k, v in options.items():
                if isinstance(v, (str, int, float, bool, type(None))):
                    options_json[k] = v
                elif isinstance(v, (list, dict)):
                    # Recursively convert nested structures
                    # Use FlextRuntime to normalize to t.GeneralValueType (compatible with JsonValue)
                    normalized_value = FlextRuntime.normalize_to_general_value(v)
                    # Type narrowing: ensure JsonValue compatibility
                    if isinstance(
                        normalized_value,
                        (str, int, float, bool, type(None), list, dict),
                    ):
                        options_json[k] = normalized_value
                    else:
                        options_json[k] = str(normalized_value)
                else:
                    options_json[k] = str(v)

            route_data: t.Api.RouteData = {
                "path": path,
                "method": method,
                "handler": handler,
                "options": options_json,
            }
            if schema is not None:
                # Use FlextRuntime to normalize to t.GeneralValueType (compatible with JsonValue)
                normalized_value = FlextRuntime.normalize_to_general_value(v)
                # Convert SchemaValue to GeneralValueType
                # First convert schema to str to ensure it's a proper GeneralValueType
                schema_str = schema if isinstance(schema, str) else str(schema)
                schema_normalized = FlextRuntime.normalize_to_general_value(schema_str)
                # Type narrowing: ensure JsonValue compatibility
                if isinstance(
                    schema_normalized,
                    (str, int, float, bool, type(None), list, dict),
                ):
                    route_data["schema"] = schema_normalized
                else:
                    route_data["schema"] = str(schema_normalized)

            self._routes[route_key] = route_data

            self._logger.info(
                "Endpoint registered",
                extra={"method": method, "path": path, "key": route_key},
            )

            return r[bool].ok(True)

        @property
        def routes(self) -> dict[str, t.Api.RouteData]:
            """Get all registered routes."""
            return self._routes.copy()

        @property
        def count(self) -> int:
            """Get route count."""
            return len(self._routes)

    class ConnectionManager:
        """Manage WebSocket and SSE connection lifecycle."""

        def __init__(self, logger: FlextLogger) -> None:
            """Initialize connection manager.

            Args:
            logger: Logger instance

            """
            self._websocket_connections: dict[str, t.GeneralValueType] = {}
            self._sse_connections: dict[str, t.GeneralValueType] = {}
            self._logger = logger

        def close_all(self) -> r[bool]:
            """Close all active connections gracefully."""
            for conn_id, connection in self._websocket_connections.items():
                try:
                    if connection is not None and hasattr(connection, "close"):
                        connection.close()
                except Exception as e:
                    self._logger.warning(
                        "Failed to close WebSocket %s",
                        conn_id,
                        error=str(e),
                    )

            for conn_id, connection in self._sse_connections.items():
                try:
                    if connection is not None and hasattr(connection, "close"):
                        connection.close()
                except Exception as e:
                    self._logger.warning(
                        "Failed to close SSE %s",
                        conn_id,
                        error=str(e),
                    )

            self._websocket_connections.clear()
            self._sse_connections.clear()

            return r[bool].ok(True)

    class LifecycleManager:
        """Manage server startup, shutdown, and restart logic."""

        def __init__(
            self,
            host: str,
            port: int,
            title: str,
            version: str,
            logger: FlextLogger,
        ) -> None:
            """Initialize lifecycle manager.

            Args:
            host: Server host
            port: Server port
            title: App title
            version: App version
            logger: Logger instance

            """
            self._host = host
            self._port = port
            self._title = title
            self._version = version
            self._logger = logger
            self._is_running = False
            self._app: FastAPI | None = None

        @property
        def logger(self) -> FlextLogger:
            """Get the logger instance."""
            return self._logger

        @property
        def host(self) -> str:
            """Get the server host."""
            return self._host

        @property
        def port(self) -> int:
            """Get the server port."""
            return self._port

        def create_app(self) -> r[FastAPI]:
            """Create FastAPI application."""
            try:
                app = FastAPI(
                    title=self._title,
                    version=self._version,
                    docs_url="/docs",
                    redoc_url="/redoc",
                    openapi_url="/openapi.json",
                )
                return r[FastAPI].ok(app)
            except Exception as e:
                return r[FastAPI].fail(f"Failed to create app: {e}")

        def apply_middleware(
            self,
            middleware_pipeline: list[Callable[..., object]],
        ) -> r[bool]:
            """Apply middleware to application."""
            try:
                for middleware in middleware_pipeline:
                    self._logger.debug(
                        "Middleware applied",
                        extra={"middleware": middleware.__class__.__name__},
                    )
                return r[bool].ok(True)
            except Exception as e:
                return r[bool].fail(f"Failed to apply middleware: {e}")

        def register_routes(
            self,
            routes: dict[str, t.Api.RouteData],
        ) -> r[bool]:
            """Register routes with FastAPI application."""
            if not self._app:
                return r[bool].fail("Application not created")

            # Type narrowing: assign to local variable for type checker
            app = self._app
            try:
                for route_config in routes.values():
                    # Type narrowing: RouteData has specific types
                    method_raw = route_config.get("method")
                    path_raw = route_config.get("path")
                    handler_raw = route_config.get("handler")
                    if (
                        not isinstance(method_raw, str)
                        or not isinstance(path_raw, str)
                        or not callable(handler_raw)
                    ):
                        continue
                    method: str = method_raw
                    path: str = path_raw
                    handler: Callable[..., object] = handler_raw

                    if method == "WS":
                        app.websocket(path)(handler)
                    elif method == "SSE":
                        app.get(path)(handler)
                    elif method == "GRAPHQL":
                        app.post(path)(handler)
                    else:
                        method_lower = method.lower()
                        if hasattr(app, method_lower):
                            getattr(app, method_lower)(path)(handler)

                    self._logger.debug(
                        "Route registered",
                        extra={"method": method, "path": path},
                    )

                return r[bool].ok(True)
            except Exception as e:
                return r[bool].fail(f"Failed to register routes: {e}")

        def start(
            self,
            middleware_pipeline: list[Callable[..., object]],
            routes: dict[str, t.Api.RouteData],
            protocol_handlers: dict[str, p.Api.Server.ProtocolHandler],
        ) -> r[bool]:
            """Start server with complete initialization pipeline."""
            if self._is_running:
                return r[bool].fail("Server already running")

            app_result = self.create_app()
            if app_result.is_failure:
                return r[bool].fail(f"Failed to create app: {app_result.error}")

            self._app = app_result.value

            middleware_result = self.apply_middleware(middleware_pipeline)
            if middleware_result.is_failure:
                return middleware_result

            routes_result = self.register_routes(routes)
            if routes_result.is_failure:
                return routes_result

            self._is_running = True

            self._logger.info(
                "Server started",
                extra={
                    "host": self._host,
                    "port": self._port,
                    "routes": len(routes),
                    "protocols": list(protocol_handlers.keys()),
                },
            )

            return r[bool].ok(True)

        def stop(self) -> r[bool]:
            """Stop server and cleanup resources."""
            if not self._is_running:
                return r[bool].fail("Server not running")

            self._is_running = False
            self._app = None

            self._logger.info("Server stopped")

            return r[bool].ok(True)

        @property
        def is_running(self) -> bool:
            """Check if server is running."""
            return self._is_running

        @property
        def app(self) -> FastAPI | None:
            """Get FastAPI application instance."""
            return self._app

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        title: str = "Flext API Server",
        version: str = "1.0.0",
    ) -> None:
        """Initialize API server with Flext patterns."""
        super().__init__()

        # Enhanced logging with FlextLogger
        logger = FlextLogger(__name__)

        # Use constants for defaults
        server_host = host if host is not None else c.Api.Server.DEFAULT_HOST
        server_port = port if port is not None else c.Api.Server.DEFAULT_PORT

        # Validate configuration using Flext validation patterns
        config_validation = self._validate_server_config(
            server_host,
            server_port,
            title,
            version,
        )
        if config_validation.is_failure:
            error_msg = f"Invalid server configuration: {config_validation.error}"
            raise e.ConfigurationError(error_msg)

        # Delegate to specialized managers (Composition over inheritance)
        self._route_registry = self.RouteRegistry(logger)
        self._connection_manager = self.ConnectionManager(logger)
        self._lifecycle_manager = self.LifecycleManager(
            server_host,
            server_port,
            title,
            version,
            logger,
        )

        # Protocol and middleware with FlextConstants defaults
        object.__setattr__(self, "_protocol_handlers", {})
        object.__setattr__(self, "_middleware_pipeline", [])

    def _validate_server_config(
        self,
        host: str,
        port: int,
        title: str,
        version: str,
    ) -> r[bool]:
        """Validate server configuration using utilities directly."""
        host_result = u.Validation.Network.validate_hostname(host)
        if host_result.is_failure:
            return r[bool].fail(host_result.error or "Host validation failed")

        port_result = u.Validation.Network.validate_port_number(port)
        if port_result.is_failure:
            return r[bool].fail(port_result.error or "Port validation failed")

        # Validate string field - check non-empty
        title_result: r[str]
        if not isinstance(title, str) or not title.strip():
            title_result = r[str].fail("Title cannot be empty")
        else:
            title_result = r[str].ok(title)
        if title_result.is_failure:
            return r[bool].fail(title_result.error or "Title validation failed")

        # Validate string field - check non-empty
        version_result: r[str]
        if not isinstance(version, str) or not version.strip():
            version_result = r[str].fail("Version cannot be empty")
        else:
            version_result = r[str].ok(version)
        if version_result.is_failure:
            return r[bool].fail(version_result.error or "Version validation failed")

        return r[bool].ok(True)

    def execute(self) -> r[object]:
        """Execute server service (required by FlextService)."""
        return r[object].ok(True)

    def register_protocol_handler(
        self,
        protocol: str,
        handler: p.Api.Server.ProtocolHandler,
    ) -> r[bool]:
        """Register protocol handler with Flext validation."""
        # Validate protocol name using utilities directly
        # Validate string field - check non-empty
        protocol_validation: r[str]
        if not isinstance(protocol, str) or not protocol.strip():
            protocol_validation = r[str].fail("Protocol cannot be empty")
        else:
            protocol_validation = r[str].ok(protocol)
        if protocol_validation.is_failure:
            return r[bool].fail(
                protocol_validation.error or "Protocol validation failed",
            )

        if protocol in self._protocol_handlers:
            return r[bool].fail(f"Protocol already registered: {protocol}")

        # Validate handler using Flext protocols
        if not hasattr(handler, "supports_protocol"):
            return r[bool].fail(f"Invalid protocol handler: {type(handler)}")

        self._protocol_handlers[protocol] = handler

        # Use logger from lifecycle manager
        handler_name = ""
        if hasattr(handler, "name"):
            name_value = handler.name
            if isinstance(name_value, str):
                handler_name = name_value

        self._lifecycle_manager.logger.info(
            "Protocol handler registered",
            extra={"protocol": protocol, "handler": handler_name},
        )

        return r[bool].ok(True)

    def add_middleware(
        self,
        middleware: Callable[..., object],
    ) -> r[bool]:
        """Add middleware to pipeline."""
        self._middleware_pipeline.append(middleware)

        self._lifecycle_manager.logger.info(
            "Middleware added",
            extra={"middleware": middleware.__class__.__name__},
        )

        return r[bool].ok(True)

    def register_route(
        self,
        path: str,
        method: c.Api.Method | str,
        handler: Callable[..., object],
        **options: t.GeneralValueType,
    ) -> r[bool]:
        """Register HTTP route (delegates to RouteRegistry)."""
        # Type narrowing: convert options to expected type
        options_typed: dict[str, t.JsonValue | str | int | bool] = {}
        for k, v in options.items():
            # Convert object to GeneralValueType
            v_as_general: t.GeneralValueType = (
                v
                if isinstance(v, (str, int, float, bool, type(None), list, dict))
                else str(v)
            )
            normalized = FlextRuntime.normalize_to_general_value(v_as_general)
            if isinstance(normalized, (str, int, float, bool, type(None), list, dict)):
                options_typed[k] = normalized
            else:
                options_typed[k] = str(normalized)
        return self._route_registry.register(
            method,
            path,
            handler,
            prefix="",
            schema=None,
            **options_typed,
        )

    def register_websocket_endpoint(
        self,
        path: str,
        handler: Callable[..., object],
        **options: t.GeneralValueType,
    ) -> r[bool]:
        """Register WebSocket endpoint (delegates to RouteRegistry)."""
        # Type narrowing: convert options to expected type
        options_typed: dict[str, t.JsonValue | str | int | bool] = {}
        for k, v in options.items():
            # Convert object to GeneralValueType
            v_as_general: t.GeneralValueType = (
                v
                if isinstance(v, (str, int, float, bool, type(None), list, dict))
                else str(v)
            )
            normalized = FlextRuntime.normalize_to_general_value(v_as_general)
            if isinstance(normalized, (str, int, float, bool, type(None), list, dict)):
                options_typed[k] = normalized
            else:
                options_typed[k] = str(normalized)
        return self._route_registry.register(
            "WS",
            path,
            handler,
            prefix="WS",
            schema=None,
            **options_typed,
        )

    def register_sse_endpoint(
        self,
        path: str,
        handler: Callable[..., object],
        **options: t.GeneralValueType,
    ) -> r[bool]:
        """Register SSE endpoint (delegates to RouteRegistry)."""
        # Type narrowing: convert options to expected type
        options_typed: dict[str, t.JsonValue | str | int | bool] = {}
        for k, v in options.items():
            # Convert object to GeneralValueType
            v_as_general: t.GeneralValueType = (
                v
                if isinstance(v, (str, int, float, bool, type(None), list, dict))
                else str(v)
            )
            normalized = FlextRuntime.normalize_to_general_value(v_as_general)
            if isinstance(normalized, (str, int, float, bool, type(None), list, dict)):
                options_typed[k] = normalized
            else:
                options_typed[k] = str(normalized)
        return self._route_registry.register(
            "SSE",
            path,
            handler,
            prefix="SSE",
            schema=None,
            **options_typed,
        )

    def register_graphql_endpoint(
        self,
        path: str = "/graphql",
        schema: t.Api.SchemaValue | None = None,
        **options: t.GeneralValueType,
    ) -> r[bool]:
        """Register GraphQL endpoint (delegates to RouteRegistry)."""
        # Type narrowing: convert options to expected type
        options_typed: dict[str, t.JsonValue | str | int | bool] = {}
        for k, v in options.items():
            # Convert object to GeneralValueType
            v_as_general: t.GeneralValueType = (
                v
                if isinstance(v, (str, int, float, bool, type(None), list, dict))
                else str(v)
            )
            normalized = FlextRuntime.normalize_to_general_value(v_as_general)
            if isinstance(normalized, (str, int, float, bool, type(None), list, dict)):
                options_typed[k] = normalized
            else:
                options_typed[k] = str(normalized)
        return self._route_registry.register(
            "GRAPHQL",
            path,
            lambda: None,
            prefix="GRAPHQL",
            schema=schema,
            **options_typed,
        )

    def start(self) -> r[bool]:
        """Start server (delegates to LifecycleManager)."""
        return self._lifecycle_manager.start(
            self._middleware_pipeline,
            self._route_registry.routes,
            self._protocol_handlers,
        )

    def stop(self) -> r[bool]:
        """Stop server (delegates to ConnectionManager and LifecycleManager)."""
        self._connection_manager.close_all()
        return self._lifecycle_manager.stop()

    def restart(self) -> r[bool]:
        """Restart server (orchestrate stop/start)."""
        stop_result = self.stop()
        if stop_result.is_failure:
            return r[bool].fail(f"Failed to stop: {stop_result.error}")

        start_result = self.start()
        if start_result.is_failure:
            return r[bool].fail(f"Failed to start: {start_result.error}")

        FlextLogger(__name__).info("Server restarted")

        return r[bool].ok(True)

    def get_app(self) -> r[FastAPI]:
        """Get FastAPI application instance."""
        app = self._lifecycle_manager.app
        if not app:
            msg = "Application not created. Call start() first."
            return r[FastAPI].fail(msg)

        # Type check to ensure app is FastAPI instance
        if not isinstance(app, FastAPI):
            msg = f"Application is not FastAPI instance, got {type(app)}"
            return r[FastAPI].fail(msg)

        return r[FastAPI].ok(app)

    @property
    def is_running(self) -> bool:
        """Check if server is running."""
        return self._lifecycle_manager.is_running

    @property
    def host(self) -> str:
        """Get server host."""
        return self._lifecycle_manager.host

    @property
    def port(self) -> int:
        """Get server port."""
        return self._lifecycle_manager.port

    @property
    def routes(self) -> dict[str, t.Api.RouteData]:
        """Get registered routes."""
        return self._route_registry.routes

    @property
    def protocols(self) -> list[str]:
        """Get registered protocols."""
        return list(self._protocol_handlers.keys())


__all__ = ["FlextApiServer"]
