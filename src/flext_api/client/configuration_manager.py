"""Configuration Management for FlextApiClient.

This module contains configuration-related functionality extracted from FlextApiClient
to improve maintainability and separation of concerns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextCore

from flext_api.config import FlextApiConfig
from flext_api.constants import FlextApiConstants
from flext_api.models import FlextApiModels
from flext_api.typings import FlextApiTypes


class ConfigurationManager:
    """Configuration management functionality for FlextApiClient."""

    def __init__(self) -> None:
        """Initialize configuration manager."""
        self._config: FlextApiConfig | None = None

    @property
    def config(self) -> FlextApiConfig:
        """Get current configuration."""
        if self._config is None:
            self._config = FlextApiConfig()
        return self._config

    @config.setter
    def config(self, value: FlextApiConfig) -> None:
        """Set configuration."""
        self._config = value

    def configure(
        self, config: FlextApiConfig | dict[str, object] | None = None
    ) -> FlextCore.Result[None]:
        """Configure the HTTP client with provided configuration.

        Args:
            config: Configuration object, dictionary, or None for defaults

        Returns:
            FlextCore.Result indicating success or failure

        """
        try:
            if config is None:
                self._config = FlextApiConfig()
            elif isinstance(config, dict):
                # Convert dict to FlextApiConfig
                self._config = FlextApiConfig(**config)
            elif isinstance(config, FlextApiConfig):
                self._config = config
            else:
                return FlextCore.Result[None].fail(
                    f"Invalid configuration type: {type(config)}. "
                    "Expected FlextApiConfig, dict, or None."
                )

            # Validate configuration
            validation_result = self._validate_configuration()
            if validation_result.is_failure:
                return validation_result

            return FlextCore.Result[None].ok(None)

        except Exception as e:
            return FlextCore.Result[None].fail(f"Configuration failed: {e}")

    def _validate_configuration(self) -> FlextCore.Result[None]:
        """Validate current configuration."""
        if self._config is None:
            return FlextCore.Result[None].fail("No configuration set")

        try:
            # Validate base URL
            if self._config.base_url and hasattr(FlextApiModels, "HttpRequest"):
                # Try to create a test request to validate URL
                FlextApiModels.HttpRequest(
                    method="GET",
                    url=self._config.base_url,
                    timeout=self._config.timeout,
                )
                # If we get here without exception, URL is valid

            # Validate timeout
            if self._config.timeout <= 0:
                return FlextCore.Result[None].fail("Timeout must be positive")

            # Validate max retries
            if self._config.max_retries < 0:
                return FlextCore.Result[None].fail("Max retries cannot be negative")

            return FlextCore.Result[None].ok(None)

        except Exception as e:
            return FlextCore.Result[None].fail(f"Configuration validation failed: {e}")

    def get_client_config(self) -> FlextApiTypes.ConfigDict:
        """Get client configuration dictionary for HTTP operations."""
        if self._config is None:
            return {}

        return {
            "base_url": self._config.base_url,
            "timeout": self._config.timeout,
            "max_retries": self._config.max_retries,
            "headers": self._get_default_headers(),
        }

    def _get_default_headers(self) -> dict[str, str]:
        """Get default headers from configuration."""
        headers = {}

        if self._config and hasattr(self._config, "get_default_headers"):
            headers = self._config.get_default_headers()

        # Add any additional default headers
        if "User-Agent" not in headers:
            headers["User-Agent"] = f"FlextApi/{FlextApiConstants.API_VERSION}"

        if "Accept" not in headers:
            headers["Accept"] = "application/json"

        return headers

    def merge_config(self, updates: dict[str, object]) -> FlextCore.Result[None]:
        """Merge configuration updates into current config.

        Args:
            updates: Dictionary of configuration updates

        Returns:
            FlextCore.Result indicating success or failure

        """
        try:
            if self._config is None:
                self._config = FlextApiConfig()

            # Update configuration attributes
            for key, value in updates.items():
                if hasattr(self._config, key):
                    setattr(self._config, key, value)
                else:
                    return FlextCore.Result[None].fail(
                        f"Unknown configuration key: {key}"
                    )

            # Re-validate configuration
            return self._validate_configuration()

        except Exception as e:
            return FlextCore.Result[None].fail(f"Configuration merge failed: {e}")

    def reset_config(self) -> FlextCore.Result[None]:
        """Reset configuration to defaults."""
        try:
            self._config = FlextApiConfig()
            return FlextCore.Result[None].ok(None)
        except Exception as e:
            return FlextCore.Result[None].fail(f"Configuration reset failed: {e}")

    def get_config_summary(self) -> dict[str, object]:
        """Get configuration summary for debugging/logging."""
        if self._config is None:
            return {"status": "unconfigured"}

        return {
            "status": "configured",
            "base_url": self._config.base_url,
            "timeout": self._config.timeout,
            "max_retries": self._config.max_retries,
            "has_cors_config": bool(self._config.cors_origins),
            "structured_logging": getattr(self._config, "structured_output", False),
        }


__all__ = ["ConfigurationManager"]
