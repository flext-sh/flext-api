"""Behavioral tests for the flext-api async client public contract.

Exercises observable behavior of the async client facade, models, serializers,
and result-returning operations — never implementation details. Settings are
consumed in the canonical strict form: the published ``settings`` singleton,
cloned (never rebuilt) when a test needs specific values.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_api.services import FlextApiAsyncClient
from tests import c, settings, tm, u


class TestsFlextApiAsyncClientSmoke:
    """Behavioral contract of the flext-api async client public surface."""

    # ---- Client / facade contract ---------------------------------------

    @c.Tests.MARK.asyncio
    @staticmethod
    async def test_async_client_exposes_settings_through_public_properties() -> None:
        """The async client surfaces the settings namespace it was built from."""
        configured = settings.clone(
            Api={"base_url": "https://service.example", "timeout": 9.5},
        )
        client = FlextApiAsyncClient(runtime_settings=configured)
        tm.that(client.base_url, eq=configured.Api.base_url)
        tm.that(client.timeout, eq=u.Tests.approx(configured.Api.timeout))

    @c.Tests.MARK.asyncio
    @staticmethod
    async def test_async_client_execute_reports_success() -> None:
        """A configured async client executes its lifecycle successfully."""
        client = FlextApiAsyncClient(runtime_settings=settings)
        result = client.execute()
        tm.ok(result.success)
        tm.ok(result.value)
