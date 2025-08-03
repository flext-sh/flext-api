"""API configuration settings management.

Configuration class extending FlextBaseSettings for API server settings.
Provides basic settings for host, port, timeouts, and caching with
environment variable support through FLEXT_API_ prefix.

Main classes:
    - FlextApiSettings: API server and client configuration settings
    - create_api_settings(): Factory function for creating settings with validation

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_core import FlextBaseSettings, FlextConstants, FlextResult
from pydantic import Field, field_validator


class FlextApiSettings(FlextBaseSettings):
    """API-specific configuration settings extending flext-core patterns.

    Follows Single Responsibility Principle by handling only API configuration.
    Uses Dependency Inversion Principle by depending on FlextBaseSettings abstraction.
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

    @classmethod
    def create_with_validation(
        cls,
        overrides: dict[str, object] | None = None,
        **kwargs: object,
    ) -> FlextResult[FlextBaseSettings]:
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
        except Exception as e:
            return FlextResult.fail(f"Failed to create settings: {e}")


def create_api_settings(**overrides: object) -> FlextResult[FlextApiSettings]:
    """Factory function for creating API settings with overrides.

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
