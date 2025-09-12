"""FLEXT API Config - Configuration management extending flext-core patterns.

Provides API-specific configuration management extending flext-core FlextConfig
with API domain-specific settings, HTTP configuration, and validation patterns.
Follows consolidated class pattern with nested configuration domains.
Uses singleton pattern as source of truth.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import ClassVar
from urllib.parse import urlparse

from flext_core import FlextConfig, FlextLogger, FlextResult, FlextTypes
from pydantic import Field, field_validator, model_validator
from pydantic_settings import SettingsConfigDict

logger = FlextLogger(__name__)


# API CONFIGURATION HELL: 595 LINES COM 37 CLASSES/MÉTODOS!
# SINGLETON HELL: Mais um singleton para configuração simples!
# ENTERPRISE MADNESS: "Configuration domains" para API REST!
# OVER-VALIDATION: Type-safe validation para configuração básica!

class FlextApiConfig(FlextConfig):
    """OVER-ENGINEERED API CONFIG: 595 lines for REST API settings!

    ARCHITECTURAL VIOLATIONS:
    - SINGLETON PATTERN for simple API configuration
    - "CONFIGURATION DOMAINS" for REST API settings
    - ENVIRONMENT VARIABLE HELL with complex validation
    - TYPE-SAFE VALIDATION for basic server settings
    - CORS configuration as "enterprise patterns"

    REALITY CHECK: This should be simple Pydantic BaseSettings with minimal validation.
    MIGRATE TO: Single configuration class with environment loading.

    API configuration class extending FlextConfig with singleton pattern.

    Provides type-safe configuration for API services with
    environment variable support, validation, and default values following
    flext-core configuration patterns. Uses singleton pattern as source of truth.

    Configuration Structure:
        - Server settings: host, port, workers, debug mode
        - API settings: title, version, hostname, endpoints
        - Client settings: timeouts, retries, base URLs
        - CORS settings: origins, methods, headers
        - Storage settings: backend selection

    Environment Variables:
        - FLEXT_API_HOST: Server host address
        - FLEXT_API_PORT: Server port
        - FLEXT_API_WORKERS: Number of worker processes
        - FLEXT_API_DEBUG: Enable debug mode
        - FLEXT_API_TITLE: API title
        - FLEXT_API_VERSION: API version
        - FLEXT_API_TIMEOUT: Default request timeout
        - FLEXT_API_MAX_RETRIES: Maximum retry attempts
        - FLEXT_API_BASE_URL: Base URL for requests
        - FLEXT_API_CORS_ORIGINS: Allowed CORS origins
        - FLEXT_API_BACKEND: Default storage backend

    Singleton Usage:
        # Get global instance (source of truth)
        config = FlextApiConfig.get_global_instance()

        # Set global instance with overrides
        FlextApiConfig.set_global_instance(custom_config)

        # Create with environment-specific settings
        config = FlextApiConfig.create_for_environment("production")
    """

    # SINGLETON PATTERN - Global configuration instance
    _global_instance: ClassVar[FlextApiConfig | None] = None

    # Override model_config to use FLEXT_API_ prefix for API-specific fields
    model_config = SettingsConfigDict(
        # Environment integration
        env_prefix="FLEXT_API_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        # Validation behavior
        validate_assignment=True,
        str_strip_whitespace=True,
        use_enum_values=True,
        extra="ignore",
        # Schema generation
        title="FLEXT API Configuration",
        json_schema_extra={
            "description": "FLEXT API configuration with type safety",
            "examples": [
                {
                    "host": "127.0.0.1",
                    "port": 8000,
                    "workers": 4,
                    "debug": False,
                    "api_title": "FLEXT API",
                    "api_version": "0.9.0",
                }
            ],
        },
    )

    # =========================================================================
    # SERVER CONFIGURATION
    # =========================================================================

    # Server configuration (extends base host/port from FlextConfig)
    api_host: str = Field(
        default="127.0.0.1",
        description="API server host address",
    )
    api_port: int = Field(
        default=8000,
        ge=1,
        le=65535,
        description="API server port",
    )
    workers: int = Field(
        default=4,
        ge=1,
        le=50,
        description="Number of worker processes",
    )
    api_debug: bool = Field(
        default=False,
        description="Enable API debug mode",
    )

    # =========================================================================
    # API CONFIGURATION
    # =========================================================================

    api_title: str = Field(
        default="FLEXT API",
        description="API title",
        min_length=1,
        max_length=100,
    )
    api_version: str = Field(
        default="0.9.0",
        description="API version",
        pattern=r"^\d+\.\d+\.\d+.*$",
    )
    api_description: str = Field(
        default="FLEXT Enterprise Data Integration API",
        description="API description",
        max_length=500,
    )

    # =========================================================================
    # CLIENT CONFIGURATION
    # =========================================================================

    default_timeout: float = Field(
        default=30.0,
        gt=0,
        le=300,
        description="Default request timeout in seconds",
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum retry attempts for client requests",
    )
    retry_delay: float = Field(
        default=1.0,
        ge=0.1,
        le=60.0,
        description="Delay between retries in seconds",
    )
    api_base_url: str = Field(
        default="http://localhost:8000",
        description="Base URL for API requests",
    )

    # =========================================================================
    # CORS CONFIGURATION
    # =========================================================================

    cors_origins: FlextTypes.Core.StringList = Field(
        default_factory=lambda: ["*"],
        description="Allowed CORS origins",
    )
    cors_methods: FlextTypes.Core.StringList = Field(
        default_factory=lambda: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        description="Allowed CORS methods",
    )
    cors_headers: FlextTypes.Core.StringList = Field(
        default_factory=lambda: ["*"],
        description="Allowed CORS headers",
    )
    cors_credentials: bool = Field(
        default=True,
        description="Allow CORS credentials",
    )

    # =========================================================================
    # STORAGE CONFIGURATION
    # =========================================================================

    default_backend: str = Field(
        default="memory",
        description="Default storage backend",
    )
    storage_config: FlextTypes.Core.Dict = Field(
        default_factory=dict,
        description="Storage backend configuration",
    )

    # =========================================================================
    # RATE LIMITING CONFIGURATION
    # =========================================================================

    enable_rate_limiting: bool = Field(
        default=True,
        description="Enable API rate limiting",
    )
    rate_limit_requests: int = Field(
        default=100,
        ge=1,
        le=10000,
        description="Rate limit requests per window",
    )
    rate_limit_window: int = Field(
        default=60,
        ge=1,
        le=3600,
        description="Rate limit window in seconds",
    )

    # =========================================================================
    # FIELD VALIDATORS
    # =========================================================================

    @field_validator("api_host")
    @classmethod
    def validate_api_host(cls, v: str) -> str:
        """Validate API host is not empty."""
        if not v or not v.strip():
            msg = "API host cannot be empty"
            raise ValueError(msg)
        return v.strip()

    @field_validator("api_base_url")
    @classmethod
    def validate_api_base_url(cls, v: str) -> str:
        """Validate API base URL format."""
        if not v or not v.strip():
            msg = "API base URL cannot be empty"
            raise ValueError(msg)

        try:
            parsed = urlparse(v.strip())
            if not parsed.scheme or not parsed.netloc:
                msg = "API base URL must include scheme and hostname"
                raise ValueError(msg)
            return v.strip()
        except Exception as e:
            msg = f"Invalid API base URL format: {e}"
            raise ValueError(msg)

    @field_validator("default_backend")
    @classmethod
    def validate_default_backend(cls, v: str) -> str:
        """Validate storage backend is supported."""
        supported_backends = {"memory", "file", "redis", "database"}
        if v not in supported_backends:
            msg = f"Storage backend must be one of: {supported_backends}"
            raise ValueError(msg)
        return v

    @model_validator(mode="after")
    def validate_configuration_consistency(self) -> FlextApiConfig:
        """Validate cross-field configuration consistency."""
        # Ensure API port doesn't conflict with base port
        if hasattr(self, "port") and self.api_port == self.port:
            # This is fine - same port for API and base
            pass

        # Validate rate limiting settings
        if self.enable_rate_limiting and self.rate_limit_requests <= 0:
            msg = "Rate limit requests must be positive when rate limiting is enabled"
            raise ValueError(msg)

        return self

    # =========================================================================
    # CONFIGURATION METHODS
    # =========================================================================

    def get_server_config(self) -> FlextResult[FlextTypes.Core.Dict]:
        """Get server configuration as dictionary.

        Returns:
            FlextResult[FlextTypes.Core.Dict]: Server configuration data.

        """
        data: FlextTypes.Core.Dict = {
            "host": self.api_host,
            "port": self.api_port,
            "workers": self.workers,
            "debug": self.api_debug,
        }
        return FlextResult[FlextTypes.Core.Dict].ok(data)

    def get_client_config(self) -> FlextResult[FlextTypes.Core.Dict]:
        """Get client configuration as dictionary.

        Returns:
            FlextResult[FlextTypes.Core.Dict]: Client configuration data.

        """
        data: FlextTypes.Core.Dict = {
            "base_url": self.api_base_url,
            "timeout": self.default_timeout,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
        }
        return FlextResult[FlextTypes.Core.Dict].ok(data)

    def get_cors_config(self) -> FlextResult[FlextTypes.Core.Dict]:
        """Get CORS configuration as dictionary.

        Returns:
            FlextResult[FlextTypes.Core.Dict]: CORS configuration data.

        """
        data: FlextTypes.Core.Dict = {
            "allow_origins": list(self.cors_origins),
            "allow_methods": list(self.cors_methods),
            "allow_headers": list(self.cors_headers),
            "allow_credentials": self.cors_credentials,
        }
        return FlextResult[FlextTypes.Core.Dict].ok(data)

    def get_rate_limit_config(self) -> FlextResult[FlextTypes.Core.Dict]:
        """Get rate limiting configuration as dictionary.

        Returns:
            FlextResult[FlextTypes.Core.Dict]: Rate limiting configuration data.

        """
        data: FlextTypes.Core.Dict = {
            "enabled": self.enable_rate_limiting,
            "requests_per_window": self.rate_limit_requests,
            "window_seconds": self.rate_limit_window,
        }
        return FlextResult[FlextTypes.Core.Dict].ok(data)

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate API-specific business rules extending base validation.

        Returns:
            FlextResult indicating validation success or failure

        """
        try:
            # Call parent validation first
            base_validation = super().validate_business_rules()
            if base_validation.is_failure:
                return base_validation

            # Execute API-specific validations
            validations = [
                self._validate_server_settings(),
                self._validate_client_settings(),
                self._validate_cors_settings(),
                self._validate_rate_limiting(),
            ]

            # Return first failure or success if all pass
            for validation in validations:
                if validation.is_failure:
                    return validation

            return FlextResult[None].ok(None)

        except Exception as e:
            return FlextResult[None].fail(f"API configuration validation failed: {e}")

    def _validate_server_settings(self) -> FlextResult[None]:
        """Validate server configuration values."""
        if self.workers <= 0:
            return FlextResult[None].fail("Workers must be positive")

        if self.api_port <= 0 or self.api_port > 65535:
            return FlextResult[None].fail("API port must be between 1 and 65535")

        return FlextResult[None].ok(None)

    def _validate_client_settings(self) -> FlextResult[None]:
        """Validate client configuration values."""
        if self.default_timeout <= 0:
            return FlextResult[None].fail("Default timeout must be positive")

        if self.max_retries < 0:
            return FlextResult[None].fail("Max retries cannot be negative")

        return FlextResult[None].ok(None)

    def _validate_cors_settings(self) -> FlextResult[None]:
        """Validate CORS configuration values."""
        if not self.cors_origins:
            return FlextResult[None].fail("CORS origins cannot be empty")

        if not self.cors_methods:
            return FlextResult[None].fail("CORS methods cannot be empty")

        return FlextResult[None].ok(None)

    def _validate_rate_limiting(self) -> FlextResult[None]:
        """Validate rate limiting configuration."""
        if self.enable_rate_limiting:
            if self.rate_limit_requests <= 0:
                return FlextResult[None].fail("Rate limit requests must be positive when enabled")

            if self.rate_limit_window <= 0:
                return FlextResult[None].fail("Rate limit window must be positive when enabled")

        return FlextResult[None].ok(None)

    # =========================================================================
    # FACTORY METHODS
    # =========================================================================

    @classmethod
    def create_for_environment(
        cls, environment: str = "development", **overrides: object
    ) -> FlextResult[FlextApiConfig]:
        """Create configuration using flext-core FlextConfig.create_from_environment with API-specific validation.

        Args:
            environment: Environment name (development, production, etc.)
            **overrides: Parameter overrides that can change behavior

        Returns:
            FlextResult containing FlextApiConfig instance

        """
        # Use flext-core FlextConfig.create_from_environment directly
        extra_settings = dict(overrides)
        extra_settings["environment"] = environment

        result = cls.create_from_environment(extra_settings=extra_settings)
        if result.is_failure:
            return result

        # Validate the created configuration
        config = result.value
        validation_result = config.validate_business_rules()
        if validation_result.is_failure:
            return FlextResult[FlextApiConfig].fail(validation_result.error or "Configuration validation failed")

        return result

    @classmethod
    def create_with_overrides(
        cls,
        api_host: str | None = None,
        api_port: int | None = None,
        workers: int | None = None,
        api_debug: bool | None = None,
        environment: str = "development",
        **additional_overrides: object
    ) -> FlextResult[FlextApiConfig]:
        """Create configuration with specific parameter overrides.

        Args:
            api_host: Override API host
            api_port: Override API port
            workers: Override number of workers
            api_debug: Override debug mode
            environment: Environment name
            **additional_overrides: Additional parameter overrides

        Returns:
            FlextResult containing FlextApiConfig instance

        """
        overrides = dict(additional_overrides)

        # Apply parameter overrides if provided
        if api_host is not None:
            overrides["api_host"] = api_host
        if api_port is not None:
            overrides["api_port"] = api_port
        if workers is not None:
            overrides["workers"] = workers
        if api_debug is not None:
            overrides["api_debug"] = api_debug

        return cls.create_for_environment(environment, **overrides)

    # =============================================================================
    # SINGLETON GLOBAL INSTANCE METHODS
    # =============================================================================

    @classmethod
    def get_global_instance(cls) -> FlextApiConfig:
        """Get the SINGLETON GLOBAL API configuration instance.

        This method ensures a single source of truth for API configuration
        across the entire application. It loads configuration from multiple sources:
        1. Default values defined in Field()
        2. Environment variables with FLEXT_API_ prefix
        3. Explicitly set values

        Returns:
            FlextApiConfig: The global API configuration instance

        """
        if cls._global_instance is None:
            cls._global_instance = cls._load_from_sources()
        return cls._global_instance

    @classmethod
    def _load_from_sources(cls) -> FlextApiConfig:
        """Load API configuration from all available sources.

        Priority (lowest to highest):
        1. Default values in model
        2. Environment variables with FLEXT_API_ prefix (highest priority)

        Returns:
            FlextApiConfig: Loaded configuration instance

        """
        # Create instance with default values and environment variables
        return cls()

    @classmethod
    def set_global_instance(cls, config: FlextConfig) -> None:
        """Set the global API configuration instance.

        Args:
            config: API configuration instance to set as global

        """
        if isinstance(config, FlextApiConfig):
            cls._global_instance = config
        else:
            # Convert base config to API config
            cls._global_instance = FlextApiConfig(**config.model_dump())

    @classmethod
    def clear_global_instance(cls) -> None:
        """Clear the global API configuration instance."""
        cls._global_instance = None

    @classmethod
    def get_or_create_global(
        cls, environment: str = "development", **overrides: object
    ) -> FlextResult[FlextApiConfig]:
        """Get or create global API configuration with overrides.

        This method ensures a single source of truth for API configuration
        while allowing parameter overrides to change behavior.

        Args:
            environment: Environment name for configuration
            **overrides: Configuration parameter overrides

        Returns:
            FlextResult containing FlextApiConfig instance

        """
        # Try to get existing global instance
        if cls._global_instance is not None and not overrides:
            return FlextResult[FlextApiConfig].ok(cls._global_instance)

        # Create new instance with overrides
        result = cls.create_for_environment(environment, **overrides)
        if result.is_success:
            # Set as global instance
            cls.set_global_instance(result.value)

        return result

    # =========================================================================
    # LEGACY COMPATIBILITY METHODS
    # =========================================================================

    @classmethod
    def from_env(cls) -> FlextResult[FlextApiConfig]:
        """Create configuration from environment variables (legacy method).

        Returns:
            FlextResult containing FlextApiConfig instance

        """
        return cls.create_for_environment()

    @classmethod
    def default(cls) -> FlextApiConfig:
        """Create default configuration (legacy method).

        Returns:
            FlextApiConfig: Default configuration instance

        """
        return cls.get_global_instance()

    # Legacy aliases removed to avoid Pydantic field conflicts
    # Use api_host, api_port, api_debug, api_base_url directly


__all__ = ["FlextApiConfig"]
