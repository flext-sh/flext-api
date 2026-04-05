"""Generic HTTP Configuration - FlextSettings-based.

HTTP configuration using FlextSettings with env var support (FLEXT_API_ prefix).
100% GENERIC - no domain coupling. Single responsibility.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import Annotated

from pydantic import Field
from pydantic_settings import SettingsConfigDict

from flext_api import c, t
from flext_core.settings import FlextSettings


@FlextSettings.auto_register("api")
class FlextApiSettings(FlextSettings):
    """Validated settings consumed by API facade and HTTP client."""

    model_config = SettingsConfigDict(env_prefix="FLEXT_API_", extra="ignore")

    base_url: Annotated[
        str,
        Field(description="Base URL for relative requests"),
    ] = c.Api.DEFAULT_BASE_URL
    timeout: Annotated[
        t.PositiveTimeout,
        Field(description="Default request timeout in seconds"),
    ] = c.Api.DEFAULT_TIMEOUT
    max_retries: Annotated[
        t.RetryCount,
        Field(description="Maximum retry attempts"),
    ] = c.MAX_RETRY_ATTEMPTS
    verify_ssl: Annotated[
        bool,
        Field(description="Enable TLS certificate check"),
    ] = True
    default_headers: Annotated[
        t.StrMapping,
        Field(description="Default headers applied to all requests"),
    ] = Field(default_factory=dict)
    headers: Annotated[
        t.StrMapping,
        Field(description="Compatibility headers bag"),
    ] = Field(default_factory=dict)
    log_requests: Annotated[
        bool,
        Field(description="Log outbound requests"),
    ] = False
    log_responses: Annotated[
        bool,
        Field(description="Log inbound responses"),
    ] = False


__all__ = ["FlextApiSettings"]
