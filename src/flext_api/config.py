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
    """FLEXT API configuration extending flext-core FlextConfig.

    This configuration class provides comprehensive settings for FLEXT API
    operations including server configuration, client settings, and CORS
    policies. It extends FlextConfig to inherit core functionality while
    adding API-specific configuration options.

    The configuration supports:
    - Server settings (host, port, workers, debug mode)
    - API metadata (title, version, base URL)
    - Client configuration (timeout, retry settings)
    - CORS policies for web integration
    - Environment variable overrides

    Attributes:
        api_host: Server host address (default: "127.0.0.1").
        api_port: Server port number (default: 8000, range: 1-65535).
        workers: Number of worker processes (default: 4, minimum: 1).
        api_debug: Enable debug mode (default: False).
        api_title: API title for documentation (default: "FLEXT API").
        api_version: API version string (default: "0.9.0").
        api_base_url: Base URL for API endpoints.
        api_timeout: Request timeout in seconds.
        max_retries: Maximum retry attempts for failed requests.
        cors_origins: Allowed CORS origins.
        cors_methods: Allowed HTTP methods for CORS.
        cors_headers: Allowed headers for CORS.
        cors_allow_credentials: Whether to allow credentials in CORS.

    Example:
        >>> config = FlextApiConfig(api_host="0.0.0.0", api_port=8080, api_debug=True)
        >>> validation_result = config.validate_configuration()
        >>> if validation_result.is_success:
        ...     print("Configuration is valid")

    """

    # Singleton pattern for global instance

    model_config = SettingsConfigDict(
        env_prefix="FLEXT_API_", env_file=".env", extra="ignore",
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
        """Validate API base URL using centralized FlextModels validation.

        Validates the API base URL format and ensures it's a properly
        formatted HTTP or HTTPS URL.

        Args:
            v: URL string to validate.

        Returns:
            Validated and cleaned URL string.

        Raises:
            ValueError: If the URL format is invalid.

        """
        # Use centralized FlextModels validation instead of duplicate logic
        validation_result = FlextModels.create_validated_http_url(v.strip())
        if validation_result.is_failure:
            # Map flext-core error messages to expected test messages
            error_msg = validation_result.error or "Invalid API base URL"
            if "URL must start with http:// or https://" in error_msg:
                error_msg = "API base URL must include scheme and hostname"
            msg = f"Invalid API base URL: {error_msg}"
            raise ValueError(msg)
        return validation_result.unwrap()

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, value: str) -> str:
        """Validate base URL using centralized FlextModels validation.

        Validates the base URL format and ensures it's a properly
        formatted HTTP or HTTPS URL.

        Args:
            value: URL string to validate.

        Returns:
            Validated and cleaned URL string.

        Raises:
            ValueError: If the URL format is invalid.

        """
        # Use centralized FlextModels validation instead of duplicate logic
        validation_result = FlextModels.create_validated_http_url(
            value.strip() if value else "",
        )
        if validation_result.is_failure:
            error_msg = f"Invalid base URL: {validation_result.error}"
            raise ValueError(error_msg)
        return validation_result.unwrap()

    @classmethod
    def get_global_instance(cls) -> FlextApiConfig:
        """Get global configuration instance.

        Returns the singleton global instance of FlextApiConfig,
        creating it if it doesn't exist.

        Returns:
            Global FlextApiConfig instance.

        Example:
            >>> config = FlextApiConfig.get_global_instance()
            >>> print(f"Global config host: {config.api_host}")

        """
        if cls._global_instance is None or not isinstance(
            cls._global_instance, FlextApiConfig,
        ):
            cls._global_instance = cls()
        return cls._global_instance

    @classmethod
    def set_global_instance(cls, config: FlextConfig | None) -> None:
        """Set global configuration instance.

        Sets the singleton global instance of FlextApiConfig.

        Args:
            config: FlextApiConfig instance to set as global, or None to clear.

        Raises:
            TypeError: If config is not a FlextApiConfig instance.

        Example:
            >>> custom_config = FlextApiConfig(api_port=9000)
            >>> FlextApiConfig.set_global_instance(custom_config)

        """
        if config is None:
            cls._global_instance = None
        elif isinstance(config, FlextApiConfig):
            cls._global_instance = config
        else:
            error_msg = "Expected FlextApiConfig instance"
            raise TypeError(error_msg)

    def validate_configuration(self) -> FlextResult[None]:
        """Validate configuration values.

        Performs comprehensive validation of all configuration values
        to ensure they are within acceptable ranges and formats.

        Returns:
            FlextResult indicating validation success or failure with error details.

        Example:
            >>> config = FlextApiConfig(api_port=99999)
            >>> result = config.validate_configuration()
            >>> if result.is_failure:
            ...     print(f"Validation failed: {result.error}")

        """
        if self.workers <= 0:
            return FlextResult[None].fail("Workers must be positive")

        if self.api_port <= 0 or self.api_port > FlextApiConstants.MAX_PORT:
            return FlextResult[None].fail(
                f"API port must be between 1 and {FlextApiConstants.MAX_PORT}",
            )

        return FlextResult[None].ok(None)

    def get_server_config(self) -> FlextResult[dict[str, str | int | bool]]:
        """Get server configuration dictionary.

        Returns a dictionary containing all server-related configuration
        values for easy consumption by server components.

        Returns:
            FlextResult containing server configuration dictionary:
                - host: Server host address
                - port: Server port number
                - workers: Number of worker processes
                - debug: Debug mode flag

        Example:
            >>> result = config.get_server_config()
            >>> if result.is_success:
            ...     server_config = result.unwrap()
            ...     print(
            ...         f"Server will run on {server_config['host']}:{server_config['port']}"
            ...     )

        """
        return FlextResult[dict[str, str | int | bool]].ok(
            {
                "host": self.api_host,
                "port": self.api_port,
                "workers": self.workers,
                "debug": self.api_debug,
            },
        )

    def get_client_config(self) -> FlextResult[dict[str, str | float | int]]:
        """Get client configuration dictionary.

        Returns a dictionary containing all client-related configuration
        values for HTTP client initialization.

        Returns:
            FlextResult containing client configuration dictionary:
                - base_url: Base URL for requests
                - timeout: Request timeout in seconds
                - max_retries: Maximum retry attempts

        Example:
            >>> result = config.get_client_config()
            >>> if result.is_success:
            ...     client_config = result.unwrap()
            ...     print(f"Client base URL: {client_config['base_url']}")

        """
        return FlextResult[dict[str, str | float | int]].ok(
            {
                "base_url": self.api_base_url,
                "timeout": self.api_timeout,
                "max_retries": self.max_retries,
            },
        )

    def get_cors_config(self) -> FlextResult[dict[str, list[str] | bool]]:
        """Get CORS configuration dictionary.

        Returns a dictionary containing all CORS-related configuration
        values for web integration.

        Returns:
            FlextResult containing CORS configuration dictionary:
                - allow_origins: List of allowed origins
                - allow_methods: List of allowed HTTP methods
                - allow_headers: List of allowed headers
                - allow_credentials: Whether to allow credentials

        Example:
            >>> result = config.get_cors_config()
            >>> if result.is_success:
            ...     cors_config = result.unwrap()
            ...     print(f"Allowed origins: {cors_config['allow_origins']}")

        """
        return FlextResult[dict[str, list[str] | bool]].ok(
            {
                "allow_origins": self.cors_origins,
                "allow_methods": self.cors_methods,
                "allow_headers": self.cors_headers,
                "allow_credentials": self.cors_allow_credentials,
            },
        )

    # Removed unnecessary getter methods - direct attribute access preferred

    def get_default_headers(self) -> dict[str, str]:
        """Get default HTTP headers.

        Returns a dictionary containing default HTTP headers that should
        be included with all API requests.

        Returns:
            Dictionary containing default headers:
                - User-Agent: API client identification
                - Accept: Content type acceptance
                - Content-Type: Request content type

        Example:
            >>> headers = config.get_default_headers()
            >>> print(f"User-Agent: {headers['User-Agent']}")

        """
        return {
            "User-Agent": f"FlextAPI/{self.api_version}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    @classmethod
    def create_with_overrides(cls, **overrides: object) -> FlextResult[FlextApiConfig]:
        """Create configuration with parameter overrides.

        Creates a new FlextApiConfig instance with default values and
        applies the provided overrides.

        Args:
            **overrides: Configuration parameter overrides to apply.

        Returns:
            FlextResult containing configured FlextApiConfig instance or error details.

        Example:
            >>> result = FlextApiConfig.create_with_overrides(
            ...     api_port=9000, api_debug=True, api_title="My Custom API"
            ... )
            >>> if result.is_success:
            ...     config = result.unwrap()
            ...     print(f"Created config: {config.api_title}")

        """
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
                f"Configuration creation failed: {e}",
            )

    class _BackwardCompatibility:
        """Nested backward compatibility class for FLEXT compliance.

        Provides backward compatibility methods and utilities for
        maintaining API compatibility across versions.
        """

        @staticmethod
        def get_client_config() -> type:
            """Get client config class.

            Returns the FlextApiModels.ClientConfig class for
            backward compatibility.

            Returns:
                FlextApiModels.ClientConfig class.

            """
            return FlextApiModels.ClientConfig

    # Backward compatibility alias - add after class definition


# Backward compatibility exports - FLEXT unified class pattern
# Simple alias following venv_consistency.py pattern
setattr(FlextApiConfig, "ClientConfig", FlextApiModels.ClientConfig)

__all__ = [
    "FlextApiConfig",
]
