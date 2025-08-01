"""FLEXT API configuration module.

Provides configuration management for FLEXT API services using flext-core patterns.
Implements Single Responsibility Principle with specific API-focused settings.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core import FlextBaseSettings, FlextConstants, FlextResult
from pydantic import Field, field_validator

if TYPE_CHECKING:
    from flext_core.flext_types import TAnyDict


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


def create_api_settings(**overrides: object) -> FlextResult[FlextApiSettings]:
    """Factory function for creating API settings with overrides.

    Follows Factory Pattern and Open/Closed Principle.
    Uses FlextResult for consistent error handling.
    Uses FlextBaseSettings.create_with_validation for proper validation.

    Args:
        **overrides: Configuration overrides to apply

    Returns:
        FlextResult containing validated FlextApiSettings instance

    """
    # Convert overrides to dict format for create_with_validation
    overrides_dict: TAnyDict = dict(overrides) if overrides else {}

    # Use the correct method from FlextBaseSettings
    result = FlextApiSettings.create_with_validation(overrides_dict)

    # Type narrowing for MyPy - we know this returns FlextApiSettings
    if result.is_success and isinstance(result.data, FlextApiSettings):
        return FlextResult.ok(result.data)

    return FlextResult.fail(result.error or "Failed to create API settings")
