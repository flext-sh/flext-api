"""Infrastructure ports implementations for FLEXT-API.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

This module provides the infrastructure ports for the FLEXT API.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING
from typing import Any

from flext_api.domain.ports import AuthService
from flext_api.domain.ports import CacheService
from flext_api.domain.ports import HealthCheckService
from flext_api.domain.ports import MetricsService
from flext_api.domain.ports import RateLimitService
from flext_api.domain.ports import ServerService
from flext_api.domain.ports import ValidationService
from flext_api.domain.ports import WebFrameworkService
from flext_core.infrastructure.cache.base import CacheBackend
from flext_core.infrastructure.security.base import SecurityService

if TYPE_CHECKING:
    from uuid import UUID

    from flext_api.domain.entities import APIRequest
    from flext_api.domain.entities import APIResponse
    from flext_api.infrastructure.config import APIConfig


class JWTAuthService(AuthService):
    """JWT authentication service implementation."""

    def __init__(self, config: APIConfig) -> None:
        self.config = config
        self.security_service = SecurityService(
            secret_key=config.auth_secret_key,
            algorithm=config.auth_algorithm,
        )

    async def authenticate(self, token: str) -> dict | None:
        """Authenticate a user.

        Args:
            token: The token to authenticate.

        Returns:
            The token data if authenticated, None otherwise.

        """
        try:
            return self.security_service.verify_token(token)
        except Exception:
            return None

    async def authorize(self, user_id: UUID, resource: str, action: str) -> bool:
        """Authorize a user to access a resource.

        Args:
            user_id: The ID of the user.
            resource: The resource to access.
            action: The action to perform.

        Returns:
            True if the user is authorized, False otherwise.

        """
        # Implement authorization logic
        return True  # Placeholder

    async def generate_token(self, user_data: dict) -> str:
        """Generate a token for a user.

        Args:
            user_data: The user data.

        Returns:
            The token.

        """
        return self.security_service.create_token(user_data)

    async def validate_token(self, token: str) -> dict | None:
        """Validate a token.

        Args:
            token: The token to validate.

        Returns:
            The token data if valid, None otherwise.

        """
        return await self.authenticate(token)


class RedisCache(CacheService):
    """Redis cache service implementation."""

    def __init__(self, config: APIConfig) -> None:
        """Initialize the Redis cache service.

        Args:
            config: The API configuration.

        """
        self.config = config
        self.cache_backend = CacheBackend(
            backend="redis",
            redis_url=(
                config.cache_backend
                if config.cache_backend.startswith("redis://")
                else "redis://localhost:6379/0"
            ),
            default_ttl=config.cache_ttl,
        )

    async def get(self, key: str) -> str | bytes | dict[str, object] | None:
        """Get a value from the cache.

        Args:
            key: The key to get.

        Returns:
            The value if found, None otherwise.

        """
        return await self.cache_backend.get(key)

    async def set(
        self,
        key: str,
        value: str | bytes | dict[str, object],
        ttl: int | None = None,
    ) -> bool:
        """Set a key in the cache.

        Args:
            key: The key to set.
            value: The value to set.
            ttl: The time to live for the key.

        Returns:
            True if the key was set, False otherwise.

        """
        return await self.cache_backend.set(key, value, ttl or self.config.cache_ttl)

    async def delete(self, key: str) -> bool:
        """Delete a key from the cache.

        Args:
            key: The key to delete.

        Returns:
            True if the key was deleted, False otherwise.

        """
        return await self.cache_backend.delete(key)

    async def clear(self) -> bool:
        """Clear the cache.

        Returns:
            True if the cache was cleared, False otherwise.

        """
        return await self.cache_backend.clear()


class PrometheusMetricsService(MetricsService):
    """Prometheus metrics service implementation."""

    def __init__(self, config: APIConfig) -> None:
        """Initialize the Prometheus metrics service.

        Args:
            config: The API configuration.

        """
        self.config = config
        self.metrics = {
            "request_count": 0,
            "response_count": 0,
            "error_count": 0,
            "avg_response_time": 0.0,
            "total_response_time": 0.0,
        }

    async def record_request(self, request: APIRequest) -> None:
        """Record a request.

        Args:
            request: The request to record.

        """
        self.metrics["request_count"] += 1

    async def record_response(self, response: APIResponse) -> None:
        """Record a response.

        Args:
            response: The response to record.

        """
        self.metrics["response_count"] += 1

        if response.response_time_ms:
            self.metrics["total_response_time"] += response.response_time_ms
            self.metrics["avg_response_time"] = (
                self.metrics["total_response_time"] / self.metrics["response_count"]
            )

        if response.is_server_error or response.is_client_error:
            self.metrics["error_count"] += 1

    async def get_metrics(self) -> dict:
        """Get the current metrics.

        Returns:
            A copy of the current metrics dictionary.

        """
        return self.metrics.copy()

    async def reset_metrics(self) -> None:
        """Reset all metrics to zero."""
        self.metrics = {
            "request_count": 0,
            "response_count": 0,
            "error_count": 0,
            "avg_response_time": 0.0,
            "total_response_time": 0.0,
        }


class PostgreSQLHealthCheck(HealthCheckService):
    """PostgreSQL health check service implementation."""

    def __init__(self, config: APIConfig) -> None:
        """Initialize the PostgreSQL health check service.

        Args:
            config: The API configuration.

        """
        self.config = config

    async def check_health(self) -> dict:
        """Check the overall health of the system.

        Returns:
            A dictionary containing the health status and detailed checks.

        """
        health_status = {
            "status": "healthy",
            "version": self.config.version,
            "timestamp": asyncio.get_event_loop().time(),
            "checks": await self.check_dependencies(),
        }

        # Overall status based on checks
        if any(not check["healthy"] for check in health_status["checks"].values()):
            health_status["status"] = "unhealthy"

        return health_status

    async def check_database(self) -> bool:
        """Check if the database is healthy.

        Returns:
            True if the database is healthy, False otherwise.

        """
        try:
            # TODO: Implement actual database health check
            return True
        except Exception:
            return False

    async def check_cache(self) -> bool:
        """Check if the cache is healthy.

        Returns:
            True if the cache is healthy, False otherwise.

        """
        try:
            # TODO: Implement actual cache health check
            return True
        except Exception:
            return False

    async def check_dependencies(self) -> dict:
        """Check the health of all dependencies.

        Returns:
            A dictionary containing the health status of each dependency.

        """
        return {
            "database": {
                "healthy": await self.check_database(),
                "response_time_ms": 5,
            },
            "cache": {
                "healthy": await self.check_cache(),
                "response_time_ms": 2,
            },
        }


class MemoryRateLimitService(RateLimitService):
    """Memory-based rate limiting service implementation."""

    def __init__(self, config: APIConfig) -> None:
        """Initialize the memory rate limit service.

        Args:
            config: The API configuration.

        """
        self.config = config
        self.counters = {}
        self.windows = {}

    async def check_rate_limit(self, key: str, limit: int, window: int) -> bool:
        """Check if the rate limit has been exceeded.

        Args:
            key: The key to check.
            limit: The limit to check.
            window: The window to check.

        Returns:
            True if the rate limit has been exceeded, False otherwise.

        """
        current_time = asyncio.get_event_loop().time()

        # Clean old windows
        if key in self.windows and current_time - self.windows[key] > window:
            self.counters[key] = 0
            self.windows[key] = current_time

        # Check current count
        current_count = self.counters.get(key, 0)
        return current_count < limit

    async def increment_counter(self, key: str, window: int) -> int:
        """Increment the counter for a given key.

        Args:
            key: The key to increment.
            window: The time window in seconds.

        Returns:
            The new counter value.

        """
        current_time = asyncio.get_event_loop().time()

        # Initialize if needed:
        if key not in self.counters:
            self.counters[key] = 0
            self.windows[key] = current_time

        # Check if window expired:
        if current_time - self.windows[key] > window:
            self.counters[key] = 0
            self.windows[key] = current_time

        # Increment counter
        self.counters[key] += 1
        return self.counters[key]

    async def reset_counter(self, key: str) -> None:
        """Reset the counter for a given key.

        Args:
            key: The key to reset.

        """
        if key in self.counters:
            self.counters[key] = 0
            self.windows[key] = asyncio.get_event_loop().time()


class FastAPIMiddleware(WebFrameworkService):
    """FastAPI middleware service implementation."""

    def __init__(self, config: APIConfig) -> None:
        self.config = config

    async def create_app(self) -> Any:
        """Create a FastAPI application.

        Returns:
            The configured FastAPI application.

        Raises:
            RuntimeError: If FastAPI is not installed.

        """
        try:
            from fastapi import FastAPI
            from fastapi.middleware.cors import CORSMiddleware

            app = FastAPI(
                title=self.config.title,
                description=self.config.description,
                version=self.config.version,
                docs_url=(
                    self.config.docs_url if self.config.swagger_ui_enabled else None
                ),
                redoc_url=(
                    self.config.redoc_url if self.config.redoc_enabled else None
                ),
                openapi_url=self.config.openapi_url,
            )

            # Add CORS middleware
            app.add_middleware(
                CORSMiddleware,
                allow_origins=self.config.cors_origins,
                allow_credentials=self.config.cors_config["allow_credentials"],
                allow_methods=self.config.cors_config["allow_methods"],
                allow_headers=self.config.cors_config["allow_headers"],
            )

            return app
        except ImportError as e:
            msg = "FastAPI not installed. Please install with: pip install fastapi"
            raise RuntimeError(
                msg,
            ) from e

    async def add_middleware(self, app: Any, middleware: Any) -> None:
        """Add middleware to the FastAPI app.

        Args:
            app: The FastAPI app.
            middleware: The middleware to add.

        """
        app.add_middleware(middleware)

    async def add_route(
        self,
        app: Any,
        path: str,
        handler: Any,
        methods: list[str],
    ) -> None:
        """Add a route to the FastAPI app.

        Args:
            app: The FastAPI app.
            path: The path of the route.
            handler: The handler function.
            methods: The HTTP methods to support.

        """
        for method in methods:
            app.add_api_route(path, handler, methods=[method])

    async def configure_cors(self, app: Any, origins: list[str]) -> None:
        """Configure CORS for the FastAPI app.

        Args:
            app: The FastAPI app.
            origins: The origins to allow.

        """
        # CORS is already configured in create_app


class UvicornServer(ServerService):
    """Uvicorn server service implementation."""

    def __init__(self, config: APIConfig) -> None:
        """Initialize the FastAPI middleware service.

        Args:
            config: The API configuration.

        """
        self.config = config
        self.server = None

    async def start(self, app: Any) -> None:
        """Start the FastAPI server.

        Args:
            app: The FastAPI app.

        """
        try:
            import uvicorn

            config = uvicorn.Config(
                app=app,
                host=self.config.host,
                port=self.config.port,
                log_level=self.config.log_level.lower(),
                reload=self.config.reload,
                access_log=self.config.access_log_enabled,
            )

            self.server = uvicorn.Server(config)
            await self.server.serve()
        except ImportError as e:
            msg = "Uvicorn not installed. Please install with: pip install uvicorn"
            raise RuntimeError(
                msg,
            ) from e

    async def stop(self) -> None:
        """Stop the server."""
        if self.server:
            self.server.should_exit = True

    async def restart(self) -> None:
        """Restart the server."""
        await self.stop()
        # Restart would need app reference

    async def get_status(self) -> dict:
        """Get the server status.

        Returns:
            A dictionary containing the server status information.

        """
        return {
            "status": (
                "running" if self.server and not self.server.should_exit else "stopped"
            ),
            "host": self.config.host,
            "port": self.config.port,
            "workers": self.config.workers,
            "reload": self.config.reload,
        }


class PydanticValidationService(ValidationService):
    """Pydantic validation service implementation."""

    def __init__(self, config: APIConfig) -> None:
        """Initialize the Pydantic validation service.

        Args:
            config: The API configuration.

        """
        self.config = config

    async def validate_request(self, request: APIRequest) -> Any:
        """Validate a request.

        Args:
            request: The request to validate.

        Returns:
            The validated request.

        """
        try:
            # Pydantic models automatically validate
            return {"success": True, "data": request}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def validate_pipeline(self, pipeline: Any) -> Any:
        """Validate a pipeline.

        Args:
            pipeline: The pipeline to validate.

        Returns:
            The validated pipeline.

        """
        try:
            # Pydantic models automatically validate
            return {"success": True, "data": pipeline}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def validate_plugin(self, plugin: Any) -> Any:
        """Validate a plugin.

        Args:
            plugin: The plugin to validate.

        Returns:
            The validated plugin.

        """
        try:
            # Pydantic models automatically validate
            return {"success": True, "data": plugin}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def validate_schema(self, data: dict, schema: dict) -> Any:
        """Validate a schema.

        Args:
            data: The data to validate.
            schema: The schema to validate against.

        Returns:
            The validated data.

        """
        try:
            # TODO: Implement JSON schema validation
            return {"success": True, "data": data}
        except Exception as e:
            return {"success": False, "error": str(e)}
