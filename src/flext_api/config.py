"""FLEXT API Configuration - Settings using flext-core patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pydantic import Field, computed_field
from pydantic_settings import SettingsConfigDict

from flext_core import FlextConfig


class FlextApiConfig(FlextConfig):
    """API Configuration using flext-core FlextConfig."""

    model_config = SettingsConfigDict(
        env_prefix="FLEXT_API_",
        case_sensitive=False,
        extra="allow",
    )

    base_url: str = Field(
        default="http://localhost:8000",
        description="Base URL for API requests",
    )
    timeout: int = Field(
        default=30,
        description="Request timeout in seconds",
    )
    max_retries: int = Field(
        default=3,
        description="Maximum number of retries for failed requests",
    )

    @computed_field  # type: ignore[misc]
    @property
    def api_url(self) -> str:
        """Get complete API URL."""
        return f"{self.base_url}/api"


__all__ = [
    "FlextApiConfig",
]
