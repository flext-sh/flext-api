"""Configuration for FLEXT-API infrastructure.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

This module provides the configuration for the FLEXT API.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import ClassVar

from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict

from flext_core.config import singleton
from flext_core.domain.types import FlextConstants

if TYPE_CHECKING:
    from flext_core.domain.types import LogLevelLiteral


@singleton()
class APIConfig(BaseSettings):
    """API configuration using flext-core BaseSettings with DI."""

    model_config = SettingsConfigDict(
        env_prefix="API_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="forbid",
    )

    # Server settings
    host: str = Field(default="0.0.0.0", description="API server host")
    port: int = Field(default=8000, ge=1, le=65535, description="API server port")
    workers: int = Field(
        default=4,
        ge=1,
        le=FlextConstants.MAX_PAGE_SIZE,
        description="Number of workers",
    )
    reload: bool = Field(default=False, description="Auto-reload in development")

    # CORS settings
    cors_origins: ClassVar[list[str]] = ["http://localhost:3000"]
    cors_methods: ClassVar[list[str]] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    cors_headers: ClassVar[list[str]] = ["*"]
    cors_credentials: bool = True

    # API settings
    title: str = Field(
        default="FLEXT API",
        max_length=FlextConstants.MAX_ENTITY_NAME_LENGTH,
    )
    description: str = Field(
        default="Enterprise Data Integration API",
        max_length=FlextConstants.MAX_ERROR_MESSAGE_LENGTH,
    )
    version: str = Field(default=FlextConstants.FRAMEWORK_VERSION)
    docs_url: str = Field(default="/docs")
    redoc_url: str = Field(default="/redoc")
    openapi_url: str = Field(default="/openapi.json")

    # Database settings
    database_url: str = "postgresql://localhost/flext_api"
    database_pool_size: int = 20
    database_max_overflow: int = 40
    database_pool_timeout: int = 30

    # Authentication settings
    auth_secret_key: str = "dev-secret-key-change-in-production"
    auth_algorithm: str = "HS256"
    auth_access_token_expire_minutes: int = 30

    # Rate limiting settings
    rate_limit_enabled: bool = True
    rate_limit_per_minute: int = 100
    rate_limit_burst: int = 200

    # Monitoring settings
    metrics_enabled: bool = True
    metrics_endpoint: str = "/metrics"
    health_endpoint: str = "/health"

    # Logging settings
    log_level: LogLevelLiteral = Field(default="INFO")
    log_format: str = Field(default="json")
    access_log_enabled: bool = Field(default=True)

    # Security settings
    security_enabled: bool = True
    trusted_hosts: ClassVar[list[str]] = ["localhost", "127.0.0.1"]

    # Timeout settings
    request_timeout: int = 30
    keepalive_timeout: int = 5

    # Pagination settings
    default_page_size: int = Field(default=FlextConstants.DEFAULT_PAGE_SIZE)
    max_page_size: int = Field(default=FlextConstants.MAX_PAGE_SIZE)

    # File upload settings
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: ClassVar[list[str]] = [".json", ".yaml", ".yml", ".csv"]

    # Cache settings
    cache_enabled: bool = True
    cache_ttl: int = 3600
    cache_backend: str = "memory"

    # Background tasks settings
    background_tasks_enabled: bool = True
    task_queue_size: int = 1000

    # Feature flags
    websocket_enabled: bool = True
    swagger_ui_enabled: bool = True
    redoc_enabled: bool = True

    @property
    def is_development(self) -> bool:
        """Check if API is running in development mode.

        Returns:
            True if reload is enabled (development mode).

        """
        return self.reload

    @property
    def is_production(self) -> bool:
        """Check if API is running in production mode.

        Returns:
            True if reload is disabled and host is 0.0.0.0.

        """
        return not self.reload and self.host == "0.0.0.0"

    @property
    def database_async_url(self) -> str:
        """Get async database URL with asyncpg driver.

        Returns:
            Database URL with postgresql+asyncpg:// scheme.

        """
        return self.database_url.replace("postgresql://", "postgresql+asyncpg://")

    @property
    def cors_config(self) -> dict[str, list[str] | bool]:
        """Get CORS configuration dictionary.

        Returns:
            Dictionary with CORS settings for FastAPI middleware.

        """
        return {
            "allow_origins": self.cors_origins,
            "allow_methods": self.cors_methods,
            "allow_headers": self.cors_headers,
            "allow_credentials": self.cors_credentials,
        }

    @property
    def server_config(self) -> dict[str, str | int | bool]:
        """Get server configuration dictionary.

        Returns:
            Dictionary with server settings for Uvicorn.

        """
        return {
            "host": self.host,
            "port": self.port,
            "workers": self.workers,
            "reload": self.reload,
            "log_level": self.log_level.lower(),
            "access_log": self.access_log_enabled,
            "keepalive_timeout": self.keepalive_timeout,
        }

    def validate_configuration(self) -> list[str]:
        """Validate API configuration settings.

        Returns:
            List of validation error messages.

        """
        errors = {}

        if self.port < 1 or self.port > 65535:
            errors.append("Port must be between 1 and 65535")

        if self.workers < 1:
            errors.append("Workers must be at least 1")

        if self.database_pool_size < 1:
            errors.append("Database pool size must be at least 1")

        if self.auth_access_token_expire_minutes < 1:
            errors.append("Token expiration must be at least 1 minute")

        if self.default_page_size < 1 or self.default_page_size > self.max_page_size:
            errors.append(
                f"Default page size must be between 1 and {self.max_page_size}",
            )

        if self.max_file_size < 1024:
            # 1KB minimum
            errors.append("Max file size must be at least 1024 bytes")

        return errors
