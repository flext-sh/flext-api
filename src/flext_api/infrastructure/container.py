"""Dependency injection container for FLEXT-API.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

This module provides the dependency injection container for the FLEXT API.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from lato import Container
from lato import DependencyProvider
from lato.di import DiContainer

from flext_api.application.handlers import AuthenticateHandler
from flext_api.application.handlers import CreatePipelineHandler
from flext_api.application.handlers import CreatePluginHandler
from flext_api.application.handlers import DeletePipelineHandler
from flext_api.application.handlers import DeletePluginHandler
from flext_api.application.handlers import GetPipelineHandler
from flext_api.application.handlers import GetPluginHandler
from flext_api.application.handlers import GetSystemHealthHandler
from flext_api.application.handlers import GetSystemInfoHandler
from flext_api.application.handlers import ListPipelinesHandler
from flext_api.application.handlers import ListPluginsHandler
from flext_api.application.handlers import UpdatePipelineHandler
from flext_api.application.handlers import UpdatePluginHandler
from flext_api.infrastructure.config import APIConfig
from flext_api.infrastructure.persistence.repositories import (
    PostgreSQLPipelineRepository,
)
from flext_api.infrastructure.persistence.repositories import PostgreSQLPluginRepository
from flext_api.infrastructure.ports import FastAPIMiddleware
from flext_api.infrastructure.ports import JWTAuthService
from flext_api.infrastructure.ports import PostgreSQLHealthCheck
from flext_api.infrastructure.ports import PrometheusMetricsService
from flext_api.infrastructure.ports import RedisCache
from flext_api.infrastructure.ports import UvicornServer
from flext_core.domain.constants import FlextFramework

if TYPE_CHECKING:
    from flext_api.domain.ports import AuthService
    from flext_api.domain.ports import CacheService
    from flext_api.domain.ports import HealthCheckService
    from flext_api.domain.ports import MetricsService
    from flext_api.domain.ports import PipelineRepository
    from flext_api.domain.ports import PluginRepository
    from flext_api.domain.ports import ServerService
    from flext_api.domain.ports import WebFrameworkService


class APIContainer(Container):
    """Dependency injection container for FLEXT-API."""

    # Configuration
    config: APIConfig = DependencyProvider(
        lambda: APIConfig(
            host=os.getenv("API_HOST", "0.0.0.0"),
            port=int(os.getenv("API_PORT", "8000")),
            workers=int(os.getenv("API_WORKERS", "4")),
            reload=os.getenv("API_RELOAD", "false").lower() == "true",
            cors_origins=os.getenv("API_CORS_ORIGINS", "http://localhost:3000").split(
                ",",
            ),
            title=os.getenv("API_TITLE", "FLEXT API"),
            description=os.getenv("API_DESCRIPTION", "Enterprise Data Integration API"),
            version=os.getenv("API_VERSION", FlextFramework.VERSION),
            docs_url=os.getenv("API_DOCS_URL", "/docs"),
            redoc_url=os.getenv("API_REDOC_URL", "/redoc"),
            openapi_url=os.getenv("API_OPENAPI_URL", "/openapi.json"),
            database_url=os.getenv("DATABASE_URL", "postgresql://localhost/flext_api"),
            database_pool_size=int(os.getenv("DATABASE_POOL_SIZE", "20")),
            database_max_overflow=int(os.getenv("DATABASE_MAX_OVERFLOW", "40")),
            database_pool_timeout=int(os.getenv("DATABASE_POOL_TIMEOUT", "30")),
            auth_secret_key=os.getenv(
                "AUTH_SECRET_KEY",
                "dev-secret-key-change-in-production",
            ),
            auth_algorithm=os.getenv("AUTH_ALGORITHM", "HS256"),
            auth_access_token_expire_minutes=int(
                os.getenv("AUTH_ACCESS_TOKEN_EXPIRE_MINUTES", "30"),
            ),
            rate_limit_enabled=os.getenv("RATE_LIMIT_ENABLED", "true").lower()
            == "true",
            rate_limit_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", "100")),
            rate_limit_burst=int(os.getenv("RATE_LIMIT_BURST", "200")),
            metrics_enabled=os.getenv("METRICS_ENABLED", "true").lower() == "true",
            metrics_endpoint=os.getenv("METRICS_ENDPOINT", "/metrics"),
            health_endpoint=os.getenv("HEALTH_ENDPOINT", "/health"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_format=os.getenv("LOG_FORMAT", "json"),
            access_log_enabled=os.getenv("ACCESS_LOG_ENABLED", "true").lower()
            == "true",
            security_enabled=os.getenv("SECURITY_ENABLED", "true").lower() == "true",
            trusted_hosts=os.getenv("TRUSTED_HOSTS", "localhost,127.0.0.1").split(","),
            request_timeout=int(os.getenv("REQUEST_TIMEOUT", "30")),
            keepalive_timeout=int(os.getenv("KEEPALIVE_TIMEOUT", "5")),
            default_page_size=int(os.getenv("DEFAULT_PAGE_SIZE", "20")),
            max_page_size=int(os.getenv("MAX_PAGE_SIZE", "100")),
            max_file_size=int(os.getenv("MAX_FILE_SIZE", str(10 * 1024 * 1024))),
            allowed_file_types=os.getenv(
                "ALLOWED_FILE_TYPES",
                ".json,.yaml,.yml,.csv",
            ).split(","),
            cache_enabled=os.getenv("CACHE_ENABLED", "true").lower() == "true",
            cache_ttl=int(os.getenv("CACHE_TTL", "3600")),
            cache_backend=os.getenv("CACHE_BACKEND", "memory"),
            background_tasks_enabled=os.getenv(
                "BACKGROUND_TASKS_ENABLED",
                "true",
            ).lower()
            == "true",
            task_queue_size=int(os.getenv("TASK_QUEUE_SIZE", "1000")),
            websocket_enabled=os.getenv("WEBSOCKET_ENABLED", "true").lower() == "true",
            swagger_ui_enabled=os.getenv("SWAGGER_UI_ENABLED", "true").lower()
            == "true",
            redoc_enabled=os.getenv("REDOC_ENABLED", "true").lower() == "true",
        ),
    )

    # Repositories
    pipeline_repository: PipelineRepository = DependencyProvider(
        lambda config: PostgreSQLPipelineRepository(config.database_url),
        config,
    )

    plugin_repository: PluginRepository = DependencyProvider(
        lambda config: PostgreSQLPluginRepository(config.database_url),
        config,
    )

    # Services
    auth_service: AuthService = DependencyProvider(
        JWTAuthService,
        config,
    )

    cache_service: CacheService = DependencyProvider(
        lambda config:
            RedisCache(config) if config.cache_backend == "redis" else None,
        config,
    )

    metrics_service: MetricsService = DependencyProvider(
        PrometheusMetricsService,
        config,
    )

    health_check_service: HealthCheckService = DependencyProvider(
        PostgreSQLHealthCheck,
        config,
    )

    web_framework_service: WebFrameworkService = DependencyProvider(
        FastAPIMiddleware,
        config,
    )

    server_service: ServerService = DependencyProvider(
        UvicornServer,
        config,
    )

    # Handlers
    authenticate_handler: AuthenticateHandler = DependencyProvider(
        AuthenticateHandler,
        auth_service,
        config,
    )

    create_pipeline_handler: CreatePipelineHandler = DependencyProvider(
        CreatePipelineHandler,
        pipeline_repository,
        config,
    )

    get_pipeline_handler: GetPipelineHandler = DependencyProvider(
        GetPipelineHandler,
        pipeline_repository,
        config,
    )

    list_pipelines_handler: ListPipelinesHandler = DependencyProvider(
        ListPipelinesHandler,
        pipeline_repository,
        config,
    )

    update_pipeline_handler: UpdatePipelineHandler = DependencyProvider(
        UpdatePipelineHandler,
        pipeline_repository,
        config,
    )

    delete_pipeline_handler: DeletePipelineHandler = DependencyProvider(
        DeletePipelineHandler,
        pipeline_repository,
        config,
    )

    create_plugin_handler: CreatePluginHandler = DependencyProvider(
        CreatePluginHandler,
        plugin_repository,
        config,
    )

    get_plugin_handler: GetPluginHandler = DependencyProvider(
        GetPluginHandler,
        plugin_repository,
        config,
    )

    list_plugins_handler: ListPluginsHandler = DependencyProvider(
        ListPluginsHandler,
        plugin_repository,
        config,
    )

    update_plugin_handler: UpdatePluginHandler = DependencyProvider(
        UpdatePluginHandler,
        plugin_repository,
        config,
    )

    delete_plugin_handler: DeletePluginHandler = DependencyProvider(
        DeletePluginHandler,
        plugin_repository,
        config,
    )

    get_system_info_handler: GetSystemInfoHandler = DependencyProvider(
        GetSystemInfoHandler,
        config,
    )

    get_system_health_handler: GetSystemHealthHandler = DependencyProvider(
        GetSystemHealthHandler,
        health_check_service,
        config,
    )


def create_api_container() -> APIContainer:
    """Create the API container."""
    container = APIContainer()

    # Initialize container
    di_container = DiContainer()
    container.wire(di_container)

    return container


# Global container instance
api_container = create_api_container()
