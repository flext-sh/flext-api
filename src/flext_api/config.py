"""FLEXT API configuration management."""

from __future__ import annotations

from collections.abc import Mapping
from typing import override

from flext_core import FlextConstants, FlextResult
from flext_core.config import FlextConfig
from pydantic import Field, field_validator

# Import from flext-api root - following FLEXT standards
from flext_api.constants import FlextApiConstants


class FlextApiConfig(FlextConfig.BaseConfigModel):
    """Main API configuration class inheriting from FlextConfig.BaseConfigModel.

    This class follows the FLEXT pattern of having a single Flext[Area][Module] class
    that inherits from the equivalent FlextCore class and provides all functionality
    through internal method delegation.

    Inherits ALL FlextConfig.BaseConfigModel functionality and extends with API-specific configuration:
    - API server and client settings
    - Database configuration
    - Security and authentication settings
    - Environment and logging configuration
    - Plugin and caching configuration
    - External service integration settings

    Follows Single Responsibility Principle by handling only API configuration.
    Uses Dependency Inversion Principle by depending on FlextConfig abstraction.
    """

    # =============================================================================
    # API-SPECIFIC CONFIGURATION - Extensions to FlextConfig.BaseConfigModel
    # =============================================================================

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
        default_factory=list[str],
        description="CORS allowed origins",
    )
    # Environment Configuration
    environment: str = Field(
        default="development",
        description="Application environment",
    )
    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    # Inherit base model_config and customize env_prefix
    model_config = FlextConfig.BaseConfigModel.model_config | {
        "env_prefix": "FLEXT_API_"
    }

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

    @override
    def validate_business_rules(self) -> FlextResult[None]:
        """Validate API-specific business rules."""
        # API port validation
        if (
            self.api_port < FlextApiConstants.Connection.PRIVILEGED_PORT_LIMIT
            and self.environment == "production"
        ):
            return FlextResult[None].fail(
                f"Production API should not use privileged ports (< {FlextApiConstants.Connection.PRIVILEGED_PORT_LIMIT})",
            )
        # Debug mode validation
        if self.debug and self.environment == "production":
            return FlextResult[None].fail("Debug mode cannot be enabled in production")
        # Database configuration validation
        if (
            self.database_url
            and self.database_pool_size > FlextApiConstants.ApiDatabase.MAX_POOL_SIZE
        ):
            return FlextResult[None].fail(
                f"Database pool size should not exceed {FlextApiConstants.ApiDatabase.MAX_POOL_SIZE} for optimal performance",
            )
        # Cache configuration validation
        if self.enable_caching and self.cache_ttl <= 0:
            return FlextResult[None].fail(
                "Cache TTL must be positive when caching is enabled",
            )
        # External API configuration validation
        if self.external_api_retries > FlextApiConstants.Config.MAX_RETRIES:
            return FlextResult[None].fail(
                f"External API retries should not exceed {FlextApiConstants.Config.MAX_RETRIES} to avoid excessive delays",
            )
        return FlextResult[None].ok(None)

    @classmethod
    @override
    def create_with_validation(
        cls,
        overrides: Mapping[str, object] | None = None,
        **kwargs: object,
    ) -> FlextResult[FlextConfig]:
        """Create settings instance with validation and return FlextResult.

        Args:
            overrides: Optional dictionary of configuration overrides
            **kwargs: Additional keyword arguments for settings
        Returns:
            FlextResult containing validated FlextApiConfig instance

        """
        try:
            # Merge overrides and kwargs
            config_data: dict[str, object] = {}
            if overrides:
                config_data.update(overrides)
            config_data.update(kwargs)
            settings = (
                cls.model_validate(config_data)
                if config_data
                else cls.model_validate({})
            )
            return FlextResult[FlextConfig].ok(settings)
        except (RuntimeError, ValueError, TypeError, OSError) as e:
            return FlextResult[FlextConfig].fail(f"Failed to create settings: {e}")

    @classmethod
    def create_api_settings(
        cls,
        **overrides: object,
    ) -> FlextResult[FlextApiConfig]:
        """Create API settings with overrides.

        Follows Factory Pattern and Open/Closed Principle.
        Uses FlextResult for consistent error handling.

        Args:
            **overrides: Configuration overrides to apply
        Returns:
            FlextResult containing validated FlextApiConfig instance

        """
        try:
            # Create settings - Pydantic settings automatically load from environment
            settings = cls()
            # Apply any overrides after creation if needed
            if overrides:
                # Merge current values with overrides and validate
                current_values = settings.model_dump()
                current_values.update(overrides)
                settings = cls.model_validate(current_values)
            return FlextResult[FlextApiConfig].ok(settings)
        except Exception as e:
            return FlextResult[FlextApiConfig].fail(f"Failed to create settings: {e}")

    @classmethod
    def load_configuration(
        cls,
        environment: str = "development",
    ) -> FlextResult[FlextApiConfig]:
        """Load configuration for specified environment.

        Args:
            environment: Target environment

        Returns:
            FlextResult containing configuration

        """
        return cls.create_api_settings(environment=environment)

    @classmethod
    def validate_configuration(cls, settings: FlextApiConfig) -> FlextResult[None]:
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
                    return FlextResult[None].fail(
                        "Secret key is required for production environment",
                    )
                if not settings.database_url:
                    return FlextResult[None].fail(
                        "Database URL is required for production environment",
                    )

            # Validate CORS origins format
            for origin in settings.cors_origins:
                if not origin.startswith(("http://", "https://")):
                    return FlextResult[None].fail(
                        f"Invalid CORS origin format: {origin}"
                    )

            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Configuration validation failed: {e}")


# =============================================================================
# LEGACY COMPATIBILITY - Function aliases for backward compatibility
# =============================================================================


def create_api_settings(**overrides: object) -> FlextResult[FlextApiConfig]:
    """Create API settings with overrides."""
    return FlextApiConfig.create_api_settings(**overrides)


def load_configuration(
    environment: str = "development",
) -> FlextResult[FlextApiConfig]:
    """Load configuration for specified environment."""
    return FlextApiConfig.load_configuration(environment)


def validate_configuration(settings: FlextApiConfig) -> FlextResult[None]:
    """Validate configuration settings."""
    return FlextApiConfig.validate_configuration(settings)


# =============================================================================
# LEGACY ALIASES - Class aliases for backward compatibility
# =============================================================================


FlextApiSettings = FlextApiConfig  # Legacy alias
APIConfig = FlextApiConfig  # Alternative alias
FlextAPISettings = FlextApiConfig  # Alternative alias


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "APIConfig",
    "FlextAPISettings",
    # Main Configuration Class (Primary API)
    "FlextApiConfig",
    # Legacy Class Aliases (for backward compatibility)
    "FlextApiSettings",
    # Legacy Function Aliases (for backward compatibility)
    "create_api_settings",
    "load_configuration",
    "validate_configuration",
]
