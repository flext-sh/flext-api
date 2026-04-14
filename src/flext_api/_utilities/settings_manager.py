"""Generic HTTP Config Manager - Domain-agnostic configuration management.

This module provides FlextApiUtilitiesSettingsManager, a generic class for managing
HTTP client configuration with flext-core patterns and type safety.
Completely domain-agnostic and reusable across any HTTP client.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping

from flext_api import c, m, p, r, t, u


class FlextApiUtilitiesSettingsManager:
    """Generic configuration management for HTTP clients with flext-core patterns.

    Provides type-safe configuration handling with validation and defaults,
    following railway-oriented error handling throughout. Domain-agnostic.
    """

    _config: t.JsonObject | None
    _client_config: m.Api.ClientConfig | None

    def __init__(self) -> None:
        """Initialize configuration manager."""
        self._config = None
        self._client_config = None

    @property
    def settings(self) -> t.JsonObject | None:
        """Get current configuration."""
        return self._config

    def configure(
        self,
        settings: t.ScalarMapping | None = None,
    ) -> p.Result[bool]:
        """Configure the HTTP client with type safety and validation - no fallbacks."""
        try:
            processed_result = self._process_config(
                {} if settings is None else settings
            )
            if processed_result.failure:
                self._client_config = None
                return r[bool].fail(
                    processed_result.error or "Configuration processing failed",
                )
            self._config = processed_result.value
            client_config_result = self._build_client_config()
            if client_config_result.failure:
                self._client_config = None
                return r[bool].fail(
                    client_config_result.error or "Configuration validation failed",
                )
            self._client_config = client_config_result.value
            self._config = {
                **self._config,
                "base_url": self._client_config.base_url,
                "timeout": self._client_config.timeout,
                "max_retries": self._client_config.max_retries,
                "headers": self._client_config.headers,
                "verify_ssl": self._client_config.verify_ssl,
            }
            return r[bool].ok(True)
        except (ValueError, TypeError, KeyError, ConnectionError) as e:
            error_msg = f"Configuration failed: {e}"
            return r[bool].fail(error_msg)

    def client_config(self) -> p.Result[m.Api.ClientConfig]:
        """Get validated client configuration - no fallbacks."""
        if self._client_config is not None:
            return r[m.Api.ClientConfig].ok(self._client_config)
        if self._config is None:
            return r[m.Api.ClientConfig].fail("No configuration set")
        client_config_result = self._build_client_config()
        if client_config_result.failure:
            return r[m.Api.ClientConfig].fail(
                client_config_result.error or "Configuration validation failed",
            )
        self._client_config = client_config_result.value
        return r[m.Api.ClientConfig].ok(self._client_config)

    def _normalize_value(
        self,
        key: str,
        *,
        value: t.Scalar,
    ) -> p.Result[t.ContainerValue]:
        """Normalize configuration value based on key type - no fallbacks."""
        if key == "headers" and isinstance(value, Mapping):
            return u.try_(
                lambda: t.Api.STR_MAPPING_ADAPTER.validate_python(value),
                catch=(c.ValidationError, TypeError, ValueError),
            ).map_error(lambda e: f"Failed to validate headers mapping: {e}")
        if key == "headers" and isinstance(value, str):
            return u.try_(
                lambda: t.Api.STR_MAPPING_ADAPTER.validate_json(value),
                catch=(c.ValidationError, TypeError, ValueError),
            ).map_error(lambda e: f"Failed to parse headers JSON: {e}")
        if key in {"log_requests", "log_responses", "verify_ssl"}:
            return u.try_(
                lambda: t.bool_adapter().validate_python(value),
                catch=(c.ValidationError, TypeError, ValueError),
            ).map_error(lambda e: f"Invalid {key} value: {e}")
        return r[t.ContainerValue].ok(value)

    def _process_config(
        self,
        settings: t.ScalarMapping,
    ) -> p.Result[t.JsonObject]:
        """Process and normalize configuration values - no fallbacks."""
        processed: t.MutableContainerValueMapping = {}
        for key, value in settings.items():
            normalize_result = self._normalize_value(key, value=value)
            if normalize_result.failure:
                return r[t.JsonObject].fail(
                    normalize_result.error or "Value normalization failed",
                )
            processed[key] = normalize_result.value
        return r[t.JsonObject].ok(processed)

    def _build_client_config(self) -> p.Result[m.Api.ClientConfig]:
        """Build validated client configuration from the normalized config bag."""
        if self._config is None:
            return r[m.Api.ClientConfig].fail("No configuration set")
        if "timeout" not in self._config:
            return r[m.Api.ClientConfig].fail("Timeout not specified in configuration")
        if "max_retries" not in self._config:
            return r[m.Api.ClientConfig].fail(
                "Max retries not specified in configuration",
            )
        headers_value = self._config.get("headers", {})
        if not isinstance(headers_value, Mapping):
            return r[m.Api.ClientConfig].fail(
                f"Invalid headers type: {type(headers_value)}",
            )
        client_config_payload: t.JsonObject = {
            "base_url": self._config.get("base_url", ""),
            "timeout": self._config["timeout"],
            "max_retries": self._config["max_retries"],
            "headers": headers_value,
            "verify_ssl": self._config.get("verify_ssl", True),
        }
        return u.try_(
            lambda: m.Api.ClientConfig.model_validate(client_config_payload),
            catch=(c.ValidationError, TypeError, ValueError),
        ).map_error(
            lambda e: f"Client configuration validation failed: {e}",
        )
