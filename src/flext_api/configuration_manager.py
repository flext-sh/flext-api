"""FLEXT API Configuration Manager - Standalone configuration management module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_api.models import FlextApiModels
from flext_core import FlextLogger, FlextResult


class FlextApiConfigurationManager:
    """Configuration manager for FlextApiClient.

    Manages client configuration, validation, and updates.
    Follows FLEXT "one class per module" architectural principle.
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

    @property
    def headers(self) -> dict[str, str]:
        """Get headers from the underlying configuration."""
        return self._config.headers

    def update_configuration(
        self, new_config: FlextApiModels.ClientConfig
    ) -> FlextResult[None]:
        """Update configuration with new values.

        Args:
            new_config: New configuration to apply

        Returns:
            FlextResult indicating success or failure

        """
        try:
            # Validate new configuration
            validation_result = self.validate_configuration(new_config)
            if validation_result.is_failure:
                return validation_result

            # Update configuration
            self._config = new_config
            self._logger.info("Configuration updated successfully")

            return FlextResult[None].ok(None)
        except Exception as e:
            error_msg = f"Configuration update failed: {e}"
            self._logger.error(error_msg)
            return FlextResult[None].fail(error_msg)

    def get_configuration_dict(self) -> dict[str, object]:
        """Get current configuration as dictionary.

        Returns:
            Dictionary representation of current configuration

        """
        return self._config.model_dump()

    def validate_configuration(
        self, config: FlextApiModels.ClientConfig
    ) -> FlextResult[None]:
        """Validate configuration object.

        Args:
            config: Configuration to validate

        Returns:
            FlextResult indicating validation success or failure

        """
        try:
            # Validate base URL
            url_result = config.validate_base_url()
            if url_result.is_failure:
                return url_result

            # Additional validation logic can be added here
            self._logger.debug("Configuration validation successful")
            return FlextResult[None].ok(None)

        except Exception as e:
            error_msg = f"Configuration validation failed: {e}"
            self._logger.error(error_msg)
            return FlextResult[None].fail(error_msg)

    def reset_to_defaults(self) -> FlextResult[None]:
        """Reset configuration to default values.

        Returns:
            FlextResult indicating success or failure

        """
        try:
            # Create default configuration
            default_config = FlextApiModels.ClientConfig()
            self._config = default_config
            self._logger.info("Configuration reset to defaults")

            return FlextResult[None].ok(None)
        except Exception as e:
            error_msg = f"Configuration reset failed: {e}"
            self._logger.error(error_msg)
            return FlextResult[None].fail(error_msg)


__all__ = ["FlextApiConfigurationManager"]
