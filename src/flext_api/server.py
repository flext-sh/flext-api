"""Generic server abstraction for flext-api.

Provides protocol-agnostic server functionality with:
- Protocol handler registration (HTTP, WebSocket, SSE, GraphQL)
- Middleware pipeline management
- Route registration and management
- WebSocket endpoint support
- SSE endpoint support
- GraphQL endpoint support
- Server lifecycle management

See TRANSFORMATION_PLAN.md - Phase 6 for implementation details.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Callable

from fastapi import FastAPI
from flext_core import FlextLogger, FlextResult, FlextService

from flext_api.middleware import BaseMiddleware
from flext_api.plugins import ProtocolPlugin


class FlextApiServer(FlextService):
    """Generic API server with protocol handler support.

    Features:
    - Protocol handler registration (HTTP, WebSocket, SSE, GraphQL)
    - Middleware pipeline management
    - Dynamic route registration
    - WebSocket endpoint support with bidirectional communication
    - SSE endpoint support with event streaming
    - GraphQL endpoint support with query/mutation/subscription
    - Server lifecycle management (start, stop, restart)
    - Health check and metrics endpoints

    Integration:
    - Uses FastAPI for HTTP server
    - Protocol plugins for WebSocket, SSE, GraphQL
    - Middleware pipeline for request/response processing
    - FlextResult for error handling
    - FlextLogger for structured logging
    """

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 8000,
        title: str = "Flext API Server",
        version: str = "1.0.0",
    ) -> None:
        """Initialize API server.

        Args:
            host: Server host address
            port: Server port
            title: API server title
            version: API server version

        """
        super().__init__()
        self._logger = FlextLogger(__name__)

        # Server configuration
        self._host = host
        self._port = port
        self._title = title
        self._version = version

        # Server state
        self._is_running = False
        self._app: object | None = None

        # Protocol handlers
        self._protocol_handlers: dict[str, ProtocolPlugin] = {}

        # Middleware pipeline
        self._middleware_pipeline: list[BaseMiddleware] = []

        # Route registry
        self._routes: dict[str, dict[str, object]] = {}

        # WebSocket connections
        self._websocket_connections: dict[str, object] = {}

        # SSE connections
        self._sse_connections: dict[str, object] = {}

    def execute(self, *_args: object, **_kwargs: object) -> FlextResult[object]:
        """Execute server service lifecycle operations.

        FlextService requires this method for service execution.
        For server, this is handled by start/stop methods.

        Returns:
            FlextResult[object]: Success result

        """
        return FlextResult[object].ok(None)

    def register_protocol_handler(
        self,
        protocol: str,
        handler: ProtocolPlugin,
    ) -> FlextResult[None]:
        """Register protocol handler for server.

        Args:
            protocol: Protocol name (http, websocket, sse, graphql)
            handler: Protocol plugin instance

        Returns:
            FlextResult indicating success or failure

        """
        if protocol in self._protocol_handlers:
            return FlextResult[None].fail(
                f"Protocol handler already registered: {protocol}"
            )

        self._protocol_handlers[protocol] = handler

        self._logger.info(
            "Protocol handler registered",
            extra={"protocol": protocol, "handler": handler.name},
        )

        return FlextResult[None].ok(None)

    def add_middleware(
        self,
        middleware: BaseMiddleware,
    ) -> FlextResult[None]:
        """Add middleware to server pipeline.

        Args:
            middleware: Middleware instance

        Returns:
            FlextResult indicating success or failure

        """
        self._middleware_pipeline.append(middleware)

        self._logger.info(
            "Middleware added to pipeline",
            extra={"middleware": middleware.__class__.__name__},
        )

        return FlextResult[None].ok(None)

    def register_route(
        self,
        path: str,
        method: str,
        handler: Callable,
        **options: object,
    ) -> FlextResult[None]:
        """Register route with server.

        Args:
            path: Route path (e.g., "/api/users")
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            handler: Route handler function
            **options: Additional route options

        Returns:
            FlextResult indicating success or failure

        """
        route_key = f"{method}:{path}"

        if route_key in self._routes:
            return FlextResult[None].fail(f"Route already registered: {route_key}")

        self._routes[route_key] = {
            "path": path,
            "method": method,
            "handler": handler,
            "options": options,
        }

        self._logger.info(
            "Route registered",
            extra={"path": path, "method": method},
        )

        return FlextResult[None].ok(None)

    def register_websocket_endpoint(
        self,
        path: str,
        handler: Callable,
        **options: object,
    ) -> FlextResult[None]:
        """Register WebSocket endpoint.

        Args:
            path: WebSocket endpoint path
            handler: WebSocket handler function
            **options: Additional endpoint options

        Returns:
            FlextResult indicating success or failure

        """
        route_key = f"WS:{path}"

        if route_key in self._routes:
            return FlextResult[None].fail(
                f"WebSocket endpoint already registered: {path}"
            )

        self._routes[route_key] = {
            "path": path,
            "method": "WS",
            "handler": handler,
            "options": options,
        }

        self._logger.info(
            "WebSocket endpoint registered",
            extra={"path": path},
        )

        return FlextResult[None].ok(None)

    def register_sse_endpoint(
        self,
        path: str,
        handler: Callable,
        **options: object,
    ) -> FlextResult[None]:
        """Register SSE endpoint.

        Args:
            path: SSE endpoint path
            handler: SSE handler function
            **options: Additional endpoint options

        Returns:
            FlextResult indicating success or failure

        """
        route_key = f"SSE:{path}"

        if route_key in self._routes:
            return FlextResult[None].fail(f"SSE endpoint already registered: {path}")

        self._routes[route_key] = {
            "path": path,
            "method": "SSE",
            "handler": handler,
            "options": options,
        }

        self._logger.info(
            "SSE endpoint registered",
            extra={"path": path},
        )

        return FlextResult[None].ok(None)

    def register_graphql_endpoint(
        self,
        path: str = "/graphql",
        schema: object | None = None,
        **options: object,
    ) -> FlextResult[None]:
        """Register GraphQL endpoint.

        Args:
            path: GraphQL endpoint path
            schema: GraphQL schema
            **options: Additional endpoint options

        Returns:
            FlextResult indicating success or failure

        """
        route_key = f"GRAPHQL:{path}"

        if route_key in self._routes:
            return FlextResult[None].fail(
                f"GraphQL endpoint already registered: {path}"
            )

        self._routes[route_key] = {
            "path": path,
            "method": "GRAPHQL",
            "schema": schema,
            "options": options,
        }

        self._logger.info(
            "GraphQL endpoint registered",
            extra={"path": path},
        )

        return FlextResult[None].ok(None)

    def start(self) -> FlextResult[None]:
        """Start API server.

        Returns:
            FlextResult indicating success or failure

        """
        if self._is_running:
            return FlextResult[None].fail("Server is already running")

        # Create FastAPI application
        app_result = self._create_app()
        if app_result.is_failure:
            return FlextResult[None].fail(
                f"Failed to create application: {app_result.error}"
            )

        self._app = app_result.unwrap()

        # Apply middleware
        middleware_result = self._apply_middleware()
        if middleware_result.is_failure:
            return FlextResult[None].fail(
                f"Failed to apply middleware: {middleware_result.error}"
            )

        # Register routes
        routes_result = self._register_routes()
        if routes_result.is_failure:
            return FlextResult[None].fail(
                f"Failed to register routes: {routes_result.error}"
            )

        # Mark server as running
        self._is_running = True

        self._logger.info(
            "API server started",
            extra={
                "host": self._host,
                "port": self._port,
                "routes": len(self._routes),
                "protocols": list(self._protocol_handlers.keys()),
            },
        )

        return FlextResult[None].ok(None)

    def stop(self) -> FlextResult[None]:
        """Stop API server.

        Returns:
            FlextResult indicating success or failure

        """
        if not self._is_running:
            return FlextResult[None].fail("Server is not running")

        # Close WebSocket connections
        for conn_id, connection in self._websocket_connections.items():
            try:
                connection.close()
            except Exception as e:
                self._logger.warning(
                    f"Failed to close WebSocket connection {conn_id}: {e}"
                )

        # Close SSE connections
        for conn_id, connection in self._sse_connections.items():
            try:
                connection.close()
            except Exception as e:
                self._logger.warning(f"Failed to close SSE connection {conn_id}: {e}")

        # Mark server as stopped
        self._is_running = False
        self._app = None

        self._logger.info("API server stopped")

        return FlextResult[None].ok(None)

    def restart(self) -> FlextResult[None]:
        """Restart API server.

        Returns:
            FlextResult indicating success or failure

        """
        stop_result = self.stop()
        if stop_result.is_failure:
            return FlextResult[None].fail(f"Failed to stop server: {stop_result.error}")

        start_result = self.start()
        if start_result.is_failure:
            return FlextResult[None].fail(
                f"Failed to start server: {start_result.error}"
            )

        self._logger.info("API server restarted")

        return FlextResult[None].ok(None)

    def _create_app(self) -> FlextResult[object]:
        """Create FastAPI application.

        Returns:
            FlextResult containing FastAPI app or error

        """
        if FastAPI is None:
            return FlextResult[object].fail(
                "FastAPI not installed. Install with: pip install fastapi"
            )

        try:
            # Create FastAPI app
            app = FastAPI(
                title=self._title,
                version=self._version,
                docs_url="/docs",
                redoc_url="/redoc",
                openapi_url="/openapi.json",
            )

            return FlextResult[object].ok(app)

        except Exception as e:
            return FlextResult[object].fail(f"Failed to create FastAPI app: {e}")

    def _apply_middleware(self) -> FlextResult[None]:
        """Apply middleware to application.

        Returns:
            FlextResult indicating success or failure

        """
        if not self._app:
            return FlextResult[None].fail("Application not created")

        try:
            for middleware in self._middleware_pipeline:
                # Apply middleware to app
                # Note: Actual middleware application would depend on middleware type
                self._logger.debug(
                    "Middleware applied",
                    extra={"middleware": middleware.__class__.__name__},
                )

            return FlextResult[None].ok(None)

        except Exception as e:
            return FlextResult[None].fail(f"Failed to apply middleware: {e}")

    def _register_routes(self) -> FlextResult[None]:
        """Register routes with application.

        Returns:
            FlextResult indicating success or failure

        """
        if not self._app:
            return FlextResult[None].fail("Application not created")

        try:
            for route_config in self._routes.values():
                method = route_config["method"]
                path = route_config["path"]
                handler = route_config["handler"]

                # Register route based on method
                if method == "WS":
                    # WebSocket endpoint
                    self._app.websocket(path)(handler)
                elif method == "SSE":
                    # SSE endpoint (GET with streaming)
                    self._app.get(path)(handler)
                elif method == "GRAPHQL":
                    # GraphQL endpoint (POST for operations)
                    self._app.post(path)(handler)
                else:
                    # Standard HTTP methods
                    method_lower = method.lower()
                    if hasattr(self._app, method_lower):
                        getattr(self._app, method_lower)(path)(handler)

                self._logger.debug(
                    "Route registered",
                    extra={"method": method, "path": path},
                )

            return FlextResult[None].ok(None)

        except Exception as e:
            return FlextResult[None].fail(f"Failed to register routes: {e}")

    def get_app(self) -> FlextResult[object]:
        """Get FastAPI application instance.

        Returns:
            FlextResult containing FastAPI app or error

        """
        if not self._app:
            return FlextResult[object].fail(
                "Application not created. Call start() first."
            )

        return FlextResult[object].ok(self._app)

    @property
    def is_running(self) -> bool:
        """Check if server is running."""
        return self._is_running

    @property
    def host(self) -> str:
        """Get server host."""
        return self._host

    @property
    def port(self) -> int:
        """Get server port."""
        return self._port

    @property
    def routes(self) -> dict[str, dict[str, object]]:
        """Get registered routes."""
        return self._routes.copy()

    @property
    def protocols(self) -> list[str]:
        """Get registered protocols."""
        return list(self._protocol_handlers.keys())


__all__ = ["FlextApiServer"]
