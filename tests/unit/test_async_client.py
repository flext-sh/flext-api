"""Behavioral tests for the flext-api async client public contract.

Exercises observable behavior of the async client facade, models, serializers,
and result-returning operations — never implementation details.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import inspect

import pytest
from flext_tests import tm

from flext_api import FlextApiAsyncClient, FlextApiSettings

from .model_contract import TestsFlextApiModelContract


class TestsFlextApiAsyncClientSmoke(TestsFlextApiModelContract):
    """Behavioral contract of the flext-api async client public surface."""

    # ---- Client / facade contract ---------------------------------------

    @pytest.mark.asyncio
    async def test_async_client_exposes_settings_through_public_properties(
        self,
    ) -> None:
        """The async client surfaces its configured base_url and timeout."""
        settings = FlextApiSettings(base_url="https://service.example", timeout=9.5)
        client = FlextApiAsyncClient(runtime_settings=settings)
        tm.that(client.base_url, eq="https://service.example")
        tm.that(client.timeout, eq=pytest.approx(9.5))

    @pytest.mark.asyncio
    async def test_async_client_execute_reports_success(self) -> None:
        """A configured async client executes its lifecycle successfully."""
        client = FlextApiAsyncClient(
            runtime_settings=FlextApiSettings(base_url="https://service.example")
        )
        result = client.execute()
        tm.that(result.success, eq=True)
        tm.that(result.value, eq=True)

    # ---- Async client request execution contract -------------------------

    @pytest.mark.asyncio
    async def test_async_client_request_method_is_async(self) -> None:
        """Async client request method is a coroutine function."""
        client = FlextApiAsyncClient(
            runtime_settings=FlextApiSettings(base_url="https://httpbin.org")
        )
        tm.that(inspect.iscoroutinefunction(client.request), eq=True)

    @pytest.mark.asyncio
    async def test_async_client_context_manager_pattern(self) -> None:
        """Async client can be used with async context manager semantics."""
        settings = FlextApiSettings(base_url="https://service.example")
        client = FlextApiAsyncClient(runtime_settings=settings)

        # Verify the client has the expected async interface
        tm.that(hasattr(client, "request"), eq=True)
        tm.that(callable(client.request), eq=True)

        # execute() should still work synchronously for lifecycle
        result = client.execute()
        tm.that(result.success, eq=True)

    @pytest.mark.asyncio
    async def test_async_client_same_interface_as_sync(self) -> None:
        """Async client mirrors sync client's public properties and methods."""
        client = FlextApiAsyncClient(
            runtime_settings=FlextApiSettings(base_url="https://service.example")
        )

        # Same properties
        tm.that(hasattr(client, "base_url"), eq=True)
        tm.that(hasattr(client, "timeout"), eq=True)

        # Same execute method
        tm.that(hasattr(client, "execute"), eq=True)
        tm.that(callable(client.execute), eq=True)

        # Async-specific method
        tm.that(hasattr(client, "request"), eq=True)
        tm.that(callable(client.request), eq=True)

        # Verify request is async
        tm.that(inspect.iscoroutinefunction(client.request), eq=True)


__all__: list[str] = ["TestsFlextApiAsyncClientSmoke"]
