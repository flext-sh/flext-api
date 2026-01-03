"""Generic HTTP Configuration - Pure Pydantic v2.

Minimal HTTP configuration using Pydantic v2 with flext-core constants.
100% GENERIC - no domain coupling. Single responsibility.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json

from flext_core import FlextSettings
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from flext_api.constants import c


@FlextSettings.auto_register("api")
class FlextApiSettings(BaseSettings):
    """HTTP configuration using Pydantic v2.

    Pure configuration model with validation using c.
    Config has priority over Constants, but uses Constants as defaults.
    No wrappers - use Pydantic directly.
    """

    model_config = SettingsConfigDict(
        env_prefix="FLEXT_API_",
        env_file=FlextSettings.resolve_env_file(),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    base_url: str = Field(
        default=c.Api.DEFAULT_BASE_URL,
        max_length=c.Api.MAX_URL_LENGTH,
        description="Base URL for HTTP requests",
    )

    timeout: float = Field(
        default=float(c.Api.DEFAULT_TIMEOUT),
        ge=float(c.Api.VALIDATION_LIMITS["MIN_TIMEOUT"]),
        le=float(c.Api.VALIDATION_LIMITS["MAX_TIMEOUT"]),
        description="HTTP request timeout (seconds)",
    )

    max_retries: int = Field(
        default=c.Api.DEFAULT_MAX_RETRIES,
        ge=int(c.Api.VALIDATION_LIMITS["MIN_RETRIES"]),
        le=int(c.Api.VALIDATION_LIMITS["MAX_RETRIES"]),
        description="Maximum retry attempts",
    )

    headers: dict[str, str] = Field(
        default_factory=dict,
        description="Default HTTP headers",
    )

    @field_validator("headers", mode="before")
    @classmethod
    def validate_headers(cls, v: dict[str, str]) -> dict[str, str]:
        """Validate headers."""
        for key, value in v.items():
            key_stripped = key.strip()
            if not key_stripped:
                msg = f"Invalid header key: '{key}'"
                raise ValueError(msg)
            if not value:
                msg = f"Invalid header value for '{key}': '{value}'"
                raise ValueError(msg)
        return v

    @property
    def default_headers(self) -> dict[str, str]:
        """Default headers with MIME type from Constants."""
        return {
            c.Api.HEADER_ACCEPT: c.Api.ContentType.JSON,
            c.Api.HEADER_CONTENT_TYPE: c.Api.ContentType.JSON,
            **self.headers,
        }

    def to_json(self) -> str:
        """Convert to JSON."""
        return json.dumps(self.model_dump(), indent=2)

    @classmethod
    def from_json(cls, data: str) -> FlextApiSettings:
        """Create from JSON."""
        return cls.model_validate(json.loads(data))


__all__ = ["FlextApiSettings"]
