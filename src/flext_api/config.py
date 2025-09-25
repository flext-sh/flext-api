"""FLEXT API Configuration - Settings using flext-core patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pydantic import Field, computed_field
from pydantic_settings import SettingsConfigDict

from flext_api.constants import FlextApiConstants
from flext_core import FlextConfig


class FlextApiConfig(FlextConfig):
    """Single Pydantic 2 Settings class for flext-api extending FlextConfig.

    Follows standardized pattern:
    - Extends FlextConfig from flext-core
    - No nested classes within Config
    - All defaults from FlextApiConstants
    - Dependency injection integration with flext-core container
    - Uses Pydantic 2.11+ features (field_validator, model_validator)
    """

    model_config = SettingsConfigDict(
        env_prefix="FLEXT_API_",
        case_sensitive=False,
        extra="allow",
    )

    # API Configuration using FlextApiConstants for defaults
    base_url: str = Field(
        default=FlextApiConstants.DEFAULT_BASE_URL,
        description="Base URL for API requests",
    )

    # Legacy compatibility fields
    api_base_url: str = Field(
        default=FlextApiConstants.DEFAULT_BASE_URL,
        description="API base URL (legacy compatibility)",
    )

    timeout: int = Field(
        default=FlextApiConstants.DEFAULT_TIMEOUT,
        ge=1,
        le=300,
        description="Request timeout in seconds",
    )

    # Legacy compatibility fields
    api_timeout: int = Field(
        default=FlextApiConstants.DEFAULT_TIMEOUT,
        ge=1,
        le=300,
        description="API timeout (legacy compatibility)",
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

    @computed_field  # type: ignore[misc]
    @property
    def api_url(self) -> str:
        """Get complete API URL."""
        return f"{self.base_url}/api/{self.api_version}"

    # API-specific methods
    def get_client_config(self) -> dict[str, object]:
        """Get API client configuration."""
        return {
            "base_url": self.base_url,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "api_version": self.api_version,
        }

    @classmethod
    def create_for_environment(
        cls, environment: str, **overrides: object
    ) -> FlextApiConfig:
        """Create configuration for specific environment."""
        return cls(environment=environment, **overrides)


__all__ = [
    "FlextApiConfig",
]
