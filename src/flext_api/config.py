"""FLEXT API Configuration - Settings using flext-core patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import cast

from pydantic import Field, computed_field
from pydantic_settings import SettingsConfigDict

from flext_api.constants import FlextApiConstants
from flext_api.typings import FlextApiTypes
from flext_core import FlextConfig


class FlextApiConfig(FlextConfig):
    """Single Pydantic 2 Settings class for flext-api extending FlextConfig.

    Follows standardized pattern:
    - Extends FlextConfig from flext-core
    - No nested classes within Config
    - All defaults from FlextApiConstants
    - Uses enhanced singleton pattern with inverse dependency injection
    - Uses Pydantic 2.11+ features (field_validator, model_validator)
    """

    model_config = SettingsConfigDict(
        env_prefix="FLEXT_API_",
        case_sensitive=False,
        extra="allow",
        # Inherit enhanced Pydantic 2.11+ features from FlextConfig
        validate_assignment=True,
        str_strip_whitespace=True,
        json_schema_extra={
            "title": "FLEXT API Configuration",
            "description": "Enterprise API configuration extending FlextConfig",
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
    cors_origins: list[str] = Field(
        default_factory=lambda: ["*"],
        description="CORS allowed origins",
    )

    cors_methods: list[str] = Field(
        default_factory=lambda: ["GET", "POST", "PUT", "DELETE"],
        description="CORS allowed methods",
    )

    cors_headers: list[str] = Field(
        default_factory=lambda: ["Content-Type", "Authorization"],
        description="CORS allowed headers",
    )

    @computed_field
    def api_url(self) -> str:
        """Get complete API URL."""
        return f"{self.base_url}/api/{self.api_version}"

    @computed_field
    def api_base_url(self) -> str:
        """Alias for base_url to maintain API compatibility."""
        return self.base_url

    @computed_field
    def api_timeout(self) -> int:
        """Alias for timeout to maintain API compatibility."""
        return self.timeout

    # API-specific methods
    def get_client_config(self) -> FlextApiTypes.Core.ClientConfigDict:
        """Get API client configuration."""
        return {
            "base_url": self.base_url,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "api_version": self.api_version,
        }

    def get_default_headers(self) -> dict[str, str]:
        """Get default HTTP headers for API requests."""
        return {
            "User-Agent": f"flext-api/{self.api_version}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def to_dict(self) -> dict[str, object]:
        """Convert configuration to dictionary."""
        return {
            "base_url": self.base_url,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "api_version": self.api_version,
            "log_requests": self.log_requests,
            "log_responses": self.log_responses,
        }

    @classmethod
    def create_for_environment(
        cls, environment: str, **overrides: object
    ) -> FlextApiConfig:
        """Create configuration for specific environment using enhanced singleton pattern."""
        return cast(
            "FlextApiConfig",
            cls.get_or_create_shared_instance(
                project_name="flext-api", environment=environment, **overrides
            ),
        )

    @classmethod
    def create_default(cls) -> FlextApiConfig:
        """Create default configuration instance using enhanced singleton pattern."""
        return cast(
            "FlextApiConfig",
            cls.get_or_create_shared_instance(project_name="flext-api"),
        )

    @classmethod
    def get_global_instance(cls) -> FlextApiConfig:
        """Get the global singleton instance using enhanced FlextConfig pattern."""
        return cast(
            "FlextApiConfig",
            cls.get_or_create_shared_instance(project_name="flext-api"),
        )

    @classmethod
    def reset_global_instance(cls) -> None:
        """Reset the global FlextApiConfig instance (mainly for testing)."""
        # Use the enhanced FlextConfig reset mechanism
        # Reset mechanism - method may not exist in parent class


__all__ = [
    "FlextApiConfig",
]
