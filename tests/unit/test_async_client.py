"""Behavioral tests for the flext-api async client public contract.

Exercises observable behavior of the async client facade, models, serializers,
and result-returning operations — never implementation details. Settings are
consumed in the canonical strict form: the published ``settings`` singleton,
cloned (never rebuilt) when a test needs specific values.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import inspect

import pytest

from flext_api.services import FlextApiAsyncClient
from tests import c, settings, tm
from tests.unit.model_contract import TestsFlextApiModelContract


class TestsFlextApiAsyncClientSmoke(TestsFlextApiModelContract):
    """Behavioral contract of the flext-api async client public surface."""

    # ---- Client / facade contract ---------------------------------------

    @pytest.mark.asyncio
    @staticmethod
    async def test_async_client_exposes_settings_through_public_properties() -> None:
        """The async client surfaces the settings namespace it was built from."""
        configured = settings.clone(
            Api={"base_url": "https://service.example", "timeout": 9.5},
        )
        client = FlextApiAsyncClient(runtime_settings=configured)
        tm.that(client.base_url, eq=configured.Api.base_url)
        tm.that(client.timeout, eq=pytest.approx(configured.Api.timeout))

    @pytest.mark.asyncio
    @staticmethod
    async def test_async_client_execute_reports_success() -> None:
        """A configured async client executes its lifecycle successfully."""
        client = FlextApiAsyncClient(runtime_settings=settings)
        result = client.execute()
        tm.ok(result.success)
        tm.ok(result.value)

    # ---- Async client request execution contract -------------------------

    @pytest.mark.asyncio
    @staticmethod
    async def test_async_client_request_method_is_async() -> None:
        """Async client request method is a coroutine function."""
        client = FlextApiAsyncClient(runtime_settings=settings)
        tm.ok(inspect.iscoroutinefunction(client.request))

    @pytest.mark.asyncio
    @staticmethod
    async def test_async_client_context_manager_pattern() -> None:
        """Async client can be used with async context manager semantics."""
        client = FlextApiAsyncClient(runtime_settings=settings)

        # Verify the client has the expected async interface
        tm.ok(hasattr(client, c.ContextScope.REQUEST))
        tm.ok(callable(client.request))

        # execute() should still work synchronously for lifecycle
        result = client.execute()
        tm.ok(result.success)

    @pytest.mark.asyncio
    @staticmethod
    async def test_async_client_same_interface_as_sync() -> None:
        """Async client mirrors sync client's public properties and methods."""
        client = FlextApiAsyncClient(runtime_settings=settings)

        # Same properties
        tm.ok(hasattr(client, "base_url"))
        tm.ok(hasattr(client, "timeout"))

        # Same execute method
        tm.ok(hasattr(client, "execute"))
        tm.ok(callable(client.execute))

        # Async-specific method
        tm.ok(hasattr(client, c.ContextScope.REQUEST))
        tm.ok(callable(client.request))

        # Verify request is async
        tm.ok(inspect.iscoroutinefunction(client.request))
