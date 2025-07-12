"""FLEXT API Configuration - Modern Python 3.13 patterns.

REFACTORED:
    Uses flext-core BaseSettings with structured value objects.
Zero tolerance for duplication.
"""

from __future__ import annotations

from typing import Any

from pydantic import Field
from pydantic_settings import SettingsConfigDict

from flext_core.config import BaseSettings
from flext_core.config import get_container
from flext_core.config import singleton
from flext_core.domain.constants import FlextFramework
from flext_core.domain.pydantic_base import DomainValueObject


class ServerConfig(DomainValueObject):
    """Server configuration value object."""

    host: str = Field("0.0.0.0", description="API server host")  # noqa: S104
    port: int = Field(8000, ge=1, le=65535, description="API server port")
    workers: int = Field(4, ge=1, le=100, description="Number of worker processes")
    reload: bool = Field(False, description="Enable auto-reload in development")


class CORSConfig(DomainValueObject):
    """CORS configuration value object."""

    enabled: bool = Field(True, description="Enable CORS")
    allow_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000"],
        description="Allowed CORS origins",
    )
    allow_methods: list[str] = Field(
        default_factory=lambda: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        description="Allowed HTTP methods",
    )
    allow_headers: list[str] = Field(
        default_factory=lambda: ["*"],
        description="Allowed headers",
    )
    allow_credentials: bool = Field(True, description="Allow credentials")


class RateLimitConfig(DomainValueObject):
    """Rate limiting configuration value object."""

    enabled: bool = Field(True, description="Enable rate limiting")
    per_minute: int = Field(100, ge=1, le=10000, description="Requests per minute")
    per_hour: int = Field(1000, ge=1, le=100000, description="Requests per hour")


class APIDocsConfig(DomainValueObject):
    """API documentation configuration value object."""

    title: str = Field("FLEXT API", description="API title")
    description: str = Field(
        "Enterprise Data Integration API",
        description="API description",
    )
    version: str = Field(FlextFramework.VERSION, description="API version")
    docs_url: str = Field("/docs", description="Swagger UI URL")
    redoc_url: str = Field("/redoc", description="ReDoc URL")
    openapi_url: str = Field("/openapi.json", description="OpenAPI schema URL")


class SecurityConfig(DomainValueObject):
    """Security configuration value object."""

    secret_key: str = Field(
        "change-this-secret-in-production",
        description="Secret key for JWT signing",
    )
    algorithm: str = Field("HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(
        30,
        ge=1,
        le=1440,
        description="Access token expiration in minutes",
    )
    trusted_hosts: list[str] = Field(
        default_factory=lambda: ["*"],
        description="Trusted host patterns",
    )


@singleton()
class APISettings(BaseSettings):
    """FLEXT API configuration settings with environment variable support.

    All settings can be overridden via environment variables with the
    prefix FLEXT_API_ (e.g., FLEXT_API_SERVER__HOST).

    Uses flext-core BaseSettings foundation with DI support.
    """

    model_config = SettingsConfigDict(
        env_prefix="FLEXT_API_",
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
        validate_assignment=True,
        str_strip_whitespace=True,
        use_enum_values=True,
    )

    # Project identification
    project_name: str = Field("flext-api", description="Project name")
    project_version: str = Field(FlextFramework.VERSION, description="Project version")

    # Configuration value objects
    server: ServerConfig = Field(
        default_factory=ServerConfig,
        description="Server configuration",
    )
    cors: CORSConfig = Field(
        default_factory=CORSConfig,
        description="CORS configuration",
    )
    rate_limit: RateLimitConfig = Field(
        default_factory=RateLimitConfig,
        description="Rate limiting configuration",
    )
    docs: APIDocsConfig = Field(
        default_factory=APIDocsConfig,
        description="API documentation configuration",
    )
    security: SecurityConfig = Field(
        default_factory=SecurityConfig,
        description="Security configuration",
    )

    # Database settings
    database_url: str = Field(
        "postgresql://localhost/flext_api",
        description="Database connection URL",
    )
    database_pool_size: int = Field(
        20,
        ge=1,
        le=100,
        description="Database connection pool size",
    )

    # Redis settings
    redis_url: str = Field(
        "redis://localhost:6379/0",
        description="Redis connection URL",
    )

    # Environment and debugging
    environment: str = Field("development", description="Environment name")
    debug: bool = Field(False, description="Debug mode")
    log_level: str = Field("INFO", description="Log level")
    log_format: str = Field("text", description="Log format (text or json)")

    @property
    def rate_limit_enabled(self) -> bool:
        """Check if rate limiting is enabled.

        Returns:
            True if rate limiting is enabled.

        """
        return self.rate_limit.enabled

    @property
    def rate_limit_per_minute(self) -> int:
        """Get rate limit per minute.

        Returns:
            Maximum requests allowed per minute.

        """
        return self.rate_limit.per_minute

    def configure_dependencies(self, container: Any = None) -> None:
        """Configure dependency injection container.

        Args:
            container: Optional DI container to configure.

        """
        if container is None:
            container = get_container()

        # Register this settings instance
        container.register(APISettings, self)

        # Call parent configuration
        super().configure_dependencies(container)


# Convenience functions for getting settings
def get_api_settings() -> APISettings:
    """Get APISettings instance from environment variables or defaults."""
    return APISettings()


def create_development_api_config() -> APISettings:
    """Create development-specific API configuration."""
    return APISettings(
        environment="development",
        debug=True,
        server=ServerConfig(
            reload=True,
            workers=1,
        ),
        rate_limit=RateLimitConfig(
            enabled=False,
        ),
        security=SecurityConfig(
            secret_key="development-secret-key-change-in-production",  # noqa: S106
            access_token_expire_minutes=60,
        ),
    )


def create_production_api_config() -> APISettings:
    """Create production-specific API configuration."""
    return APISettings(
        environment="production",
        debug=False,
        log_format="json",
        server=ServerConfig(
            workers=4,
            reload=False,
        ),
        rate_limit=RateLimitConfig(
            enabled=True,
            per_minute=60,
            per_hour=1000,
        ),
        security=SecurityConfig(
            algorithm="RS256",
            access_token_expire_minutes=15,
            trusted_hosts=["api.flext.sh", "*.flext.sh"],
        ),
        cors=CORSConfig(
            allow_origins=["https://app.flext.sh"],
            allow_credentials=True,
        ),
    )
