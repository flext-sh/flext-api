"""Generic HTTP Config Manager - Domain-agnostic configuration management.

This module provides FlextApiUtilitiesSettingsManager, a generic class for managing
HTTP client configuration with flext-core patterns and type safety.
Completely domain-agnostic and reusable across any HTTP client.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping

from flext_api.constants import c
from flext_api.models import m
from flext_api.protocols import p
from flext_api.typings import t
from flext_core import r
from flext_web import u


class FlextApiUtilitiesSettingsManager:
    """Generic configuration management for HTTP clients with flext-core patterns.

    Provides type-safe configuration handling with validation and defaults,
    following railway-oriented error handling throughout. Domain-agnostic.
    """

    _client_config: m.Api.ClientConfig | None

    def __init__(self) -> None:
        """Initialize configuration manager."""
        self._client_config = None

    @property
    def settings(self) -> m.Api.ClientConfig | None:
        """Current configuration."""
        return self._client_config

    def configure(self, settings: t.ScalarMapping | None = None) -> p.Result[bool]:
        """Configure client settings through canonical ClientConfig model."""
        try:
            client_config_result = self._build_client_config(
                {} if settings is None else settings
            )
            if client_config_result.failure:
                self._client_config = None
                return r[bool].fail(
                    client_config_result.error or "Configuration validation failed"
                )
            self._client_config = client_config_result.value
            return r[bool].ok(True)
        except c.EXC_HTTP_PROCESSING as e:
            error_msg = f"Configuration failed: {e}"
            return r[bool].fail(error_msg)

    def client_config(self) -> p.Result[m.Api.ClientConfig]:
        """Get validated client configuration - no fallbacks."""
        if self._client_config is not None:
            return r[m.Api.ClientConfig].ok(self._client_config)
        return r[m.Api.ClientConfig].fail("No configuration set")

    def _normalize_value(
        self, key: str, *, value: t.Scalar | t.StrMapping
    ) -> p.Result[t.JsonPayload]:
        """Normalize configuration value based on key type - no fallbacks."""
        result: p.Result[t.JsonPayload]
        match key:
            case "headers" if isinstance(value, Mapping):
                validated = t.Api.STR_MAPPING_ADAPTER.validate_python(value)
                result = r[t.JsonPayload].ok(dict(validated))
            case "headers" if isinstance(value, str):
                parsed_result = u.try_(
                    lambda: t.Api.STR_MAPPING_ADAPTER.validate_json(value),
                    catch=(c.ValidationError, TypeError, ValueError),
                ).map_error(lambda e: f"Failed to parse headers JSON: {e}")
                result = (
                    r[t.JsonPayload].fail(parsed_result.error)
                    if parsed_result.failure
                    else r[t.JsonPayload].ok(parsed_result.value)
                )
            case "log_requests" | "log_responses" | "verify_ssl":
                bool_result = u.try_(
                    lambda: t.bool_adapter().validate_python(value),
                    catch=(c.ValidationError, TypeError, ValueError),
                ).map_error(lambda e: f"Invalid {key} value: {e}")
                result = (
                    r[t.JsonPayload].fail(bool_result.error)
                    if bool_result.failure
                    else r[t.JsonPayload].ok(bool_result.value)
                )
            case _:
                result = r[t.JsonPayload].ok(u.normalize_to_container(value))
        return result

    def _build_client_config(
        self, settings: t.ScalarMapping
    ) -> p.Result[m.Api.ClientConfig]:
        """Build typed ClientConfig from scalar settings payload."""
        processed: MutableMapping[str, t.JsonPayload] = {}
        for key, raw_value in settings.items():
            normalize_result = self._normalize_value(key, value=raw_value)
            if normalize_result.failure:
                return r[m.Api.ClientConfig].fail(
                    normalize_result.error or "Value normalization failed"
                )
            processed[key] = normalize_result.value
        headers_value = processed.get("headers", {})
        if not isinstance(headers_value, Mapping):
            return r[m.Api.ClientConfig].fail(
                f"Invalid headers type: {type(headers_value)}"
            )
        timeout_result = u.try_(
            lambda: t.Api.FLOAT_ADAPTER.validate_python(
                processed.get("timeout", c.Api.DEFAULT_TIMEOUT)
            ),
            catch=(c.ValidationError, TypeError, ValueError),
        )
        retries_result = u.try_(
            lambda: t.Api.INTEGER_ADAPTER.validate_python(
                processed.get("max_retries", c.MAX_RETRY_ATTEMPTS)
            ),
            catch=(c.ValidationError, TypeError, ValueError),
        )
        headers_result = u.try_(
            lambda: t.Api.STR_MAPPING_ADAPTER.validate_python(headers_value),
            catch=(c.ValidationError, TypeError, ValueError),
        )
        verify_result = u.try_(
            lambda: t.bool_adapter().validate_python(processed.get("verify_ssl", True)),
            catch=(c.ValidationError, TypeError, ValueError),
        )
        for result in (timeout_result, retries_result, headers_result, verify_result):
            if result.failure:
                return r[m.Api.ClientConfig].fail_op(
                    "Client configuration validation", result.error
                )
        config_model = m.Api.ClientConfig(
            base_url=str(processed.get("base_url", c.Api.DEFAULT_BASE_URL)),
            timeout=timeout_result.value,
            max_retries=retries_result.value,
            headers=headers_result.value,
            verify_ssl=verify_result.value,
        )
        return r[m.Api.ClientConfig].ok(config_model)
