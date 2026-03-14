"""Generic HTTP Config Manager - Domain-agnostic configuration management.

This module provides FlextApiSettingsManager, a generic class for managing
HTTP client configuration with flext-core patterns and type safety.
Completely domain-agnostic and reusable across any HTTP client.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping
from typing import TypeGuard

from flext_core import r, u
from pydantic import TypeAdapter, ValidationError

from flext_api import m, t

_JSON_OBJECT_ADAPTER: TypeAdapter = TypeAdapter(object)


def _is_object_mapping(
    value: t.ContainerValue,
) -> TypeGuard[Mapping[str, t.ContainerValue]]:
    return isinstance(value, Mapping)


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
        self, config: Mapping[str, str | float | bool] | None = None
    ) -> r[bool]:
        """Configure the HTTP client with type safety and validation - no fallbacks."""
        try:
            if config is None:
                self._config = {}
            else:
                process_result = self._process_config(config)
                if process_result.is_failure:
                    return r[bool].fail(
                        process_result.error or "Configuration processing failed"
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
                headers_result.error or "Headers extraction failed"
            )
        base_url_result = self._extract_base_url()
        if base_url_result.is_failure:
            return r[m.ClientConfig].fail(
                base_url_result.error or "Base URL extraction failed"
            )
        timeout_result = self._extract_timeout_for_config()
        return timeout_result.fold(
            on_failure=lambda e: r[m.ClientConfig].fail(
                e or "Timeout extraction failed"
            ),
            on_success=lambda timeout: r[m.ClientConfig].ok(
                m.create_config(
                    base_url=base_url_result.value,
                    timeout=timeout,
                    headers=headers_result.value,
                )
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
            config_headers_dict: dict[str, str] = {
                str(k): str(v) for k, v in headers_value.items()
            }
            return r[Mapping[str, str]].ok(config_headers_dict)
        if isinstance(headers_value, str):
            try:
                parsed_headers: t.ContainerValue = _JSON_OBJECT_ADAPTER.validate_json(
                    headers_value
                )
                if _is_object_mapping(parsed_headers):
                    parsed_headers_dict: dict[str, str] = {}
                    for key_obj, value_obj in parsed_headers.items():
                        parsed_headers_dict[str(key_obj)] = str(value_obj)
                    return r[Mapping[str, str]].ok(parsed_headers_dict)
                return r[Mapping[str, str]].fail(
                    f"Parsed headers must be dict, got: {type(parsed_headers)}"
                )
            except (ValidationError, TypeError) as e:
                return r[Mapping[str, str]].fail(f"Failed to parse headers JSON: {e}")
        else:
            return r[Mapping[str, str]].fail(
                f"Invalid headers type: {type(headers_value)}"
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
                lambda _e: f"Max retries must be a valid integer: {max_retries_raw}"
            )
            if retries_result.is_failure:
                return retries_result
            max_retries_value = retries_result.value
        else:
            return r[int].fail(f"Invalid max_retries type: {type(max_retries_raw)}")
        if max_retries_value < 0:
            return r[int].fail(
                f"Max retries cannot be negative, got: {max_retries_value}"
            )
        return r[int].ok(max_retries_value)

    def _extract_timeout(self) -> r[float]:
        """Extract and validate timeout from config - no fallbacks."""
        if self._config is None:
            return r[float].fail("No configuration set")
        if "timeout" not in self._config:
            return r[float].fail("Timeout not specified in configuration")
        timeout_value_raw = self._config["timeout"]
        if isinstance(timeout_value_raw, int | float):
            timeout_value = float(timeout_value_raw)
        elif isinstance(timeout_value_raw, str):
            timeout_result = u.try_(
                lambda: float(timeout_value_raw),
                catch=ValueError,
            ).map_error(
                lambda _e: f"Timeout must be a valid number: {timeout_value_raw}"
            )
            if timeout_result.is_failure:
                return timeout_result
            timeout_value = timeout_result.value
        else:
            return r[float].fail(f"Invalid timeout type: {type(timeout_value_raw)}")
        if timeout_value <= 0:
            return r[float].fail(f"Timeout must be positive, got: {timeout_value}")
        return r[float].ok(timeout_value)

    def _extract_timeout_for_config(self) -> r[float]:
        """Extract timeout for config creation - no fallbacks."""
        if self._config is None:
            return r[float].fail("No configuration set")
        if "timeout" not in self._config:
            return r[float].fail("Timeout not specified in configuration")
        timeout_raw = self._config["timeout"]
        if isinstance(timeout_raw, int | float):
            timeout_value = float(timeout_raw)
        elif isinstance(timeout_raw, str):
            timeout_result = u.try_(
                lambda: float(timeout_raw),
                catch=ValueError,
            ).map_error(lambda _e: f"Timeout must be a valid number: {timeout_raw}")
            if timeout_result.is_failure:
                return timeout_result
            timeout_value = timeout_result.value
        else:
            return r[float].fail(f"Invalid timeout type: {type(timeout_raw)}")
        if timeout_value <= 0:
            return r[float].fail(f"Timeout must be positive, got: {timeout_value}")
        return r[float].ok(timeout_value)

    def _normalize_value(self, key: str, *, value: str | float | bool) -> r:
        """Normalize configuration value based on key type - no fallbacks."""
        if key == "timeout" and isinstance(value, str):
            timeout_result = u.try_(
                lambda: float(value),
                catch=ValueError,
            ).map_error(lambda _e: f"Invalid timeout value: {value}")
            return timeout_result.fold(
                on_failure=lambda e: r.fail(
                    e or f"Invalid timeout value: {value}"
                ),
                on_success=lambda v: r.ok(v),
            )
        if key == "max_retries" and isinstance(value, str):
            retries_result = u.try_(
                lambda: int(value),
                catch=ValueError,
            ).map_error(lambda _e: f"Invalid max_retries value: {value}")
            return retries_result.fold(
                on_failure=lambda e: r.fail(
                    e or f"Invalid max_retries value: {value}"
                ),
                on_success=lambda v: r.ok(v),
            )
        if key in {"log_requests", "log_responses"}:
            return r.ok(bool(value))
        return r.ok(value)

    def _process_config(
        self, config: Mapping[str, str | float | bool]
    ) -> r[t.JsonObject]:
        """Process and normalize configuration values - no fallbacks."""
        processed: t.JsonObject = {}
        for key, value in config.items():
            normalize_result = self._normalize_value(key, value=value)
            if normalize_result.is_failure:
                return r[t.JsonObject].fail(
                    normalize_result.error or "Value normalization failed"
                )
            processed[key] = normalize_result.value
        return r[t.JsonObject].ok(processed)

    def _validate_configuration(self) -> r[bool]:
        """Validate current configuration with complete checks."""
        if self._config is None:
            return r[bool].fail("No configuration set")
        timeout_result = self._extract_timeout()
        if timeout_result.is_failure:
            return r[bool].fail(timeout_result.error or "Timeout extraction failed")
        max_retries_result = self._extract_max_retries()
        return max_retries_result.fold(
            on_failure=lambda e: r[bool].fail(e or "Max retries extraction failed"),
            on_success=lambda _: r[bool].ok(value=True),
        )
