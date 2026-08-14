"""Generic HTTP Configuration - FlextSettings-based, namespaced under ``settings.Api``.

HTTP configuration using FlextSettings with env var support (``FLEXT_API_`` prefix).
100% GENERIC - no domain coupling. Single responsibility.

Layer-0: imports only stdlib + ``pydantic_settings`` + ``FlextSettings`` / ``m`` / ``u`` facades. The universal runtime
fields (``debug``/``trace``/``log_level``/``timezone``/``async_logging``) come from
``FlextSettings`` by MRO and are NOT redeclared here. Every project field lives
inside the ``Api`` namespace group with simple scalar types so each is settable via
``.env`` / env vars / params (``FLEXT_API_API__BASE_URL`` …). Defaults are inlined
from ``flext_api._constants`` (SSOT); mutable bags use ``default_factory=dict``.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

from pydantic_settings import SettingsConfigDict

from flext_core import FlextSettings, m, u


class FlextApiSettings(FlextSettings):
    """Validated settings consumed by API facade and HTTP client; all project fields under ``settings.Api.*``."""

    model_config = SettingsConfigDict(
        env_prefix="FLEXT_API_", env_nested_delimiter="__", extra="ignore"
    )

    class _Api(m.BaseModel):
        """Namespaced API settings (HTTP client defaults)."""

        base_url: Annotated[
            str,
            m.Field(
                default="http://localhost:8000",
                description="Base URL for relative requests",
            ),
        ]
        timeout: Annotated[
            float,
            m.Field(default=30.0, description="Default request timeout in seconds"),
        ]
        max_retries: Annotated[
            int, m.Field(default=3, description="Maximum retry attempts")
        ]
        verify_ssl: Annotated[
            bool, m.Field(default=True, description="Enable TLS certificate check")
        ]
        default_headers: Annotated[
            dict[str, str],
            m.Field(
                default_factory=dict,
                description="Default headers applied to all requests",
            ),
        ]
        headers: Annotated[
            dict[str, str],
            m.Field(default_factory=dict, description="Compatibility headers bag"),
        ]
        log_requests: Annotated[
            bool, m.Field(default=False, description="Log outbound requests")
        ]
        log_responses: Annotated[
            bool, m.Field(default=False, description="Log inbound responses")
        ]

    if TYPE_CHECKING:
        Api: _Api
    else:
        Api: _Api = m.Field(
            default_factory=_Api, description="Namespaced API settings."
        )

    @u.model_validator(mode="before")
    @classmethod
    def _lift_flat_api_fields(cls, data: object) -> object:
        """Fold top-level ``_Api`` field kwargs into the ``Api`` namespace."""
        if not isinstance(data, dict):
            return data
        api_fields = cls._Api.model_fields
        flat = {key: data[key] for key in api_fields if key in data}
        if not flat:
            return data
        merged = {key: value for key, value in data.items() if key not in api_fields}
        existing = merged.get("Api")
        base = dict(existing) if isinstance(existing, dict) else {}
        merged["Api"] = {**base, **flat}
        return merged


settings: FlextApiSettings = FlextApiSettings.fetch_global()
"""Pre-instantiated project settings singleton — ``from flext_api import settings``."""

__all__: list[str] = ["FlextApiSettings", "settings"]
