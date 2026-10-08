"""Generic HTTP Configuration - FlextSettings-based, namespaced under ``settings.Api``.

HTTP configuration using FlextSettings with env var support (``FLEXT_API_`` prefix).
100% GENERIC - no domain coupling. Single responsibility.

Layer-0: imports only stdlib + ``pydantic_settings`` + ``FlextSettings``
/ ``m`` / ``u`` facades. The universal runtime
fields (``debug``/``trace``/``log_level``/``timezone``/``async_logging``) come from
``FlextSettings`` by MRO and are NOT redeclared here. Every project field lives
inside the ``Api`` namespace group with simple scalar types so each is settable via
``.env`` / env vars / params (``FLEXT_API_API__BASE_URL`` …). Defaults are inlined
from ``flext_api._constants`` (SSOT); mutable bags use ``default_factory=dict``.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Annotated

from flext_api import m
from flext_core import FlextSettings, t, u


class FlextApiSettings(FlextSettings):
    """Validated settings consumed by API facade and HTTP client.

    All project fields live under ``settings.Api.*``.
    """

    model_config = m.SettingsConfigDict(
        env_prefix="FLEXT_API_",
        env_nested_delimiter="__",
        extra="ignore",
    )

    class ApiSettings(m.BaseModel):
        """Namespaced API settings (HTTP client defaults).

        Defaults live on the assignment side (checker-visible optional
        constructor parameters); mutable bags keep ``default_factory``.
        """

        base_url: Annotated[
            str,
            m.Field(description="Base URL for relative requests"),
        ] = "http://localhost:8000"
        timeout: Annotated[
            float,
            m.Field(description="Default request timeout in seconds"),
        ] = 30.0
        max_retries: Annotated[
            int,
            m.Field(description="Maximum retry attempts"),
        ] = 3
        verify_ssl: Annotated[
            bool,
            m.Field(description="Enable TLS certificate check"),
        ] = True
        default_headers: t.StrMapping = m.Field(
            default_factory=dict[str, str],
            description="Default headers applied to all requests",
        )
        headers: t.StrMapping = m.Field(
            default_factory=dict[str, str],
            description="Compatibility headers bag",
        )
        log_requests: Annotated[
            bool,
            m.Field(description="Log outbound requests"),
        ] = False
        log_responses: Annotated[
            bool,
            m.Field(description="Log inbound responses"),
        ] = False

    Api: ApiSettings = m.Field(
        default_factory=ApiSettings,
        description="Namespaced API settings.",
    )

    @u.model_validator(mode="before")
    @classmethod
    def _lift_flat_api_fields(cls, data: t.JsonValue) -> t.JsonValue:
        """Fold top-level ``ApiSettings`` field kwargs into the ``Api`` namespace.

        Returns:
            The resulting ``t.JsonValue``.
        """
        if not isinstance(data, dict):
            return data
        api_fields = cls.ApiSettings.model_fields
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
