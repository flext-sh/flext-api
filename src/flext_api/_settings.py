"""Generic HTTP Configuration - FlextSettings-based, namespaced under ``settings.Api``.

HTTP configuration using FlextSettings with env var support (``FLEXT_API_`` prefix).
100% GENERIC - no domain coupling. Single responsibility.

Layer-0: imports only stdlib + pydantic + ``FlextSettings``. The universal runtime
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

from pydantic import BaseModel, Field
from pydantic_settings import SettingsConfigDict

from flext_core import FlextSettings


class FlextApiSettings(FlextSettings):
    """Validated settings consumed by API facade and HTTP client; all project fields under ``settings.Api.*``."""

    model_config = SettingsConfigDict(
        env_prefix="FLEXT_API_",
        env_nested_delimiter="__",
        extra="ignore",
    )

    class _Api(BaseModel):
        """Namespaced API settings (HTTP client defaults)."""

        base_url: Annotated[
            str,
            Field(default="http://localhost:8000", description="Base URL for relative requests"),
        ]
        timeout: Annotated[
            float,
            Field(default=30.0, description="Default request timeout in seconds"),
        ]
        max_retries: Annotated[
            int,
            Field(default=3, description="Maximum retry attempts"),
        ]
        verify_ssl: Annotated[
            bool,
            Field(default=True, description="Enable TLS certificate check"),
        ]
        default_headers: Annotated[
            dict[str, str],
            Field(default_factory=dict, description="Default headers applied to all requests"),
        ]
        headers: Annotated[
            dict[str, str],
            Field(default_factory=dict, description="Compatibility headers bag"),
        ]
        log_requests: Annotated[
            bool,
            Field(default=False, description="Log outbound requests"),
        ]
        log_responses: Annotated[
            bool,
            Field(default=False, description="Log inbound responses"),
        ]

    if TYPE_CHECKING:
        Api: _Api
    else:
        Api: _Api = Field(
            default_factory=_Api,
            description="Namespaced API settings.",
        )


settings: FlextApiSettings = FlextApiSettings.fetch_global()
"""Pre-instantiated project settings singleton — ``from flext_api import settings``."""

__all__: list[str] = ["FlextApiSettings", "settings"]
