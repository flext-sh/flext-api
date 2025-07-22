"""Configuration for FLEXT-API infrastructure using unified composition mixins.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

This module provides the configuration for the FLEXT API using unified mixins
from flext-core for maximum code reduction and standardization.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from flext_core import (
    APIConfigMixin,
    BaseConfigMixin,
    ConfigDefaults,
    DatabaseConfigMixin,
    LoggingConfigMixin,
    MonitoringConfigMixin,
    PerformanceConfigMixin,
)
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

if TYPE_CHECKING:
    from flext_core import LogLevel, MemoryMB, PositiveInt
else:
    # Runtime imports for actual usage
    from flext_core import (
        LogLevel,
        MemoryMB,
        PositiveInt,
    )


class APIConfig(
    BaseConfigMixin,
    LoggingConfigMixin,
    DatabaseConfigMixin,
    APIConfigMixin,
    MonitoringConfigMixin,
    PerformanceConfigMixin,
    BaseSettings,
):
    """API configuration using unified composition mixins.

    This configuration eliminates ALL duplication by using composition mixins
    from flext-core. All API server settings are provided by APIConfigMixin.
    """

    model_config = SettingsConfigDict(
        env_prefix="FLEXT_API_",  # Changed from API_ to FLEXT_API_ for consistency
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Override required fields from BaseConfigMixin with defaults
    project_name: str = Field(default="FLEXT API", description="Project name")
    database_url: str = Field(
        default="postgresql://localhost/flext_api",
        description="Database connection URL",
    )

    # Database configuration overrides for compatibility
    db_name: str = Field(default="flext_api", description="Database name")
    db_user: str = Field(default="flext_user", description="Database user")
    db_password: str = Field(default="flext_pass", description="Database password")

    # Add database_pool_size for test compatibility
    database_pool_size: int = Field(default=20, description="Database connection pool size")

    # Monitoring configuration for test compatibility
    metrics_enabled: bool = Field(default=True, description="Enable metrics collection")

    # Override log_level to ensure proper enum value
    log_level: LogLevel = Field(
        default=LogLevel.INFO, description="Log level for the API",
    )

    @classmethod
    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Initialize subclass with custom validation."""
        super().__init_subclass__(**kwargs)

    def __init__(self, **kwargs: Any) -> None:
        """Initialize with case-insensitive log level handling."""
        # Convert lowercase log_level to uppercase if provided
        if "log_level" in kwargs and isinstance(kwargs["log_level"], str):
            kwargs["log_level"] = kwargs["log_level"].upper()

        # Also handle environment variables that may come through pydantic-settings
        import os
        env_log_level = os.getenv("FLEXT_API_LOG_LEVEL")
        if env_log_level and isinstance(env_log_level, str):
            # Override kwargs with properly formatted env var
            kwargs["log_level"] = env_log_level.upper()

        super().__init__(**kwargs)

    # Redis configuration (not using RedisConfigMixin due to URL pattern mismatch)
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL",
    )
    redis_pool_size: PositiveInt = Field(
        default=10,
        description="Redis connection pool size",
    )
    redis_timeout: int = Field(default=5, description="Redis timeout in seconds")
    redis_decode_responses: bool = Field(
        default=True,
        description="Decode Redis responses",
    )

    # Note: Server settings inherited from APIConfigMixin:
    # - api_host, api_port, api_workers, api_timeout, api_cors_origins

    # Additional API-specific settings
    reload: bool = Field(default=False, description="Auto-reload in development")

    # CORS settings (additional to APIConfigMixin)
    cors_methods: ClassVar[list[str]] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    cors_headers: ClassVar[list[str]] = ["*"]
    cors_credentials: bool = True
    # Note: cors_origins inherited from APIConfigMixin (api_cors_origins)

    # API settings (additional to BaseConfigMixin)
    title: str = Field(
        default="FLEXT API",
        max_length=ConfigDefaults.MAX_ENTITY_NAME_LENGTH,
    )
    description: str = Field(
        default="Enterprise Data Integration API",
        max_length=ConfigDefaults.MAX_ERROR_MESSAGE_LENGTH,
    )
    docs_url: str = Field(default="/docs")
    redoc_url: str = Field(default="/redoc")
    openapi_url: str = Field(default="/openapi.json")
    # Note: project_version inherited from BaseConfigMixin

    # Note: All major configurations inherited from mixins:
    # - Database: DatabaseConfigMixin (database_url, database_pool_size, etc.)
    # - Redis: RedisConfigMixin (redis_url, redis_pool_size, etc.)
    # - Performance: PerformanceConfigMixin (batch_size, timeout_seconds, etc.)
    # - Monitoring: MonitoringConfigMixin (metrics_enabled, health_check_enabled, etc.)
    # - Logging: LoggingConfigMixin (log_level, log_file, etc.)

    # Rate limiting settings
    rate_limit_enabled: bool = True
    rate_limit_per_minute: PositiveInt = 100
    rate_limit_burst: PositiveInt = 200

    # Security settings
    security_enabled: bool = True
    trusted_hosts: ClassVar[list[str]] = ["localhost", "127.0.0.1"]

    # Pagination settings (can use inherited batch_size from PerformanceConfigMixin)
    default_page_size: PositiveInt = Field(default=ConfigDefaults.DEFAULT_PAGE_SIZE)
    max_page_size: PositiveInt = Field(default=ConfigDefaults.MAX_PAGE_SIZE)

    # File upload settings
    max_file_size: MemoryMB = 10  # 10MB using MemoryMB type
    allowed_file_types: ClassVar[list[str]] = [".json", ".yaml", ".yml", ".csv"]

    # Background tasks settings
    background_tasks_enabled: bool = True
    task_queue_size: PositiveInt = 1000

    # Feature flags
    websocket_enabled: bool = True
    swagger_ui_enabled: bool = True
    redoc_enabled: bool = True

    # Note: is_development and is_production properties inherited from BaseConfigMixin

    @property
    def database_async_url(self) -> str:
        """Get async database URL with asyncpg driver.

        Returns:
            Database URL with postgresql+asyncpg:// scheme.

        """
        if self.database_url.startswith("postgresql://"):
            return self.database_url.replace(
                "postgresql://",
                "postgresql+asyncpg://",
                1,
            )
        return self.database_url

    # Additional fields for backward compatibility with app.py
    # Note: project_name and project_version inherited from BaseConfigMixin

    @property
    def version(self) -> str:
        """Get project version for backward compatibility."""
        return self.project_version

    @property
    def cors_origins(self) -> list[str]:
        """Get CORS origins for backward compatibility."""
        return ["*"]  # Default CORS origins

    @property
    def host(self) -> str:
        """Get API host for backward compatibility."""
        return self.api_host

    @property
    def port(self) -> int:
        """Get API port for backward compatibility."""
        return self.api_port

    @property
    def workers(self) -> int:
        """Get API workers for backward compatibility."""
        return 4  # Default number of workers

    # Note: Database and Redis properties inherited from mixins
    # Note: JWT properties inherited from AuthConfigMixin (if using AuthConfigMixin)
    # JWT properties for backward compatibility until full auth integration

    @property
    def secret_key(self) -> str:
        """Get JWT secret key for backward compatibility."""
        # Read from environment or use default for testing
        import os

        return os.getenv("FLEXT_API_SECRET_KEY", "test-secret-key-for-real-jwt")

    @property
    def algorithm(self) -> str:
        """Get JWT algorithm for backward compatibility."""
        return "HS256"

    @property
    def access_token_expire_minutes(self) -> int:
        """Get access token expiration for backward compatibility."""
        return 30

    @property
    def cors_config(self) -> dict[str, list[str] | bool]:
        """Get CORS configuration dictionary.

        Returns:
            Dictionary with CORS settings for FastAPI middleware.

        """
        return {
            "allow_origins": self.cors_origins,  # Using cors_origins property
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
            "host": self.api_host,  # Using APIConfigMixin field
            "port": self.api_port,  # Using APIConfigMixin field
            "workers": self.workers,  # Using workers property
            "reload": self.reload,
            "log_level": self.log_level.value.lower(),  # Using LoggingConfigMixin field
            "access_log": True,  # Default value
            "keepalive_timeout": int(self.timeout_seconds),  # Using PerformanceConfigMixin field
        }

    def validate_configuration(self) -> list[str]:
        """Validate API configuration settings.

        Returns:
            List of validation error messages.

        """
        errors: list[str] = []

        # Most validations are now handled by Pydantic field constraints in mixins
        # Only validate application-specific business rules here

        if self.default_page_size < 1 or self.default_page_size > self.max_page_size:
            errors.append(
                f"Default page size must be between 1 and {self.max_page_size}",
            )

        if self.max_file_size < 1:  # 1MB minimum (MemoryMB type)
            errors.append("Max file size must be at least 1MB")

        return errors

    def configure_dependencies(self, container: Any) -> None:
        """Configure dependency injection container.

        Args:
            container: Dependency injection container to configure.

        """
        # For now, just pass - can be extended later for DI configuration

    # Nested configuration objects for backward compatibility
    @property
    def server(self) -> Any:
        """Get server configuration for backward compatibility."""

        class ServerConfig:
            def __init__(self, config: APIConfig) -> None:
                self.host = config.api_host
                self.port = config.api_port
                self.workers = config.workers
                self.reload = config.reload

        return ServerConfig(self)

    @property
    def cors(self) -> Any:
        """Get CORS configuration for backward compatibility."""

        class CorsConfig:
            def __init__(self, config: APIConfig) -> None:
                self.enabled = True  # Always enabled in our setup
                self.origins = config.cors_origins
                self.methods = config.cors_methods
                self.headers = config.cors_headers
                self.credentials = config.cors_credentials

        return CorsConfig(self)

    @property
    def rate_limit(self) -> Any:
        """Get rate limit configuration for backward compatibility."""

        class RateLimitConfig:
            def __init__(self, config: APIConfig) -> None:
                self.enabled = config.rate_limit_enabled
                self.per_minute = config.rate_limit_per_minute
                self.burst = config.rate_limit_burst

        return RateLimitConfig(self)

    @property
    def docs(self) -> Any:
        """Get documentation configuration for backward compatibility."""

        class DocsConfig:
            def __init__(self, config: APIConfig) -> None:
                self.title = config.title
                self.description = config.description
                self.version = config.project_version
                self.url = config.docs_url
                self.redoc_url = config.redoc_url
                self.openapi_url = config.openapi_url

        return DocsConfig(self)

    @property
    def security(self) -> Any:
        """Get security configuration for backward compatibility."""

        class SecurityConfig:
            def __init__(self, config: APIConfig) -> None:
                self.secret_key = config.secret_key
                self.algorithm = config.algorithm
                self.access_token_expire_minutes = config.access_token_expire_minutes
                self.enabled = config.security_enabled
                self.trusted_hosts = config.trusted_hosts

        return SecurityConfig(self)
