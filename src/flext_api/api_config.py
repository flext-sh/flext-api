"""FLEXT API configuration management."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core import FlextConstants, FlextResult, FlextBaseConfigModel
from pydantic import Field, field_validator

if TYPE_CHECKING:
    from flext_api.typings import FlextTypes


class FlextApiSettings(FlextBaseConfigModel):
    """API-specific configuration settings extending flext-core patterns.

    Follows Single Responsibility Principle by handling only API configuration.
    Uses Dependency Inversion Principle by depending on FlextSettings abstraction.
    """

    # API Server Configuration
    api_host: str = Field(default="localhost", description="API server host")
    api_port: int = Field(
        default=FlextConstants.Platform.FLEXT_API_PORT,
        description="API server port",
        ge=1,
        le=FlextConstants.Platform.MAX_PORT_NUMBER,
    )
    api_workers: int = Field(default=1, description="Number of worker processes", ge=1)

    # API Client Configuration
    default_timeout: int = Field(default=30, description="Default HTTP timeout", ge=1)
    max_retries: int = Field(default=3, description="Maximum retry attempts", ge=0)

    # Plugin Configuration
    enable_caching: bool = Field(default=True, description="Enable response caching")
    cache_ttl: int = Field(default=300, description="Cache TTL in seconds", ge=0)

    # Database Configuration
    database_url: str | None = Field(
        default=None,
        description="Database connection URL",
    )
    database_pool_size: int = Field(
        default=10,
        description="Database connection pool size",
        ge=1,
    )
    database_timeout: int = Field(
        default=30,
        description="Database timeout in seconds",
        ge=1,
    )

    # External Service Configuration
    external_api_timeout: int = Field(
        default=60,
        description="External API timeout",
        ge=1,
    )
    external_api_retries: int = Field(
        default=3,
        description="External API max retries",
        ge=0,
    )

    # Security Configuration
    secret_key: str | None = Field(default=None, description="Application secret key")
    jwt_expiry: int = Field(default=3600, description="JWT expiry in seconds", ge=60)
    cors_origins: list[str] = Field(
        default_factory=list,
        description="CORS allowed origins",
    )

    # Environment Configuration
    environment: str = Field(
        default="development",
        description="Application environment",
    )
    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: str = Field(default="INFO", description="Logging level")

    class Config:
        """Pydantic configuration class for API settings."""

        env_prefix = "FLEXT_API_"

    @field_validator("api_port")
    @classmethod
    def validate_port(cls, v: int) -> int:
        """Validate port is in acceptable range."""
        min_port = 1
        max_port = FlextConstants.Platform.MAX_PORT_NUMBER
        port_range_error = f"Port must be between {min_port} and {max_port}"
        if not (min_port <= v <= max_port):
            raise ValueError(port_range_error)
        return v

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment value."""
        allowed_environments = {"development", "staging", "production", "test"}
        if v not in allowed_environments:
            msg = f"Environment must be one of: {allowed_environments}"
            raise ValueError(msg)
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        allowed_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in allowed_levels:
            msg = f"Log level must be one of: {allowed_levels}"
            raise ValueError(msg)
        return v.upper()

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate API-specific business rules."""
        # API port validation
        if self.api_port < 1024 and self.environment == "production":
            return FlextResult.fail("Production API should not use privileged ports (< 1024)")
        
        # Debug mode validation
        if self.debug and self.environment == "production":
            return FlextResult.fail("Debug mode cannot be enabled in production")
        
        # Database configuration validation
        if self.database_url and self.database_pool_size > 50:
            return FlextResult.fail("Database pool size should not exceed 50 for optimal performance")
        
        # Cache configuration validation
        if self.enable_caching and self.cache_ttl <= 0:
            return FlextResult.fail("Cache TTL must be positive when caching is enabled")
        
        # External API configuration validation
        if self.external_api_retries > 10:
            return FlextResult.fail("External API retries should not exceed 10 to avoid excessive delays")
        
        return FlextResult.ok(None)

    @classmethod
    def create_with_validation(
        cls,
        overrides: FlextTypes.Core.JsonDict | None = None,
        **kwargs: object,
    ) -> FlextResult[FlextApiSettings]:
        """Create settings instance with validation and return FlextResult.

        Args:
            overrides: Optional dictionary of configuration overrides
            **kwargs: Additional keyword arguments for settings

        Returns:
            FlextResult containing validated FlextApiSettings instance

        """
        try:
            # Merge overrides and kwargs
            config_data = {}
            if overrides:
                config_data.update(overrides)
            config_data.update(kwargs)

            settings = cls.model_validate(config_data) if config_data else cls()
            return FlextResult.ok(settings)
        except (RuntimeError, ValueError, TypeError, OSError) as e:
            return FlextResult.fail(f"Failed to create settings: {e}")


def create_api_settings(**overrides: object) -> FlextResult[FlextApiSettings]:
    """Create API settings with overrides.

    Follows Factory Pattern and Open/Closed Principle.
    Uses FlextResult for consistent error handling.

    Args:
        **overrides: Configuration overrides to apply

    Returns:
        FlextResult containing validated FlextApiSettings instance

    """
    try:
        # Create settings - Pydantic settings automatically load from environment
        settings = FlextApiSettings()

        # Apply any overrides after creation if needed
        if overrides:
            # Merge current values with overrides and validate
            current_values = settings.model_dump()
            current_values.update(overrides)
            settings = FlextApiSettings.model_validate(current_values)

        return FlextResult.ok(settings)
    except Exception as e:
        return FlextResult.fail(f"Failed to create settings: {e}")


# Legacy compatibility - maintain backward compatibility
def load_configuration(
    environment: str = "development",
) -> FlextResult[FlextApiSettings]:
    """Load configuration for specified environment.

    Args:
        environment: Target environment

    Returns:
        FlextResult containing configuration

    """
    return create_api_settings(environment=environment)


# Configuration validation utility
def validate_configuration(settings: FlextApiSettings) -> FlextResult[None]:
    """Validate configuration settings.

    Args:
        settings: Settings to validate

    Returns:
        FlextResult indicating validation success/failure

    """
    try:
        # Validate required fields for production
        if settings.environment == "production":
            if not settings.secret_key:
                return FlextResult.fail(
                    "Secret key is required for production environment",
                )
            if not settings.database_url:
                return FlextResult.fail(
                    "Database URL is required for production environment",
                )

        # Validate CORS origins format
        for origin in settings.cors_origins:
            if not origin.startswith(("http://", "https://")):
                return FlextResult.fail(f"Invalid CORS origin format: {origin}")

        return FlextResult.ok(None)
    except Exception as e:
        return FlextResult.fail(f"Configuration validation failed: {e}")
