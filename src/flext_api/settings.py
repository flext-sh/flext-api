"""Generic HTTP Configuration - FlextSettings-based.

HTTP configuration using FlextSettings with env var support (FLEXT_API_ prefix).
100% GENERIC - no domain coupling. Single responsibility.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import Annotated, ClassVar

from flext_api import c, t
from flext_core import FlextSettingsBase, m, u


class FlextApiSettings(FlextSettingsBase):
    """Validated settings consumed by API facade and HTTP client."""

    model_config: ClassVar[m.SettingsConfigDict] = m.SettingsConfigDict(
        env_prefix="FLEXT_API_",
        extra="ignore",
    )

    base_url: Annotated[
        str,
        u.Field(description="Base URL for relative requests"),
    ] = c.Api.DEFAULT_BASE_URL
    timeout: Annotated[
        t.PositiveTimeout,
        u.Field(description="Default request timeout in seconds"),
    ] = c.Api.DEFAULT_TIMEOUT
    max_retries: Annotated[
        t.RetryCount,
        u.Field(description="Maximum retry attempts"),
    ] = c.MAX_RETRY_ATTEMPTS
    verify_ssl: Annotated[
        bool,
        u.Field(description="Enable TLS certificate check"),
    ] = True
    default_headers: Annotated[
        t.StrMapping,
        u.Field(description="Default headers applied to all requests"),
    ] = u.Field(default_factory=dict)
    headers: Annotated[
        t.StrMapping,
        u.Field(description="Compatibility headers bag"),
    ] = u.Field(default_factory=dict)
    log_requests: Annotated[
        bool,
        u.Field(description="Log outbound requests"),
    ] = False
    log_responses: Annotated[
        bool,
        u.Field(description="Log inbound responses"),
    ] = False


__all__: t.MutableSequenceOf[str] = ["FlextApiSettings"]
