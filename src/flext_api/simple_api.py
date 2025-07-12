"""Simple API for FLEXT API setup and configuration.

Provides a simple interface for setting up the FLEXT API application.
"""

from __future__ import annotations

from typing import Any

from flext_api.config import APISettings
from flext_core.config import get_container
from flext_core.domain.result import ServiceResult


def setup_api(settings: APISettings | None = None) -> ServiceResult[bool]:
    """Setup the FLEXT API.

    Args:
        settings: The settings for the API.

    Returns:
        The result of the setup.

    """
    try:
        from flext_observability.logging import (  # TODO: Mov  e import to module level
            setup_logging,
        )

        if settings is None:
            from flext_api.main import get_api_settings

            settings = get_api_settings()

        # Setup logging using flext-observability
        setup_logging(
            level=settings.log_level,
            format=settings.log_format,
            output_file=None,
        )

        # Configure DI container
        container = get_container()
        settings.configure_dependencies(container)

        return ServiceResult.ok(True)

    except Exception as e:
        return ServiceResult.fail(f"Failed to setup API: {e}")


def create_development_api_config(**overrides: Any) -> APISettings:
    # Development defaults
    defaults = {
        "host": "127.0.0.1",
        "port": 8000,
        "workers": 1,
        "reload": True,
        "log_level": "DEBUG",
        "log_format": "colored",
        "secret_key": "development-secret-key-change-in-production-minimum-50-chars",
        "cors_origins": ["*"],
        "cors_allow_credentials": True,
        "rate_limit_per_minute": 1000,
        "rate_limit_burst": 100,
        "grpc_host": "localhost",
        "grpc_port": 50051,
        "grpc_timeout": 30,
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "openapi_url": "/openapi.json",
        "health_check_enabled": True,
        "readiness_check_enabled": True,
        "metrics_enabled": True,
        "metrics_port": 9090,
        "websocket_enabled": True,
        "websocket_heartbeat_interval": 30,
    }

    # Override with provided values
    defaults.update(overrides)

    return APISettings(**defaults)


def create_production_api_config(**overrides: Any) -> APISettings:
    # Production defaults
    defaults = {
        "host": "0.0.0.0",
        "port": 8000,
        "workers": 4,
        "reload": False,
        "log_level": "INFO",
        "log_format": "json",
        "secret_key": "CHANGE-ME-IN-PRODUCTION-MINIMUM-50-CHARACTERS-LONG",
        "cors_origins": [],
        "cors_allow_credentials": True,
        "allowed_hosts": ["localhost"],
        "trusted_proxies": ["127.0.0.1"],
        "rate_limit_per_minute": 100,
        "rate_limit_burst": 10,
        "grpc_host": "localhost",
        "grpc_port": 50051,
        "grpc_timeout": 30,
        "docs_url": None,  # Disable in production
        "redoc_url": None,  # Disable in production
        "openapi_url": None,  # Disable in production
        "health_check_enabled": True,
        "readiness_check_enabled": True,
        "metrics_enabled": True,
        "metrics_port": 9090,
        "websocket_enabled": True,
        "websocket_heartbeat_interval": 30,
    }

    # Override with provided values
    defaults.update(overrides)

    return APISettings(**defaults)


# Export convenience functions
__all__ = [
    "create_development_api_config",
    "create_production_api_config",
    "setup_api",
]
