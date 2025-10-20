"""Generic HTTP Config Manager - Domain-agnostic configuration management.

This module provides FlextApiConfigManager, a generic class for managing
HTTP client configuration with flext-core patterns and type safety.
Completely domain-agnostic and reusable across any HTTP client.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json
from typing import Any

from flext_core import FlextResult

from flext_api.models import FlextApiModels


class FlextApiConfigManager:
    """Generic configuration management for HTTP clients with flext-core patterns.

    Provides type-safe configuration handling with validation and defaults,
    following railway-oriented error handling throughout. Domain-agnostic.
    """

    def __init__(self) -> None:
        """Initialize configuration manager."""
        self._config: dict[str, Any] | None = None

    def configure(
        self, config: dict[str, str | float | bool] | None = None
    ) -> FlextResult[None]:
        """Configure the HTTP client with type safety and validation."""
        try:
            if config is None:
                self._config = {}
            else:
                self._config = self._process_config(config)

            return self._validate_configuration()
        except Exception as e:
            return FlextResult[None].fail(f"Configuration failed: {e}")

    def _process_config(self, config: dict[str, Any]) -> dict[str, Any]:
        """Process and normalize configuration values."""
        processed = {}

        for key, value in config.items():
            if value is not None:
                processed[key] = self._normalize_value(key, value)

        return processed

    def _normalize_value(self, key: str, value: str | float) -> str | float:
        """Normalize configuration value based on key type."""
        if key == "timeout" and isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                return 30.0
        elif key == "max_retries" and isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                return 3
        elif key in {"log_requests", "log_responses"}:
            return bool(value) if isinstance(value, (str, int, float)) else value
        else:
            return value

    def _validate_configuration(self) -> FlextResult[None]:
        """Validate current configuration with comprehensive checks."""
        if self._config is None:
            return FlextResult[None].fail("No configuration set")

        timeout = self._config.get("timeout", 30.0)
        if timeout <= 0:
            return FlextResult[None].fail("Timeout must be positive")

        max_retries = self._config.get("max_retries", 3)
        if max_retries < 0:
            return FlextResult[None].fail("Max retries cannot be negative")

        return FlextResult[None].ok(None)

    def get_client_config(self) -> FlextResult[FlextApiModels]:
        """Get validated client configuration."""
        if self._config is None:
            return FlextResult[FlextApiModels.ClientConfig].fail("No configuration set")

        # Convert string headers back to dict if needed
        headers = self._config.get("headers", {})
        if isinstance(headers, str):
            try:
                headers = json.loads(headers)
            except Exception:
                headers = {}

        return FlextResult[FlextApiModels].ok(
            FlextApiModels.create_config(
                base_url=self._config.get("base_url", ""),
                timeout=self._config.get("timeout", 30.0),
                headers=headers,
            )
        )

    @property
    def config(self) -> dict[str, Any] | None:
        """Get current configuration."""
        return self._config
