"""FLEXT API Configuration - Consolidated using flext-core patterns.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

This module provides API configuration using consolidated flext-core patterns.
"""

from __future__ import annotations

# Note: Using string values instead of enums until flext-core enums are available
from flext_api.infrastructure.config import APIConfig

# All code should use APIConfig directly
# Alias for backward compatibility
APISettings = APIConfig

# Global settings instance
_settings: APIConfig | None = None


def get_api_settings() -> APIConfig:
    """Get API configuration settings.

    Returns:
        APIConfig: Consolidated API configuration using flext-core patterns.,

    """
    global _settings
    if _settings is None:
        _settings = APIConfig()
    return _settings


def create_development_api_config() -> APIConfig:
    """Create development API configuration.

    Returns:
        APIConfig: Development configuration.,

    """
    return APIConfig(
        project_name="FLEXT API",
        reload=True,
    )


def create_production_api_config() -> APIConfig:
    """Create production API configuration.

    Returns:
        APIConfig: Production configuration.,

    """
    return APIConfig(
        project_name="FLEXT API",
        reload=False,
    )


__all__ = [
    "APIConfig",
    "create_development_api_config",
    "create_production_api_config",
    "get_api_settings",
]
