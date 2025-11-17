"""Generic HTTP Configuration - Pure Pydantic v2.

Minimal HTTP configuration using Pydantic v2 with flext-core constants.
100% GENERIC - no domain coupling. Single responsibility.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json

from flext_core import FlextConstants
from pydantic import BaseModel, Field, field_validator


class FlextApiConfig(BaseModel):
    """HTTP configuration using Pydantic v2.

    Pure configuration model with validation using flext-core constants.
    No wrappers - use Pydantic directly.
    """

    base_url: str = Field(
        default="",
        max_length=2048,
        description="Base URL for HTTP requests",
    )

    timeout: float = Field(
        default=FlextConstants.Container.TIMEOUT_SECONDS,
        ge=FlextConstants.Container.MIN_TIMEOUT_SECONDS,
        le=FlextConstants.Container.MAX_TIMEOUT_SECONDS,
        description="HTTP request timeout (seconds)",
    )

    max_retries: int = Field(
        default=FlextConstants.Reliability.MAX_RETRY_ATTEMPTS,
        ge=FlextConstants.Cqrs.MIN_RETRIES,
        le=FlextConstants.Cqrs.MAX_RETRIES,
        description="Maximum retry attempts",
    )

    headers: dict[str, str] = Field(
        default_factory=dict,
        description="Default HTTP headers",
    )

    @field_validator("headers")
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
        """Default headers with MIME type."""
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            **self.headers,
        }

    def to_json(self) -> str:
        """Convert to JSON."""
        return json.dumps(self.model_dump(), indent=2)

    @classmethod
    def from_json(cls, data: str) -> FlextApiConfig:
        """Create from JSON."""
        return cls.model_validate(json.loads(data))


__all__ = ["FlextApiConfig"]
