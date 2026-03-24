"""Generic HTTP Configuration - Pure Pydantic v2.

Minimal HTTP configuration using Pydantic v2 with flext-core constants.
100% GENERIC - no domain coupling. Single responsibility.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping

from typing import Annotated

from flext_core import FlextModels, t
from pydantic import Field

from flext_api import c


class FlextApiSettings(FlextModels.Value):
    """Validated settings consumed by API facade and HTTP client."""

    base_url: Annotated[
        str,
        Field(
            default=c.Api.DEFAULT_BASE_URL,
            description="Base URL for relative requests",
        ),
    ]
    timeout: Annotated[
        t.PositiveTimeout,
        Field(
            default=c.Api.DEFAULT_TIMEOUT,
            description="Default request timeout in seconds",
        ),
    ]
    max_retries: Annotated[
        t.RetryCount,
        Field(
            default=c.DEFAULT_MAX_RETRY_ATTEMPTS,
            description="Maximum retry attempts",
        ),
    ]
    verify_ssl: Annotated[
        bool,
        Field(default=True, description="Enable TLS certificate check"),
    ]
    default_headers: Annotated[
        Mapping[str, str],
        Field(
            default_factory=dict,
            description="Default headers applied to all requests",
        ),
    ]
    headers: Annotated[
        Mapping[str, str],
        Field(
            default_factory=dict,
            description="Compatibility headers bag",
        ),
    ]
    log_requests: Annotated[
        bool,
        Field(default=False, description="Log outbound requests"),
    ]
    log_responses: Annotated[
        bool,
        Field(default=False, description="Log inbound responses"),
    ]


__all__ = ["FlextApiSettings"]
