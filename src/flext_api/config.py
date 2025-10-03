"""FLEXT API Configuration - Settings using flext-core patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pydantic import Field, computed_field
from pydantic_settings import SettingsConfigDict

from flext_api.constants import FlextApiConstants
from flext_core import FlextConfig, FlextResult, FlextTypes


class FlextApiConfig(FlextConfig):
    """Single Pydantic Settings class for flext-api extending FlextConfig.

    Uses enhanced FlextConfig features:
    - Protocol inheritance (Infrastructure.Configurable)
    - Computed fields for derived configuration
    - Enhanced validation with field_validator and model_validator
    - Type-safe configuration management
    - Business rule validation
    - Configuration persistence

    All defaults from FlextApiConstants with FlextConfig enhancements.
    """

    model_config = SettingsConfigDict(
        env_prefix="FLEXT_API_",
        case_sensitive=False,
        extra="allow",
        # Enhanced Pydantic 2.11+ features from FlextConfig
        validate_assignment=True,
        str_strip_whitespace=True,
        str_to_lower=False,
        json_schema_extra={
            "title": "FLEXT API Configuration",
            "description": "Enterprise API configuration with FlextConfig protocol support",
        },
    )

    # API Configuration using FlextApiConstants for defaults
    base_url: str = Field(
        default=FlextApiConstants.DEFAULT_BASE_URL,
        description="Base URL for API requests",
    )

    timeout: int = Field(
        default=FlextApiConstants.DEFAULT_TIMEOUT,
        ge=1,
        le=300,
        description="Request timeout in seconds",
    )

    max_retries: int = Field(
        default=FlextApiConstants.DEFAULT_MAX_RETRIES,
        ge=0,
        le=10,
        description="Maximum number of retries for failed requests",
    )

    api_version: str = Field(
        default=FlextApiConstants.API_VERSION,
        description="API version string",
    )

    # Logging configuration
    log_requests: bool = Field(
        default=True,
        description="Enable request logging",
    )

    log_responses: bool = Field(
        default=True,
        description="Enable response logging",
    )

    # CORS configuration
    cors_origins: FlextTypes.StringList = Field(
        default_factory=lambda: ["*"],
        description="CORS allowed origins",
    )

    cors_methods: FlextTypes.StringList = Field(
        default_factory=lambda: ["GET", "POST", "PUT", "DELETE"],
        description="CORS allowed methods",
    )

    cors_headers: FlextTypes.StringList = Field(
        default_factory=lambda: ["Content-Type", "Authorization"],
        description="CORS allowed headers",
    )

    @computed_field
    @property
    def api_url(self) -> str:
        """Get complete API URL with version."""
        return f"{self.base_url}/api/{self.api_version}"

    # =========================================================================
    # Infrastructure Protocol Implementations (FlextConfig inheritance)
    # =========================================================================

    def configure(self, config: FlextTypes.Dict) -> FlextResult[None]:
        """Configure API settings with provided configuration.

        Implements Infrastructure.Configurable protocol from FlextConfig.

        Args:
            config: Configuration dictionary to apply

        Returns:
            FlextResult[None]: Success if configuration valid, failure otherwise

        """
        try:
            # Apply API-specific configuration
            for key, value in config.items():
                if hasattr(self, key) and key in {
                    "base_url", "timeout", "max_retries", "api_version",
                    "log_requests", "log_responses", "cors_origins",
                    "cors_methods", "cors_headers"
                }:
                    setattr(self, key, value)

            # Call parent configure for core configuration
            return super().configure(config)
        except Exception as e:
            return FlextResult[None].fail(f"API configuration failed: {e}")

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate API-specific business rules for configuration consistency.

        Extends Infrastructure.ConfigValidator protocol from FlextConfig.

        Returns:
            FlextResult[None]: Success if valid, failure with error details

        """
        # Call parent business rules validation first
        parent_result = super().validate_business_rules()
        if parent_result.is_failure:
            return parent_result

        # API-specific business rules
        if self.is_production():
            # Production API validation - use constants for magic values
            max_prod_timeout = 60  # seconds
            max_prod_retries = 5

            if not self.base_url or not self.base_url.startswith(('https://', 'http://')):
                return FlextResult[None].fail(
                    "Production API requires valid base_url starting with http:// or https://"
                )

            if self.timeout > max_prod_timeout:
                return FlextResult[None].fail(
                    f"Production API timeout too high: {self.timeout}s (max: {max_prod_timeout}s)"
                )

            if self.max_retries > max_prod_retries:
                return FlextResult[None].fail(
                    f"Production API max_retries too high: {self.max_retries} (max: {max_prod_retries})"
                )

        # Development validation - combine nested if statements
        if self.is_development() and self.base_url and self.base_url.startswith('https://') and self.debug:
            # Allow HTTPS in development for testing, but warn via logging
            pass

        return FlextResult[None].ok(None)

    @classmethod
    def create_for_environment(
        cls, environment: str, **overrides: object
    ) -> FlextApiConfig:
        """Create configuration for specific environment using direct instantiation.

        Migration from old singleton pattern to new FlextConfig direct instantiation.
        """
        return cls(environment=environment, **overrides)

    @classmethod
    def create_default(cls) -> FlextApiConfig:
        """Create default configuration instance using direct instantiation.

        Migration from old singleton pattern to new FlextConfig direct instantiation.
        """
        return cls()

    @classmethod
    def get_global_instance(cls) -> FlextApiConfig:
        """REMOVED: Use direct instantiation with FlextApiConfig().

        Migration:
            # Old pattern
            config = FlextApiConfig.get_global_instance()

            # New pattern - create instance directly
            config = FlextApiConfig()
        """
        msg = (
            "FlextApiConfig.get_global_instance() has been removed. "
            "Use FlextApiConfig() to create instances directly."
        )
        raise NotImplementedError(msg)

    @classmethod
    def reset_global_instance(cls) -> None:
        """REMOVED: Singleton pattern removed in favor of direct instantiation.

        Migration:
            # Old pattern - no longer needed
            FlextApiConfig.reset_global_instance()

            # New pattern - create fresh instances as needed
            config = FlextApiConfig()
        """
        msg = (
            "FlextApiConfig.reset_global_instance() has been removed. "
            "Create new instances directly with FlextApiConfig()."
        )
        raise NotImplementedError(msg)


__all__ = [
    "FlextApiConfig",
]
