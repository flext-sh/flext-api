"""Generic HTTP Config Manager - Domain-agnostic configuration management.

This module provides FlextApiSettingsManager, a generic class for managing
HTTP client configuration with flext-core patterns and type safety.
Completely domain-agnostic and reusable across any HTTP client.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping

from flext_core import r
from pydantic import TypeAdapter, ValidationError

from flext_api import m, t, u

_JSON_HEADERS_ADAPTER: TypeAdapter[Mapping[str, t.ContainerValue]] = TypeAdapter(
    Mapping[str, t.ContainerValue],
)


class FlextApiSettingsManager:
    """Generic configuration management for HTTP clients with flext-core patterns.

    Provides type-safe configuration handling with validation and defaults,
    following railway-oriented error handling throughout. Domain-agnostic.
    """

    def __init__(self) -> None:
        """Initialize configuration manager."""
        self._config: t.JsonObject | None = None

    @property
    def config(self) -> t.JsonObject | None:
        """Get current configuration."""
        return self._config

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
                self._config = process_result.value
            return self._validate_configuration()
        except (ValueError, TypeError, KeyError, ConnectionError) as e:
            error_msg = f"Configuration failed: {e}"
            return r[bool].fail(error_msg)

    def get_client_config(self) -> r[m.ClientConfig]:
        """Get validated client configuration - no fallbacks."""
        if self._config is None:
            return r[m.ClientConfig].fail("No configuration set")
        headers_result = self._extract_headers()
        if headers_result.is_failure:
            return r[m.ClientConfig].fail(
                headers_result.error or "Headers extraction failed",
            )
        base_url_result = self._extract_base_url()
        if base_url_result.is_failure:
            return r[m.ClientConfig].fail(
                base_url_result.error or "Base URL extraction failed",
            )
        timeout_result = self._extract_positive_float_setting(
            key="timeout",
            label="Timeout",
        )
        return timeout_result.fold(
            on_failure=lambda e: r[m.ClientConfig].fail(
                e or "Timeout extraction failed",
            ),
            on_success=lambda timeout: r[m.ClientConfig].ok(
                m.create_config(
                    base_url=base_url_result.value,
                    timeout=timeout,
                    headers=headers_result.value,
                ),
            ),
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

    def _extract_headers(self) -> r[Mapping[str, str]]:
        """Extract headers from config - no fallbacks."""
        if self._config is None:
            return r[Mapping[str, str]].fail("No configuration set")
        if "headers" not in self._config:
            return r[Mapping[str, str]].ok({})
        headers_value = self._config["headers"]
        if isinstance(headers_value, Mapping):
            config_headers_dict: Mapping[str, str] = {
                str(k): str(v) for k, v in headers_value.items()
            }
            return r[Mapping[str, str]].ok(config_headers_dict)
        if isinstance(headers_value, str):
            try:
                parsed_headers = _JSON_HEADERS_ADAPTER.validate_json(headers_value)
                parsed_headers_dict: Mapping[str, str] = {
                    str(key_obj): str(value_obj)
                    for key_obj, value_obj in parsed_headers.items()
                }
                return r[Mapping[str, str]].ok(parsed_headers_dict)
            except (ValidationError, TypeError) as e:
                return r[Mapping[str, str]].fail(f"Failed to parse headers JSON: {e}")
        else:
            return r[Mapping[str, str]].fail(
                f"Invalid headers type: {type(headers_value)}",
            )

    def _extract_max_retries(self) -> r[int]:
        """Extract and validate max_retries from config - no fallbacks."""
        if self._config is None:
            return r[int].fail("No configuration set")
        if "max_retries" not in self._config:
            return r[int].fail("Max retries not specified in configuration")
        max_retries_raw = self._config["max_retries"]
        if isinstance(max_retries_raw, int):
            max_retries_value = max_retries_raw
        elif isinstance(max_retries_raw, float | str):
            retries_result = u.try_(
                lambda: int(max_retries_raw),
                catch=(ValueError, TypeError),
            ).map_error(
                lambda _e: f"Max retries must be a valid integer: {max_retries_raw}",
            )
            if retries_result.is_failure:
                return retries_result
            max_retries_value = retries_result.value
        else:
            return r[int].fail(f"Invalid max_retries type: {type(max_retries_raw)}")
        if max_retries_value < 0:
            return r[int].fail(
                f"Max retries cannot be negative, got: {max_retries_value}",
            )
        return r[int].ok(max_retries_value)

    def _extract_positive_float_setting(self, *, key: str, label: str) -> r[float]:
        if self._config is None:
            return r[float].fail("No configuration set")
        if key not in self._config:
            return r[float].fail(f"{label} not specified in configuration")
        raw_value = self._config[key]
        if isinstance(raw_value, int | float):
            float_value = float(raw_value)
        elif isinstance(raw_value, str):
            timeout_result = u.try_(
                lambda: float(raw_value),
                catch=ValueError,
            ).map_error(lambda _e: f"{label} must be a valid number: {raw_value}")
            if timeout_result.is_failure:
                return timeout_result
            float_value = timeout_result.value
        else:
            return r[float].fail(f"Invalid {key} type: {type(raw_value)}")
        if float_value <= 0:
            return r[float].fail(f"{label} must be positive, got: {float_value}")
        return r[float].ok(float_value)

    def _normalize_value(self, key: str, *, value: str | float | bool) -> r[t.Scalar]:
        """Normalize configuration value based on key type - no fallbacks."""
        if key == "timeout" and isinstance(value, str):
            timeout_result = u.try_(
                lambda: float(value),
                catch=ValueError,
            ).map_error(lambda _e: f"Invalid timeout value: {value}")
            return timeout_result.fold(
                on_failure=lambda e: r[t.Scalar].fail(
                    e or f"Invalid timeout value: {value}",
                ),
                on_success=lambda v: r[t.Scalar].ok(v),
            )
        if key == "max_retries" and isinstance(value, str):
            retries_result = u.try_(
                lambda: int(value),
                catch=ValueError,
            ).map_error(lambda _e: f"Invalid max_retries value: {value}")
            return retries_result.fold(
                on_failure=lambda e: r[t.Scalar].fail(
                    e or f"Invalid max_retries value: {value}",
                ),
                on_success=lambda v: r[t.Scalar].ok(v),
            )
        if key in {"log_requests", "log_responses"}:
            return r.ok(bool(value))
        return r.ok(value)

    def _process_config(
        self,
        config: Mapping[str, str | float | bool],
    ) -> r[t.JsonObject]:
        """Process and normalize configuration values - no fallbacks."""
        processed: t.JsonObject = {}
        for key, value in config.items():
            normalize_result = self._normalize_value(key, value=value)
            if normalize_result.is_failure:
                return r[t.JsonObject].fail(
                    normalize_result.error or "Value normalization failed",
                )
            processed[key] = normalize_result.value
        return r[t.JsonObject].ok(processed)

    def _validate_configuration(self) -> r[bool]:
        """Validate current configuration with complete checks."""
        if self._config is None:
            return r[bool].fail("No configuration set")
        timeout_result = self._extract_positive_float_setting(
            key="timeout",
            label="Timeout",
        )
        if timeout_result.is_failure:
            return r[bool].fail(timeout_result.error or "Timeout extraction failed")
        max_retries_result = self._extract_max_retries()
        return max_retries_result.fold(
            on_failure=lambda e: r[bool].fail(e or "Max retries extraction failed"),
            on_success=lambda _: r[bool].ok(value=True),
        )
