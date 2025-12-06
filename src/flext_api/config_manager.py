"""Generic HTTP Config Manager - Domain-agnostic configuration management.

This module provides FlextApiConfigManager, a generic class for managing
HTTP client configuration with flext-core patterns and type safety.
Completely domain-agnostic and reusable across any HTTP client.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json
from collections.abc import Mapping

from flext_core import r

from flext_api.models import FlextApiModels
from flext_api.typings import FlextApiTypes


class FlextApiConfigManager:
    """Generic configuration management for HTTP clients with flext-core patterns.

    Provides type-safe configuration handling with validation and defaults,
    following railway-oriented error handling throughout. Domain-agnostic.
    """

    def __init__(self) -> None:
        """Initialize configuration manager."""
        self._config: FlextApiTypes.JsonObject | None = None

    def configure(
        self,
        config: Mapping[str, str | float | bool] | None = None,
    ) -> r[bool]:
        """Configure the HTTP client with type safety and validation - no fallbacks."""
        try:
            if config is None:
                self._config = {}
            else:
                process_result = self._process_config(config)
                if process_result.is_failure:
                    return r[bool].fail(
                        process_result.error or "Configuration processing failed",
                    )
                self._config = process_result.unwrap()

            return self._validate_configuration()
        except Exception as e:
            error_msg = f"Configuration failed: {e}"
            return r[bool].fail(error_msg)

    def _process_config(
        self,
        config: Mapping[str, str | float | bool],
    ) -> r[FlextApiTypes.JsonObject]:
        """Process and normalize configuration values - no fallbacks."""
        processed: FlextApiTypes.JsonObject = {}

        for key, value in config.items():
            if value is not None:
                normalize_result = self._normalize_value(key, value=value)
                if normalize_result.is_failure:
                    return r[FlextApiTypes.JsonObject].fail(
                        normalize_result.error or "Value normalization failed",
                    )
                processed[key] = normalize_result.unwrap()

        return r[FlextApiTypes.JsonObject].ok(processed)

    def _normalize_value(
        self,
        key: str,
        *,
        value: str | float | bool,
    ) -> r[str | float | bool]:
        """Normalize configuration value based on key type - no fallbacks."""
        if key == "timeout" and isinstance(value, str):
            try:
                return r[str | float].ok(float(value))
            except ValueError:
                return r[str | float].fail(f"Invalid timeout value: {value}")
        elif key == "max_retries" and isinstance(value, str):
            try:
                return r[str | float].ok(int(value))
            except ValueError:
                return r[str | float].fail(f"Invalid max_retries value: {value}")
        elif key in {"log_requests", "log_responses"}:
            if isinstance(value, (str, int, float)):
                return r[str | float].ok(bool(value))
            return r[str | float].ok(value)
        else:
            return r[str | float].ok(value)

    def _extract_timeout(self) -> r[float]:
        """Extract and validate timeout from config - no fallbacks."""
        if self._config is None:
            return r[float].fail("No configuration set")
        if "timeout" not in self._config:
            return r[float].fail("Timeout not specified in configuration")

        timeout_value_raw = self._config["timeout"]
        if isinstance(timeout_value_raw, (int, float)):
            timeout_value = float(timeout_value_raw)
        elif isinstance(timeout_value_raw, str):
            try:
                timeout_value = float(timeout_value_raw)
            except ValueError:
                return r[float].fail(
                    f"Timeout must be a valid number: {timeout_value_raw}",
                )
        else:
            return r[float].fail(f"Invalid timeout type: {type(timeout_value_raw)}")

        if timeout_value <= 0:
            return r[float].fail(f"Timeout must be positive, got: {timeout_value}")

        return r[float].ok(timeout_value)

    def _extract_max_retries(self) -> r[int]:
        """Extract and validate max_retries from config - no fallbacks."""
        if self._config is None:
            return r[int].fail("No configuration set")
        if "max_retries" not in self._config:
            return r[int].fail("Max retries not specified in configuration")

        max_retries_raw = self._config["max_retries"]
        if isinstance(max_retries_raw, int):
            max_retries_value = max_retries_raw
        elif isinstance(max_retries_raw, (float, str)):
            try:
                max_retries_value = int(max_retries_raw)
            except (ValueError, TypeError):
                return r[int].fail(
                    f"Max retries must be a valid integer: {max_retries_raw}",
                )
        else:
            return r[int].fail(f"Invalid max_retries type: {type(max_retries_raw)}")

        if max_retries_value < 0:
            return r[int].fail(
                f"Max retries cannot be negative, got: {max_retries_value}",
            )

        return r[int].ok(max_retries_value)

    def _validate_configuration(self) -> r[bool]:
        """Validate current configuration with complete checks."""
        if self._config is None:
            return r[bool].fail("No configuration set")

        timeout_result = self._extract_timeout()
        if timeout_result.is_failure:
            return r[bool].fail(timeout_result.error or "Timeout extraction failed")

        max_retries_result = self._extract_max_retries()
        if max_retries_result.is_failure:
            return r[bool].fail(
                max_retries_result.error or "Max retries extraction failed",
            )

        return r[bool].ok(True)

    def _extract_headers(self) -> r[dict[str, str]]:
        """Extract headers from config - no fallbacks."""
        if self._config is None:
            return r[dict[str, str]].fail("No configuration set")
        if "headers" not in self._config:
            return r[dict[str, str]].ok({})

        headers_value = self._config["headers"]
        if isinstance(headers_value, dict):
            return r[dict[str, str]].ok(headers_value)
        if isinstance(headers_value, str):
            try:
                parsed_headers = json.loads(headers_value)
                if isinstance(parsed_headers, dict):
                    return r[dict[str, str]].ok(parsed_headers)
                return r[dict[str, str]].fail(
                    f"Parsed headers must be dict, got: {type(parsed_headers)}",
                )
            except (json.JSONDecodeError, TypeError) as e:
                return r[dict[str, str]].fail(f"Failed to parse headers JSON: {e}")
        else:
            return r[dict[str, str]].fail(
                f"Invalid headers type: {type(headers_value)}",
            )

    def _extract_base_url(self) -> r[str]:
        """Extract base_url from config - no fallbacks."""
        if self._config is None:
            return r[str].fail("No configuration set")
        if "base_url" not in self._config:
            return r[str].ok("")

        base_url_value = self._config["base_url"]
        if isinstance(base_url_value, str):
            return r[str].ok(base_url_value)
        return r[str].fail(f"Invalid base_url type: {type(base_url_value)}")

    def _extract_timeout_for_config(self) -> r[float]:
        """Extract timeout for config creation - no fallbacks."""
        if self._config is None:
            return r[float].fail("No configuration set")
        if "timeout" not in self._config:
            return r[float].fail("Timeout not specified in configuration")

        timeout_raw = self._config["timeout"]
        if isinstance(timeout_raw, (int, float)):
            timeout_value = float(timeout_raw)
        elif isinstance(timeout_raw, str):
            try:
                timeout_value = float(timeout_raw)
            except ValueError:
                return r[float].fail(f"Timeout must be a valid number: {timeout_raw}")
        else:
            return r[float].fail(f"Invalid timeout type: {type(timeout_raw)}")

        if timeout_value <= 0:
            return r[float].fail(f"Timeout must be positive, got: {timeout_value}")

        return r[float].ok(timeout_value)

    def get_client_config(self) -> r[FlextApiModels.ClientConfig]:
        """Get validated client configuration - no fallbacks."""
        if self._config is None:
            return r[FlextApiModels.ClientConfig].fail("No configuration set")

        headers_result = self._extract_headers()
        if headers_result.is_failure:
            return r[FlextApiModels.ClientConfig].fail(
                headers_result.error or "Headers extraction failed",
            )

        base_url_result = self._extract_base_url()
        if base_url_result.is_failure:
            return r[FlextApiModels.ClientConfig].fail(
                base_url_result.error or "Base URL extraction failed",
            )

        timeout_result = self._extract_timeout_for_config()
        if timeout_result.is_failure:
            return r[FlextApiModels.ClientConfig].fail(
                timeout_result.error or "Timeout extraction failed",
            )

        return r[FlextApiModels.ClientConfig].ok(
            FlextApiModels.create_config(
                base_url=base_url_result.unwrap(),
                timeout=timeout_result.unwrap(),
                headers=headers_result.unwrap(),
            ),
        )

    @property
    def config(self) -> FlextApiTypes.JsonObject | None:
        """Get current configuration."""
        return self._config
