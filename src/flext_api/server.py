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

from collections.abc import (
    Callable,
    MutableMapping,
    MutableSequence,
)
from typing import override

from fastapi import FastAPI

from flext_api import c, e, p, r, t, u
from flext_core import s


class FlextApiServer(s[bool]):
    """Generic API server with protocol handler support using Clean Architecture.

    Single responsibility: Orchestrate server components (RouteRegistry,
    ConnectionManager, LifecycleManager). All endpoint types delegated to
    unified RouteRegistry for consistency. Connection lifecycle delegated to
    ConnectionManager. Server lifecycle delegated to LifecycleManager.

    Uses Flext patterns: Service lifecycle decorator, logging/validation mixins,
    railway pattern results, and dependency injection.
    """

    _protocol_handlers: MutableMapping[
        str,
        p.Api.ProtocolHandler,
    ]
    _middleware_pipeline: MutableSequence[Callable[..., None]]

    class RouteRegistry:
        """Handle all endpoint registration with unified interface.

        Supports HTTP, WebSocket, SSE, and GraphQL endpoints.
        """

        def __init__(self, logger: p.Logger) -> None:
            """Initialize route registry.

            Args:
            logger: Logger instance for audit trail

            """
            self._routes: MutableMapping[str, t.Api.RouteData] = {}
            self.logger = logger

        @property
        def count(self) -> int:
            """Get route count."""
            return len(self._routes)

        @property
        def routes(self) -> t.MappingKV[str, t.Api.RouteData]:
            """Get all registered routes."""
            return dict(self._routes)

        def register(
            self,
            method: c.Api.Method | str,
            path: str,
            handler: Callable[..., t.Api.HttpResponseDict | str | None],
            schema: t.JsonMapping | None = None,
            **options: t.Scalar,
        ) -> p.Result[bool]:
            """Register endpoint with unified interface (DRY - eliminates duplication).

            Args:
                method: HTTP method (GET, POST, etc.) or special (WS, SSE, GRAPHQL)
                path: Endpoint path
                handler: Handler function
                schema: Optional schema (for GraphQL)
                **options: Additional options. Use ``prefix=...`` for route key prefix.

            Returns:
                r indicating success or failure

            """
            prefix_value = options.get("prefix", "")
            prefix = (
                prefix_value if isinstance(prefix_value, str) else str(prefix_value)
            )
            route_key = f"{prefix}{method}:{path}" if prefix else f"{method}:{path}"
            if route_key in self._routes:
                return r[bool].fail(f"Route already registered: {route_key}")
            options_json: t.ConfigurationMapping = {
                key: value for key, value in options.items() if key != "prefix"
            }
            route_dict: MutableMapping[
                str,
                t.JsonValue
                | t.ConfigurationMapping
                | t.JsonMapping
                | t.ResourceCallable
                | Callable[..., t.Api.HttpResponseDict | str | None]
                | None,
            ] = {
                "path": path,
                "method": method,
                "handler": handler,
                "options": options_json,
            }
            if schema is not None:
                route_dict["schema"] = schema
            self._routes[route_key] = route_dict
            self.logger.info(
                "Endpoint registered",
                method=method,
                path=path,
                key=route_key,
            )
            return r[bool].ok(value=True)

    class ConnectionManager:
        """Manage WebSocket and SSE connection lifecycle."""

        def __init__(self, logger: p.Logger) -> None:
            """Initialize connection manager.

            Args:
            logger: Logger instance

            """
            self._websocket_connections: MutableMapping[
                str,
                p.Api.HttpResource,
            ] = {}
            self._sse_connections: MutableMapping[
                str,
                p.Api.HttpResource,
            ] = {}
            self.logger = logger

        def close_all(self) -> p.Result[bool]:
            """Close all active connections gracefully."""
            for conn_id, connection in self._websocket_connections.items():
                try:
                    close_method = getattr(connection, "close", None)
                    if callable(close_method):
                        close_method()
                except c.EXC_HTTP_PROCESSING as exc:
                    self.logger.warning(
                        "Failed to close WebSocket %s",
                        conn_id,
                        error=f"{exc}",
                    )
            for conn_id, connection in self._sse_connections.items():
                try:
                    close_method = getattr(connection, "close", None)
                    if callable(close_method):
                        close_method()
                except c.EXC_HTTP_PROCESSING as exc:
                    self.logger.warning(
                        "Failed to close SSE %s",
                        conn_id,
                        error=f"{exc}",
                    )
            self._websocket_connections.clear()
            self._sse_connections.clear()
            return r[bool].ok(value=True)

    class LifecycleManager:
        """Manage server startup, shutdown, and restart logic."""

        def __init__(
            self,
            host: str,
            port: int,
            title: str,
            version: str,
            logger: p.Logger,
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
            self.logger = logger
            self._is_running = False
            self._app: FastAPI | None = None

        @property
        def app(self) -> FastAPI | None:
            """Get FastAPI application instance."""
            return self._app

        @property
        def host(self) -> str:
            """Get the server host."""
            return self._host

        @property
        def running(self) -> bool:
            """Check if server is running."""
            return self._is_running

        @property
        def port(self) -> int:
            """Get the server port."""
            return self._port

        def apply_middleware(
            self,
            middleware_pipeline: t.SequenceOf[Callable[..., None]],
        ) -> p.Result[bool]:
            """Apply middleware to application."""
            try:
                for middleware in middleware_pipeline:
                    self.logger.debug(
                        "Middleware applied",
                        middleware=middleware.__class__.__name__,
                    )
                return r[bool].ok(value=True)
            except c.EXC_HTTP_PROCESSING as exc:
                return r[bool].fail(f"Failed to apply middleware: {exc}")

        def create_app(self) -> p.Result[FastAPI]:
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
            except (ValueError, TypeError, KeyError, ConnectionError) as exc:
                return r[FastAPI].fail(f"Failed to create app: {exc}")

        def register_routes(
            self, routes: t.MappingKV[str, t.Api.RouteData]
        ) -> p.Result[bool]:
            """Register routes with FastAPI application."""
            if not self._app:
                return r[bool].fail("Application not created")
            app = self._app
            try:
                for route_config in routes.values():
                    method_raw = route_config.get("method")
                    path_raw = route_config.get("path")
                    handler_raw = route_config.get("handler")
                    match (method_raw, path_raw, handler_raw):
                        case [str() as method, str() as path, handler] if callable(
                            handler,
                        ):
                            route_handler = handler
                        case _:
                            continue
                    if method == c.Api.ProtocolMethod.WS.value:
                        app.websocket(path)(route_handler)
                    elif method == c.Api.ProtocolMethod.SSE.value:
                        app.get(path)(route_handler)
                    elif method == c.Api.ProtocolMethod.GRAPHQL.value:
                        app.post(path)(route_handler)
                    else:
                        method_lower = method.lower()
                        if method_lower == c.Api.METHOD_LITERALS_GET_LOWER:
                            app.get(path)(route_handler)
                        elif method_lower == c.Api.METHOD_LITERALS_POST_LOWER:
                            app.post(path)(route_handler)
                        elif method_lower == c.Api.METHOD_LITERALS_PUT_LOWER:
                            app.put(path)(route_handler)
                        elif method_lower == c.Api.METHOD_LITERALS_DELETE_LOWER:
                            app.delete(path)(route_handler)
                        elif method_lower == c.Api.METHOD_LITERALS_PATCH_LOWER:
                            app.patch(path)(route_handler)
                        elif method_lower == c.Api.METHOD_LITERALS_HEAD_LOWER:
                            app.head(path)(route_handler)
                        elif method_lower == c.Api.METHOD_LITERALS_OPTIONS_LOWER:
                            app.options(path)(route_handler)
                    self.logger.debug("Route registered", method=method, path=path)
                return r[bool].ok(value=True)
            except (ValueError, TypeError, KeyError, ConnectionError) as exc:
                return r[bool].fail(f"Failed to register routes: {exc}")

        def start(
            self,
            middleware_pipeline: t.SequenceOf[Callable[..., None]],
            routes: t.MappingKV[str, t.Api.RouteData],
            protocol_handlers: t.MappingKV[
                str,
                p.Api.ProtocolHandler,
            ],
        ) -> p.Result[bool]:
            """Start server with complete initialization pipeline."""
            if self._is_running:
                return r[bool].fail("Server already running")
            app_result = self.create_app()
            if app_result.failure:
                return r[bool].fail(f"Failed to create app: {app_result.error}")
            self._app = app_result.value
            middleware_result = self.apply_middleware(middleware_pipeline)
            if middleware_result.failure:
                return middleware_result
            routes_result = self.register_routes(routes)
            if routes_result.failure:
                return routes_result
            self._is_running = True
            self.logger.info(
                "Server started",
                host=self._host,
                port=self._port,
                routes=len(routes),
                protocols=",".join(protocol_handlers.keys()),
            )
            return r[bool].ok(value=True)

        def stop(self) -> p.Result[bool]:
            """Stop server and cleanup resources."""
            if not self._is_running:
                return r[bool].fail("Server not running")
            self._is_running = False
            self._app = None
            self.logger.info("Server stopped")
            return r[bool].ok(value=True)

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        title: str = "Flext API Server",
        version: str = "1.0.0",
    ) -> None:
        """Initialize API server with Flext patterns."""
        super().__init__()
        logger = u.fetch_logger(__name__)
        server_host = host if host is not None else c.Api.SERVER_DEFAULT_HOST
        server_port = port if port is not None else c.Api.SERVER_DEFAULT_PORT
        config_validation = self._validate_server_config(
            server_host,
            server_port,
            title,
            version,
        )
        if config_validation.failure:
            error_msg = f"Invalid server configuration: {config_validation.error}"
            raise e.ConfigurationError(error_msg)
        self._route_registry = self.RouteRegistry(logger)
        self._connection_manager = self.ConnectionManager(logger)
        self._lifecycle_manager = self.LifecycleManager(
            server_host,
            server_port,
            title,
            version,
            logger,
        )
        self._protocol_handlers: MutableMapping[
            str,
            p.Api.ProtocolHandler,
        ] = {}
        self._middleware_pipeline: MutableSequence[Callable[..., None]] = []

    @property
    def host(self) -> str:
        """Get server host."""
        return self._lifecycle_manager.host

    @property
    def running(self) -> bool:
        """Check if server is running."""
        return self._lifecycle_manager.running

    @property
    def port(self) -> int:
        """Get server port."""
        return self._lifecycle_manager.port

    @property
    def protocols(self) -> t.StrSequence:
        """Get registered protocols."""
        return list(self._protocol_handlers.keys())

    @property
    def routes(self) -> t.MappingKV[str, t.Api.RouteData]:
        """Get registered routes."""
        return self._route_registry.routes

    def add_middleware(
        self,
        middleware: Callable[..., None],
    ) -> p.Result[bool]:
        """Add middleware to pipeline."""
        self._middleware_pipeline.append(middleware)
        self._lifecycle_manager.logger.info(
            "Middleware added",
            middleware=middleware.__class__.__name__,
        )
        return r[bool].ok(value=True)

    @override
    def execute(self) -> p.Result[bool]:
        """Execute server service (required by s)."""
        return r[bool].ok(True)

    def fetch_app(self) -> p.Result[FastAPI]:
        """Get FastAPI application instance."""
        app = self._lifecycle_manager.app
        if not app:
            msg = "Application not created. Call start() first."
            return r[FastAPI].fail(msg)
        return r[FastAPI].ok(app)

    def register_graphql_endpoint(
        self,
        path: str = "/graphql",
        schema: t.JsonMapping | None = None,
        **options: t.Scalar,
    ) -> p.Result[bool]:
        """Register GraphQL endpoint (delegates to RouteRegistry)."""
        options_typed: t.ConfigurationMapping = options
        return self._route_registry.register(
            "GRAPHQL",
            path,
            lambda: None,
            prefix="GRAPHQL",
            schema=schema,
            **options_typed,
        )

    def register_protocol_handler(
        self,
        protocol: str,
        handler: p.Api.ProtocolHandler,
    ) -> p.Result[bool]:
        """Register protocol handler with Flext validation."""
        protocol_validation: p.Result[str]
        if not protocol.strip():
            protocol_validation = r[str].fail("Protocol cannot be empty")
        else:
            protocol_validation = r[str].ok(protocol)
        if protocol_validation.failure:
            return r[bool].fail(
                protocol_validation.error or "Protocol validation failed",
            )
        if protocol in self._protocol_handlers:
            return r[bool].fail(f"Protocol already registered: {protocol}")
        self._protocol_handlers[protocol] = handler
        name_value = getattr(handler, "name", None)
        if isinstance(name_value, str) and name_value:
            handler_name = name_value
        else:
            handler_name = handler.__class__.__name__
        self._lifecycle_manager.logger.info(
            "Protocol handler registered",
            protocol=protocol,
            handler=handler_name,
        )
        return r[bool].ok(value=True)

    def register_route(
        self,
        path: str,
        method: c.Api.Method | str,
        handler: Callable[..., t.Api.HttpResponseDict | str | None],
        **options: t.Scalar,
    ) -> p.Result[bool]:
        """Register HTTP route (delegates to RouteRegistry)."""
        method_value = str(method)
        prefix = method_value if method_value in c.Api.VALID_PROTOCOL_METHODS else ""
        options_typed: t.ConfigurationMapping = options
        return self._route_registry.register(
            method_value,
            path,
            handler,
            prefix=prefix,
            schema=None,
            **options_typed,
        )

    def register_sse_endpoint(
        self,
        path: str,
        handler: Callable[..., t.Api.HttpResponseDict | str | None],
        **options: t.Scalar,
    ) -> p.Result[bool]:
        """Register SSE endpoint (delegates to RouteRegistry)."""
        return self.register_route(
            path,
            c.Api.ProtocolMethod.SSE,
            handler,
            **options,
        )

    def register_websocket_endpoint(
        self,
        path: str,
        handler: Callable[..., t.Api.HttpResponseDict | str | None],
        **options: t.Scalar,
    ) -> p.Result[bool]:
        """Register WebSocket endpoint (delegates to RouteRegistry)."""
        return self.register_route(
            path,
            c.Api.ProtocolMethod.WS,
            handler,
            **options,
        )

    def restart(self) -> p.Result[bool]:
        """Restart server (orchestrate stop/start)."""

        def _log_restart(_: t.JsonValue) -> None:
            u.fetch_logger(__name__).info("Server restarted")

        return (
            self
            .stop()
            .map_error(lambda e: f"Failed to stop: {e}")
            .flat_map(
                lambda _: self.start().map_error(lambda e: f"Failed to start: {e}"),
            )
            .tap(_log_restart)
        )

    def start(self) -> p.Result[bool]:
        """Start server (delegates to LifecycleManager)."""
        return self._lifecycle_manager.start(
            self._middleware_pipeline,
            self._route_registry.routes,
            self._protocol_handlers,
        )

    def stop(self) -> p.Result[bool]:
        """Stop server (delegates to ConnectionManager and LifecycleManager)."""
        self._connection_manager.close_all()
        return self._lifecycle_manager.stop()

    def _validate_server_config(
        self,
        host: str,
        port: int,
        title: str,
        version: str,
    ) -> p.Result[bool]:
        """Validate server configuration using utilities directly."""
        try:
            t.Api.HOSTNAME_ADAPTER.validate_python(host)
        except c.ValidationError as error:
            return r[bool].fail_op("Host validation", error)
        try:
            t.Api.PORT_NUMBER_ADAPTER.validate_python(port)
        except c.ValidationError as error:
            return r[bool].fail_op("Port validation", error)
        title_result: p.Result[str]
        if not title.strip():
            title_result = r[str].fail("Title cannot be empty")
        else:
            title_result = r[str].ok(title)
        if title_result.failure:
            return r[bool].fail(title_result.error or "Title validation failed")
        version_result: p.Result[str]
        if not version.strip():
            version_result = r[str].fail("Version cannot be empty")
        else:
            version_result = r[str].ok(version)
        return version_result.fold(
            on_failure=lambda e: r[bool].fail(e or "Version validation failed"),
            on_success=lambda _: r[bool].ok(value=True),
        )


__all__: t.MutableSequenceOf[str] = ["FlextApiServer"]
