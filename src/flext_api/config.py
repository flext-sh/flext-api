"""FLEXT API Config - Configuration management implementation.

Real configuration handling with FlextResult patterns.
Environment-based configuration with validation.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os

from flext_core import FlextLogger, FlextResult
from pydantic import BaseModel, Field, field_validator, model_validator

from flext_api.typings import FlextApiTypes

logger = FlextLogger(__name__)


class FlextApiConfig(BaseModel):
    """Main configuration class for FLEXT API."""

    # Server configuration
    host: str = Field(
        default="127.0.0.1",
        description="Server host address",
    )
    port: int = Field(
        default=8000,
        ge=1,
        le=65535,
        description="Server port",
    )
    # API port (may mirror 'port' when not explicitly provided)
    api_port: int | None = Field(
        default=None,
        ge=1,
        le=65535,
        description="Public API port (defaults to 'port' if unset)",
    )
    workers: int = Field(
        default=1,
        ge=1,
        description="Number of worker processes",
    )
    debug: bool = Field(default=False, description="Debug mode")

    # API configuration
    api_title: str = Field(default="FLEXT API", description="API title")
    api_version: str = Field(default="0.9.0", description="API version")
    api_host: str = Field(default="localhost", description="API hostname")

    # Client configuration defaults
    default_timeout: float = Field(
        default=30.0,
        gt=0,
        description="Default request timeout (seconds)",
    )
    # Aligned with tests: expose 'max_retries' (>= 0)
    max_retries: int = Field(
        default=3,
        ge=0,
        description="Maximum retry attempts for client requests",
    )
    base_url: str = Field(
        default="http://localhost:8000",
        description="Base URL for client requests (http/https)",
    )

    # CORS configuration
    cors_origins: FlextApiTypes.Core.StringList = Field(
        default_factory=lambda: ["*"], description="Allowed CORS origins"
    )
    cors_methods: FlextApiTypes.Core.StringList = Field(
        default_factory=lambda: ["*"], description="Allowed CORS methods"
    )
    cors_headers: FlextApiTypes.Core.StringList = Field(
        default_factory=lambda: ["*"], description="Allowed CORS headers"
    )

    # Storage configuration
    default_backend: str = Field(
        default="memory", description="Default storage backend"
    )

    @classmethod
    def from_env(cls) -> FlextResult[FlextApiConfig]:
        """Create configuration from environment variables."""
        try:
            config = cls(
                host=os.getenv("FLEXT_API_HOST", "127.0.0.1"),
                port=int(os.getenv("FLEXT_API_PORT", "8000")),
                debug=os.getenv("FLEXT_API_DEBUG", "false").lower() == "true",
                api_title=os.getenv("FLEXT_API_TITLE", "FLEXT API"),
                api_version=os.getenv("FLEXT_API_VERSION", "0.9.0"),
                default_timeout=float(os.getenv("FLEXT_API_TIMEOUT", "30.0")),
                max_retries=int(os.getenv("FLEXT_API_MAX_RETRIES", "3")),
                default_backend=os.getenv("FLEXT_API_BACKEND", "memory"),
                base_url=os.getenv("FLEXT_API_BASE_URL", "http://localhost:8000"),
            )
            return FlextResult.ok(config)
        except Exception as e:
            logger.exception(
                "Failed to load configuration from environment", error=str(e)
            )
            return FlextResult.fail(f"Failed to load configuration: {e}")

    @classmethod
    def default(cls) -> FlextApiConfig:
        """Create default configuration.

        Returns:
            FlextResult[FlextApiConfig]:: Description of return value.

        """
        return cls()

    # ---------------------------
    # Validation and normalization
    # ---------------------------

    @field_validator("host")
    @classmethod
    def _validate_host(cls, v: str) -> str:
        if not v or not v.strip():
            msg = "Host cannot be empty"
            raise ValueError(msg)
        return v

    @field_validator("base_url")
    @classmethod
    def _validate_base_url(cls, v: str) -> str:
        if not v or not v.strip():
            msg = "Base cannot be empty"
            raise ValueError(msg)
        if not v.startswith(("http://", "https://")):
            msg = "Base must start with http:// or https://"
            raise ValueError(msg)
        return v

    @model_validator(mode="after")
    def _finalize(self) -> FlextApiConfig:
        # If api_port is not provided, mirror primary 'port'
        if self.api_port is None:
            object.__setattr__(self, "api_port", self.port)
        return self

    # ---------------------------
    # Accessors that return FlextResult with dict payloads
    # ---------------------------

    def get_server_config(self) -> FlextResult[FlextApiTypes.Core.Dict]:
        data: FlextApiTypes.Core.Dict = {
            "host": self.host,
            "port": self.port,
            "workers": self.workers,
            "debug": self.debug,
        }
        return FlextResult[FlextApiTypes.Core.Dict].ok(data)

    def get_client_config(self) -> FlextResult[FlextApiTypes.Core.Dict]:
        data: FlextApiTypes.Core.Dict = {
            "base_url": self.base_url,
            "timeout": self.default_timeout,
            "max_retries": self.max_retries,
        }
        return FlextResult[FlextApiTypes.Core.Dict].ok(data)

    def get_cors_config(self) -> FlextResult[FlextApiTypes.Core.Dict]:
        data: FlextApiTypes.Core.Dict = {
            "allow_origins": list(self.cors_origins),
            "allow_methods": list(self.cors_methods),
            "allow_headers": list(self.cors_headers),
            "allow_credentials": True,
        }
        return FlextResult[FlextApiTypes.Core.Dict].ok(data)


__all__ = ["FlextApiConfig"]
