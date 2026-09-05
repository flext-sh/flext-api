"""HTTP transport option-resolution mixin.

Behavior-preserving MRO shard for :class:`FlextWebTransport`. Holds the
stateless httpx option resolvers and the public response-mapping projection.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_api.constants import c
from flext_api.models import m
from flext_api.typings import t


class FlextApiTransportsConfigMixin:
    """Stateless httpx option resolvers for the HTTP transport."""

    @staticmethod
    def _client_timeout(options: t.MappingKV[str, t.JsonValue]) -> float:
        """Resolve the httpx timeout option from validated scalar inputs."""
        raw_timeout = options.get("timeout")
        return (
            float(raw_timeout)
            if isinstance(raw_timeout, t.NUMERIC_TYPES)
            else c.Api.DEFAULT_TIMEOUT
        )

    @staticmethod
    def _client_follow_redirects(options: t.MappingKV[str, t.JsonValue]) -> bool:
        """Resolve the httpx follow-redirects option."""
        raw_follow_redirects = options.get("follow_redirects")
        return raw_follow_redirects if isinstance(raw_follow_redirects, bool) else True

    @staticmethod
    def _client_max_redirects(options: t.MappingKV[str, t.JsonValue]) -> int:
        """Resolve the httpx maximum redirects option."""
        raw_max_redirects = options.get("max_redirects")
        return raw_max_redirects if isinstance(raw_max_redirects, int) else 20

    @staticmethod
    def _response_mapping(response: m.Api.HttpResponse) -> t.Api.HttpResponseDict:
        """Convert the central response model to the public mapping contract."""
        return {
            "status_code": response.status_code,
            "headers": response.headers,
            "body": response.body,
            "request_id": response.request_id,
        }


__all__: list[str] = ["FlextApiTransportsConfigMixin"]
