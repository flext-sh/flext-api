"""Configuration for FLEXT-API infrastructure using unified composition mixins.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

This module provides the configuration for the FLEXT API using unified mixins
from flext-core for maximum code reduction and standardization.
"""

from __future__ import annotations

from typing import Any, ClassVar

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class APIConfig(BaseSettings):
    """API configuration using FLEXT Core patterns.

    NOTE: This should inherit from FlextCoreSettings when available.,
    For now, using BaseSettings with FLEXT patterns.
    """

    """API configuration using modern Pydantic BaseSettings.

    This configuration provides all necessary API server settings
    using modern Pydantic patterns.
    """

    model_config = SettingsConfigDict(
        env_prefix="FLEXT_API_",  # Changed from API_ to FLEXT_API_ for consistency
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Core configuration fields
    project_name: str = Field(default="FLEXT API", description="Project name")
    project_version: str = Field(default="0.7.0", description="Project version")
    database_url: str = Field(
        default="postgresql://localhost/flext_api",
        description="Database connection URL",
    )

    # Database configuration
    db_name: str = Field(default="flext_api", description="Database name")
    db_user: str = Field(default="flext_user", description="Database user")
    db_password: str = Field(default="flext_pass", description="Database password")
    database_pool_size: int = Field(
        default=20,
        description="Database connection pool size",
    )

    # API server configuration (using api_host/api_port to avoid property conflicts)
    api_host: str = Field(default="localhost", description="API server host")
    api_port: int = Field(default=8000, description="API server port")
    debug: bool = Field(default=False, description="Enable debug mode")
    reload: bool = Field(default=False, description="Enable auto-reload")

    # Monitoring configuration
    metrics_enabled: bool = Field(default=True, description="Enable metrics collection")

    # Logging configuration
    log_level: str = Field(default="INFO", description="Log level for the API")
    log_format: str = Field(default="text", description="Log format (text or json)")

    # Performance configuration
    timeout_seconds: int = Field(default=30, description="Request timeout in seconds")

    def __init__(self, **kwargs: object) -> None:
        """Initialize with case-insensitive log level handling."""
        # Convert lowercase log_level to uppercase if provided
        if "log_level" in kwargs and isinstance(kwargs["log_level"], str):
            kwargs["log_level"] = kwargs["log_level"].upper()

        # Environment variables are automatically handled by pydantic-settings
        # No manual os.getenv() needed - this is handled by model_config

        super().__init__(**kwargs)

    # Redis configuration (not using RedisConfigMixin due to URL pattern mismatch)
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL",
    )
    redis_pool_size: int = Field(
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

    # CORS settings (additional to APIConfigMixin)
    cors_methods: ClassVar[list[str]] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    cors_headers: ClassVar[list[str]] = ["*"]
    cors_credentials: bool = True
    # Note: cors_origins inherited from APIConfigMixin (api_cors_origins)

    # API settings (additional to BaseConfigMixin)
    title: str = Field(
        default="FLEXT API",
        max_length=100,
    )
    description: str = Field(
        default="Enterprise Data Integration API",
        max_length=500,
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
    rate_limit_per_minute: int = 100
    rate_limit_burst: int = 200

    # Security settings
    security_enabled: bool = True
    trusted_hosts: ClassVar[list[str]] = ["localhost", "127.0.0.1", "testserver"]

    # Pagination settings (can use inherited batch_size from PerformanceConfigMixin)
    default_page_size: int = Field(default=100)
    max_page_size: int = Field(default=100)

    # File upload settings
    max_file_size: int = 10  # 10MB using int type
    allowed_file_types: ClassVar[list[str]] = [".json", ".yaml", ".yml", ".csv"]

    # Background tasks settings
    background_tasks_enabled: bool = True
    task_queue_size: int = 1000

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
            )
        return self.database_url

    @property
    def version(self) -> str:
        """Get project version."""
        return self.project_version

    @property
    def cors_origins(self) -> list[str]:
        """Get CORS origins."""
        return ["*"]  # Default CORS origins

    @property
    def host(self) -> str:
        """Get API host."""
        return self.api_host

    @property
    def port(self) -> int:
        """Get API port."""
        return self.api_port

    @property
    def workers(self) -> int:
        """Get API workers."""
        return 4  # Default number of workers

    # JWT Security Configuration - Using Pydantic fields instead of manual os.getenv
    secret_key: SecretStr = Field(
        default=SecretStr("test-secret-key-for-development-only"),
        description="JWT secret key - MUST be overridden in production",
    )
    jwt_algorithm: str = Field(
        default="HS256",
        description="JWT signing algorithm",
    )
    access_token_expire_minutes: int = Field(
        default=30,
        description="Access token expiration in minutes",
    )

    @property
    def algorithm(self) -> str:
        """Get JWT algorithm for backward compatibility."""
        return self.jwt_algorithm

    @property
    def secret_key_str(self) -> str:
        """Get JWT secret key as string for backward compatibility."""
        return self.secret_key.get_secret_value()

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
            "log_level": self.log_level.lower(),  # log_level is string
            "access_log": True,  # Default value
            "keepalive_timeout": int(
                self.timeout_seconds
            ),  # Using PerformanceConfigMixin field
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
                f"Default page size must be between 1 and {self.max_page_size}"
            )

        if self.max_file_size < 1:  # 1MB minimum (int type)
            errors.append("Max file size must be at least 1MB")

        return errors

    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.debug or self.reload

    def is_production(self) -> bool:
        """Check if running in production mode."""
        return not self.is_development()

    def configure_dependencies(self, container: Any) -> None:
        """Configure dependency injection container.

        Args:
            container: Dependency injection container to configure.,

        """
        # For now, just pass - can be extended later for DI configuration

    @property
    def server(self) -> Any:
        """Get server configuration."""

        class ServerConfig:
            def __init__(self, config: APIConfig) -> None:
                self.host = config.api_host
                self.port = config.api_port
                self.workers = config.workers
                self.reload = config.reload

        return ServerConfig(self)

    @property
    def cors(self) -> Any:
        """Get CORS configuration."""

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
        """Get rate limit configuration."""

        class RateLimitConfig:
            def __init__(self, config: APIConfig) -> None:
                self.enabled = config.rate_limit_enabled
                self.per_minute = config.rate_limit_per_minute
                self.burst = config.rate_limit_burst

        return RateLimitConfig(self)

    @property
    def docs(self) -> Any:
        """Get documentation configuration."""

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
        """Get security configuration."""

        class SecurityConfig:
            def __init__(self, config: APIConfig) -> None:
                self.secret_key = config.secret_key.get_secret_value()
                self.algorithm = config.jwt_algorithm
                self.access_token_expire_minutes = config.access_token_expire_minutes
                self.enabled = config.security_enabled
                self.trusted_hosts = config.trusted_hosts

        return SecurityConfig(self)
