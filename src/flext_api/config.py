"""Compatibility config module mapping to api_config.

Provides FlextApiSettings and create_api_settings for backward-compatibility
with older tests that import flext_api.config.
"""

from __future__ import annotations

from flext_api.api_config import FlextApiSettings, create_api_settings

__all__ = [
    "FlextApiSettings",
    "create_api_settings",
]
