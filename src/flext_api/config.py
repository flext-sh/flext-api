"""FLEXT API Configuration - Settings using flext-core patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import ClassVar

from pydantic import Field, field_validator
from pydantic_settings import SettingsConfigDict

from flext_api.constants import FlextApiConstants
from flext_api.models import FlextApiModels
from flext_core import FlextConfig, FlextModels, FlextResult


class FlextApiConfig(FlextConfig):
    """Simple API configuration extending flext-core FlextConfig."""

    # Singleton pattern for global instance

    model_config = SettingsConfigDict(
        env_prefix="FLEXT_API_", env_file=".env", extra="ignore"
    )

    # Server configuration - consolidated to remove duplication
    api_host: str = "127.0.0.1"
    api_port: int = Field(default=8000, ge=1, le=65535)
    workers: int = Field(default=4, ge=1)
    api_debug: bool = False

    # API configuration - consolidated base URLs
    api_title: str = "FLEXT API"
    api_version: str = "0.9.0"
    api_base_url: str = FlextApiConstants.DEFAULT_BASE_URL

    # Client configuration - consolidated timeout
    api_timeout: float = FlextApiConstants.DEFAULT_TIMEOUT
    max_retries: int = FlextApiConstants.DEFAULT_RETRIES

    # CORS configuration
    cors_origins: ClassVar[list[str]] = ["*"]
    cors_methods: ClassVar[list[str]] = ["GET", "POST", "PUT", "DELETE"]
    cors_headers: ClassVar[list[str]] = ["Content-Type", "Authorization"]
    cors_allow_credentials: bool = True

    @field_validator("api_base_url")
    @classmethod
    def validate_api_base_url(cls, v: str) -> str:
        """Validate API base URL using centralized FlextModels validation."""
        # Use centralized FlextModels validation instead of duplicate logic
        validation_result = FlextModels.create_validated_http_url(v.strip())
        if validation_result.is_failure:
            error_msg = f"Invalid API base URL: {validation_result.error}"
            raise ValueError(error_msg)
        return validation_result.unwrap()

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, value: str) -> str:
        """Validate base URL using centralized FlextModels validation."""
        # Use centralized FlextModels validation instead of duplicate logic
        validation_result = FlextModels.create_validated_http_url(
            value.strip() if value else ""
        )
        if validation_result.is_failure:
            error_msg = f"Invalid base URL: {validation_result.error}"
            raise ValueError(error_msg)
        return validation_result.unwrap()

    @classmethod
    def get_global_instance(cls) -> FlextApiConfig:
        """Get global configuration instance."""
        if cls._global_instance is None or not isinstance(
            cls._global_instance, FlextApiConfig
        ):
            cls._global_instance = cls()
        return cls._global_instance

    @classmethod
    def set_global_instance(cls, config: FlextConfig | None) -> None:
        """Set global configuration instance."""
        if config is None:
            cls._global_instance = None
        elif isinstance(config, FlextApiConfig):
            cls._global_instance = config
        else:
            error_msg = "Expected FlextApiConfig instance"
            raise TypeError(error_msg)

    def validate_configuration(self) -> FlextResult[None]:
        """Validate configuration values."""
        if self.workers <= 0:
            return FlextResult[None].fail("Workers must be positive")

        if self.api_port <= 0 or self.api_port > FlextApiConstants.MAX_PORT:
            return FlextResult[None].fail(
                f"API port must be between 1 and {FlextApiConstants.MAX_PORT}"
            )

        return FlextResult[None].ok(None)

    def get_server_config(self) -> FlextResult[dict[str, str | int | bool]]:
        """Get server configuration."""
        return FlextResult[dict[str, str | int | bool]].ok(
            {
                "host": self.api_host,
                "port": self.api_port,
                "workers": self.workers,
                "debug": self.api_debug,
            }
        )

    def get_client_config(self) -> FlextResult[dict[str, str | float | int]]:
        """Get client configuration."""
        return FlextResult[dict[str, str | float | int]].ok(
            {
                "base_url": self.api_base_url,
                "timeout": self.api_timeout,
                "max_retries": self.max_retries,
            }
        )

    def get_cors_config(self) -> FlextResult[dict[str, list[str] | bool]]:
        """Get CORS configuration."""
        return FlextResult[dict[str, list[str] | bool]].ok(
            {
                "allow_origins": self.cors_origins,
                "allow_methods": self.cors_methods,
                "allow_headers": self.cors_headers,
                "allow_credentials": self.cors_allow_credentials,
            }
        )

    # Removed unnecessary getter methods - direct attribute access preferred

    def get_default_headers(self) -> dict[str, str]:
        """Get default headers."""
        return {
            "User-Agent": f"FlextAPI/{self.api_version}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    @classmethod
    def create_with_overrides(cls, **overrides: object) -> FlextResult[FlextApiConfig]:
        """Create configuration with parameter overrides."""
        try:
            # Create a new instance with default values first
            config = cls()

            # Apply overrides by updating the instance attributes
            for key, value in overrides.items():
                if hasattr(config, key):
                    setattr(config, key, value)

            return FlextResult["FlextApiConfig"].ok(config)
        except Exception as e:
            return FlextResult["FlextApiConfig"].fail(
                f"Configuration creation failed: {e}"
            )

    class _BackwardCompatibility:
        """Nested backward compatibility class for FLEXT compliance - no loose functions."""

        @staticmethod
        def get_client_config() -> type:
            """Get client config class."""
            return FlextApiModels.ClientConfig

    # Backward compatibility alias - add after class definition


# Backward compatibility exports - FLEXT unified class pattern
# Simple alias following venv_consistency.py pattern
setattr(FlextApiConfig, "ClientConfig", FlextApiModels.ClientConfig)

__all__ = [
    "FlextApiConfig",
]
