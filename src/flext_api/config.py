"""FLEXT API Configuration - Settings using flext-core patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextConfig, FlextResult, FlextTypes
from pydantic import Field, computed_field
from pydantic_settings import SettingsConfigDict

from flext_api.constants import FlextApiConstants


class FlextApiConfig(FlextConfig):
    """Single Pydantic Settings class for flext-api extending FlextConfig.

    Uses enhanced FlextConfig features:
    - Protocol inheritance (Infrastructure.Configurable)
    - Computed fields for derived configuration
    - Enhanced validation with field_validator and model_validator
    - Type-safe configuration management
    - Business rule validation
    - Configuration persistence

    All defaults from FlextApiConstants with FlextConfig enhancements.
    """

    model_config = SettingsConfigDict(
        env_prefix="FLEXT_API_",
        case_sensitive=False,
        extra="allow",
        # Enhanced Pydantic 2.11+ features from FlextConfig
        validate_assignment=True,
        str_strip_whitespace=True,
        str_to_lower=False,
        json_schema_extra={
            "title": "FLEXT API Configuration",
            "description": "Enterprise API configuration with FlextConfig protocol support",
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
    cors_origins: FlextTypes.StringList = Field(
        default_factory=lambda: ["*"],
        description="CORS allowed origins",
    )

    cors_methods: FlextTypes.StringList = Field(
        default_factory=lambda: ["GET", "POST", "PUT", "DELETE"],
        description="CORS allowed methods",
    )

    cors_headers: FlextTypes.StringList = Field(
        default_factory=lambda: ["Content-Type", "Authorization"],
        description="CORS allowed headers",
    )

    @computed_field
    @property
    def api_url(self) -> str:
        """Get complete API URL with version."""
        return f"{self.base_url}/api/{self.api_version}"

    @computed_field
    def client_config(self) -> FlextTypes.Dict:
        """Get HTTP client configuration with flext-core integration patterns."""
        return {
            "base_url": self.api_url,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "headers": {
                "User-Agent": f"FlextApi/{self.api_version}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            "transport_config": {
                "connection_pool_size": self.database_pool_size,
                "max_connections": min(self.max_workers, 100),
                "retry_on": [500, 502, 503, 504],
            },
            "performance_config": {
                "enable_metrics": self.enable_metrics,
                "enable_tracing": self.enable_tracing,
                "cache_responses": self.enable_caching,
            },
        }

    @computed_field
    def server_config(self) -> FlextTypes.Dict:
        """Get HTTP server configuration with flext-core integration patterns."""
        return {
            "host": "127.0.0.1",
            "port": 8000,
            "workers": self.max_workers,
            "timeout": self.timeout_seconds,
            "cors": {
                "origins": self.cors_origins,
                "methods": self.cors_methods,
                "headers": self.cors_headers,
                "credentials": True,
            },
            "logging": {
                "request_logging": self.log_requests,
                "response_logging": self.log_responses,
                "structured": self.structured_output,
                "level": self.effective_log_level,
            },
            "security": {
                "enable_auth": True,
                "rate_limiting": self.rate_limit_max_requests > 0,
                "rate_limit_window": self.rate_limit_window_seconds,
            },
        }

    @computed_field
    def middleware_config(self) -> FlextTypes.Dict:
        """Get middleware configuration with flext-core integration patterns."""
        return {
            "cors": {
                "enabled": len(self.cors_origins) > 0,
                "origins": self.cors_origins,
                "methods": self.cors_methods,
                "headers": self.cors_headers,
            },
            "logging": {
                "request_logging": self.log_requests,
                "response_logging": self.log_responses,
                "include_context": self.include_context,
                "include_correlation_id": self.include_correlation_id,
            },
            "security": {
                "rate_limiting": {
                    "enabled": self.rate_limit_max_requests > 0,
                    "max_requests": self.rate_limit_max_requests,
                    "window_seconds": self.rate_limit_window_seconds,
                },
                "authentication": {
                    "enabled": True,
                    "jwt_expiry": self.jwt_expiry_minutes,
                },
            },
            "performance": {
                "caching": {
                    "enabled": self.enable_caching,
                    "ttl": self.cache_ttl,
                },
                "compression": {
                    "enabled": True,
                    "algorithms": ["gzip", "deflate"],
                },
            },
        }

    @computed_field
    def monitoring_config(self) -> FlextTypes.Dict:
        """Get monitoring configuration with flext-core integration patterns."""
        return {
            "metrics": {
                "enabled": self.enable_metrics,
                "endpoint": "/metrics",
                "collection_interval": 60,
            },
            "tracing": {
                "enabled": self.enable_tracing,
                "service_name": f"flext-api-{self.api_version}",
                "sampling_rate": 0.1,
            },
            "health_checks": {
                "enabled": True,
                "endpoint": "/health",
                "checks": ["database", "cache", "external_apis"],
            },
            "logging": {
                "structured": self.structured_output,
                "correlation_id": self.include_correlation_id,
                "performance_tracking": self.track_performance,
            },
        }

    # =========================================================================
    # Infrastructure Protocol Implementations (FlextConfig inheritance)
    # =========================================================================

    def configure(self, config: FlextTypes.Dict) -> FlextResult[None]:
        """Configure API settings with provided configuration.

        Implements Infrastructure.Configurable protocol from FlextConfig.

        Args:
            config: Configuration dictionary to apply

        Returns:
            FlextResult[None]: Success if configuration valid, failure otherwise

        """
        try:
            # Apply API-specific configuration
            for key, value in config.items():
                if hasattr(self, key) and key in {
                    "base_url",
                    "timeout",
                    "max_retries",
                    "api_version",
                    "log_requests",
                    "log_responses",
                    "cors_origins",
                    "cors_methods",
                    "cors_headers",
                }:
                    setattr(self, key, value)

            # Call parent configure for core configuration
            return super().configure(config)
        except Exception as e:
            return FlextResult[None].fail(f"API configuration failed: {e}")

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate API-specific business rules for configuration consistency.

        Extends Infrastructure.ConfigValidator protocol from FlextConfig.

        Returns:
            FlextResult[None]: Success if valid, failure with error details

        """
        # Call parent business rules validation first
        parent_result = super().validate_business_rules()
        if parent_result.is_failure:
            return parent_result

        # API-specific business rules
        if self.is_production():
            # Production API validation - use constants for magic values
            max_prod_timeout = 60  # seconds
            max_prod_retries = 5

            if not self.base_url or not self.base_url.startswith((
                "https://",
                "http://",
            )):
                return FlextResult[None].fail(
                    "Production API requires valid base_url starting with http:// or https://"
                )

            if self.timeout > max_prod_timeout:
                return FlextResult[None].fail(
                    f"Production API timeout too high: {self.timeout}s (max: {max_prod_timeout}s)"
                )

            if self.max_retries > max_prod_retries:
                return FlextResult[None].fail(
                    f"Production API max_retries too high: {self.max_retries} (max: {max_prod_retries})"
                )

        # Development validation - combine nested if statements
        if (
            self.is_development()
            and self.base_url
            and self.base_url.startswith("https://")
            and self.debug
        ):
            # Allow HTTPS in development for testing, but warn via logging
            pass

        return FlextResult[None].ok(None)

    # Factory methods removed - use direct instantiation only
    # ✅ CORRECT: config = FlextApiConfig()
    # ❌ FORBIDDEN: config = FlextApiConfig.get_global_instance()

    # =========================================================================
    # Enhanced flext-core Integration Methods
    # =========================================================================

    # Removed complex factory methods - use direct instantiation
    # ✅ CORRECT: config = FlextApiConfig()

    # Complex validation and demonstration methods removed for simplicity
    # Focus on core configuration functionality only


__all__ = [
    "FlextApiConfig",
]
