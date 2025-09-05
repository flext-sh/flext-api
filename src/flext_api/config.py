"""FLEXT API Config - Configuration management implementation.

Real configuration handling with FlextResult patterns.
Environment-based configuration with validation.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextResult, flext_logger
from pydantic import BaseModel, Field

logger = flext_logger(__name__)


class FlextApiConfig(BaseModel):
    """Main configuration class for FLEXT API."""

    # Server configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    debug: bool = Field(default=False, description="Debug mode")

    # API configuration
    api_title: str = Field(default="FLEXT API", description="API title")
    api_version: str = Field(default="0.9.0", description="API version")
    api_host: str = Field(default="localhost", description="API hostname")

    # Client configuration defaults
    default_timeout: float = Field(default=30.0, description="Default request timeout")
    default_max_retries: int = Field(default=3, description="Default max retries")

    # Storage configuration
    default_backend: str = Field(
        default="memory", description="Default storage backend"
    )

    @classmethod
    def from_env(cls) -> FlextResult[FlextApiConfig]:
        """Create configuration from environment variables."""
        try:
            import os

            config = cls(
                host=os.getenv("FLEXT_API_HOST", "0.0.0.0"),
                port=int(os.getenv("FLEXT_API_PORT", "8000")),
                debug=os.getenv("FLEXT_API_DEBUG", "false").lower() == "true",
                api_title=os.getenv("FLEXT_API_TITLE", "FLEXT API"),
                api_version=os.getenv("FLEXT_API_VERSION", "0.9.0"),
                default_timeout=float(os.getenv("FLEXT_API_TIMEOUT", "30.0")),
                default_max_retries=int(os.getenv("FLEXT_API_MAX_RETRIES", "3")),
                default_backend=os.getenv("FLEXT_API_BACKEND", "memory"),
            )
            return FlextResult.ok(config)
        except Exception as e:
            logger.exception(
                "Failed to load configuration from environment", error=str(e)
            )
            return FlextResult.fail(f"Failed to load configuration: {e}")

    @classmethod
    def default(cls) -> FlextApiConfig:
        """Create default configuration."""
        return cls()


__all__ = ["FlextApiConfig"]
