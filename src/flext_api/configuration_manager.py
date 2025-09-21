"""FLEXT API Configuration Manager - Standalone configuration management module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_api.models import FlextApiModels
from flext_core import FlextLogger, FlextResult


class FlextApiConfigurationManager:
    """Configuration management service for FLEXT API client.

    Handles client configuration updates, validation, and retrieval with proper
    error handling through the FlextResult pattern.

    This class was extracted from the monolithic FlextApiClient to follow
    FLEXT "one class per module" architectural principle.
    """

    def __init__(
        self, config: FlextApiModels.ClientConfig, logger: FlextLogger
    ) -> None:
        """Initialize configuration manager with configuration and logger.

        Args:
            config: Client configuration instance to manage
            logger: Logger instance for configuration events

        """
        self._config = config
        self._logger = logger

    def update_configuration(self, updates: dict[str, str | int]) -> FlextResult[None]:
        """Update client configuration with new values.

        Args:
            updates: Dictionary of configuration keys and new values

        Returns:
            FlextResult indicating success or failure of configuration update.

        """
        try:
            for key, value in updates.items():
                if hasattr(self._config, key):
                    setattr(self._config, key, value)
                else:
                    return FlextResult[None].fail(f"Invalid config key: {key}")

            self._logger.info("Configuration updated", extra={"updates": updates})
            return FlextResult[None].ok(None)
        except Exception as e:
            error_msg = f"Configuration update failed: {e}"
            self._logger.exception(error_msg, extra={"updates": updates})
            return FlextResult[None].fail(error_msg)

    def get_configuration_dict(self) -> dict[str, str | int | float]:
        """Get configuration as dictionary for inspection.

        Returns:
            Dictionary containing current configuration values.

        """
        return {
            "base_url": self._config.base_url,
            "timeout": self._config.timeout,
            "max_retries": self._config.max_retries,
        }

    def validate_configuration(self) -> FlextResult[None]:
        """Validate current configuration for correctness.

        Checks that all required configuration values are present
        and have valid values.

        Returns:
            FlextResult indicating success or failure of configuration validation.

        """
        if not self._config.base_url:
            return FlextResult[None].fail("Base URL is required")

        if self._config.timeout <= 0:
            return FlextResult[None].fail("Timeout must be positive")

        if self._config.max_retries < 0:
            return FlextResult[None].fail("Max retries cannot be negative")

        # Additional validation for URL format
        if not self._config.base_url.startswith(("http://", "https://")):
            return FlextResult[None].fail("Base URL must be a valid HTTP/HTTPS URL")

        self._logger.debug(
            "Configuration validation passed",
            extra={
                "base_url": self._config.base_url,
                "timeout": self._config.timeout,
                "max_retries": self._config.max_retries,
            },
        )

        return FlextResult[None].ok(None)

    def reset_to_defaults(self) -> FlextResult[None]:
        """Reset configuration to default values.

        Returns:
            FlextResult indicating success or failure of configuration reset.

        """
        try:
            # Create new configuration with default values
            from flext_api.models import FlextApiModels

            self._config = FlextApiModels.ClientConfig(
                base_url="https://api.example.com",
                timeout=30,
                max_retries=3,
                headers={},
            )

            self._logger.info("Configuration reset to defaults")
            return FlextResult[None].ok(None)
        except Exception as e:
            error_msg = f"Configuration reset failed: {e}"
            self._logger.exception(error_msg)
            return FlextResult[None].fail(error_msg)


# Direct class access only - no backward compatibility aliases
__all__ = ["FlextApiConfigurationManager"]
