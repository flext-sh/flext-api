"""Generic HTTP Configuration - Pure Pydantic settings.

This module provides FlextWebConfig, a generic Pydantic configuration class
for HTTP operations. Completely domain-agnostic and reusable.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class FlextWebConfig(BaseModel):
    """Generic HTTP configuration using pure Pydantic patterns.

    Domain-agnostic configuration for HTTP operations with type safety.
    Uses advanced Pydantic features for validation and defaults.
    """

    # Core HTTP configuration
    base_url: str = Field(default="", description="Base URL for HTTP requests")

    timeout: float = Field(
        default=30.0,
        ge=0.1,
        le=300.0,
        description="HTTP request timeout in seconds",
    )

    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum number of retries for failed requests",
    )

    # Request configuration
    headers: dict[str, Any] = Field(
        default_factory=dict,
        description="Default HTTP headers for requests",
    )

    # Logging configuration
    log_requests: bool = Field(default=True, description="Enable request logging")
    log_responses: bool = Field(default=True, description="Enable response logging")

    # Performance configuration
    track_performance: bool = Field(default=True, description="Enable performance tracking")

    def get_client_config(self) -> dict[str, Any]:
        """Get HTTP client configuration."""
        return {
            "base_url": self.base_url,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "headers": self.headers,
        }

    def get_server_config(self) -> dict[str, Any]:
        """Get HTTP server configuration."""
        return {
            "host": "127.0.0.1",
            "port": 8000,
            "timeout": self.timeout,
            "logging": {
                "request_logging": self.log_requests,
                "response_logging": self.log_responses,
            },
        }

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary for serialization."""
        return self.model_dump()

    def get_default_headers(self) -> dict[str, str]:
        """Get default headers for HTTP requests."""
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            **self.headers,
        }


__all__ = [
    "FlextWebConfig",
]
