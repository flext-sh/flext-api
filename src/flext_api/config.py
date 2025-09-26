"""FLEXT API Configuration - Settings using flext-core patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import threading
from typing import ClassVar

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

    # Singleton pattern attributes
    _global_instance: ClassVar[FlextApiConfig | None] = None
    _lock: ClassVar[threading.Lock] = threading.Lock()

    model_config = SettingsConfigDict(
        env_prefix="FLEXT_API_",
        case_sensitive=False,
        extra="allow",
    )

    # Class-level CORS configuration for backward compatibility
    cors_origins: ClassVar[list[str]] = ["*"]
    cors_methods: ClassVar[list[str]] = ["GET", "POST", "PUT", "DELETE"]
    cors_headers: ClassVar[list[str]] = ["Content-Type", "Authorization"]

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

    # Instance CORS configuration (inherits from ClassVar defaults)
    cors_origins_instance: list[str] = Field(
        default_factory=lambda: ["*"],
        description="CORS allowed origins",
        alias="cors_origins",
    )

    cors_methods_instance: list[str] = Field(
        default_factory=lambda: ["GET", "POST", "PUT", "DELETE"],
        description="CORS allowed methods",
        alias="cors_methods",
    )

    cors_headers_instance: list[str] = Field(
        default_factory=lambda: ["Content-Type", "Authorization"],
        description="CORS allowed headers",
        alias="cors_headers",
    )

    @computed_field
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

    def get_default_headers(self) -> dict[str, str]:
        """Get default HTTP headers for API requests."""
        return {
            "User-Agent": f"flext-api/{self.api_version}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    @classmethod
    def create_for_environment(
        cls, environment: str, **overrides: object
    ) -> FlextApiConfig:
        """Create configuration for specific environment."""
        return cls(environment=environment, **overrides)

    @classmethod
    def create_default(cls) -> FlextApiConfig:
        """Create default configuration instance."""
        return cls()

    # Singleton pattern override for proper typing
    @classmethod
    def get_global_instance(cls) -> FlextApiConfig:
        """Get the global singleton instance of FlextApiConfig."""
        if cls._global_instance is None:
            with cls._lock:
                if cls._global_instance is None:
                    cls._global_instance = cls()
        return cls._global_instance

    @classmethod
    def reset_global_instance(cls) -> None:
        """Reset the global FlextApiConfig instance (mainly for testing)."""
        cls._global_instance = None


__all__ = [
    "FlextApiConfig",
]
