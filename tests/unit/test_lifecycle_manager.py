"""Comprehensive tests for FlextApiLifecycleManager.

Tests validate HTTP resource lifecycle management using real objects.
No mocks - uses objects with actual close methods.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import pytest

from flext_api.lifecycle_manager import FlextApiLifecycleManager, HttpResourceProtocol


class MockSyncResource:
    """Mock resource with sync close method."""

    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        """Close the resource."""
        self.closed = True


class MockAsyncResource:
    """Mock resource with async aclose method."""

    def __init__(self) -> None:
        self.closed = False

    async def aclose(self) -> None:
        """Close the resource asynchronously."""
        self.closed = True


class TestFlextApiLifecycleManager:
    """Test HTTP resource lifecycle management."""

    def test_manage_sync_http_resource_with_close(self) -> None:
        """Test synchronous resource management with close method."""
        resource = MockSyncResource()

        result = FlextApiLifecycleManager.manage_sync_http_resource(resource)

        assert result is resource
        assert resource.closed

    def test_manage_sync_http_resource_without_close(self) -> None:
        """Test synchronous resource management without close method."""
        resource = object()  # No close method

        result = FlextApiLifecycleManager.manage_sync_http_resource(resource)

        assert result is resource

    @pytest.mark.asyncio
    async def test_manage_http_resource_with_aclose(self) -> None:
        """Test async resource management with aclose method."""
        resource = MockAsyncResource()

        async with FlextApiLifecycleManager.manage_http_resource(resource) as res:
            assert res is resource
            assert not resource.closed

        assert resource.closed

    @pytest.mark.asyncio
    async def test_manage_http_resource_with_close_fallback(self) -> None:
        """Test async resource management with close method fallback."""
        resource = MockSyncResource()

        async with FlextApiLifecycleManager.manage_http_resource(resource) as res:
            assert res is resource
            assert not resource.closed

        assert resource.closed

    @pytest.mark.asyncio
    async def test_manage_http_resource_without_close_methods(self) -> None:
        """Test async resource management without close methods."""
        resource = object()  # No close or aclose

        async with FlextApiLifecycleManager.manage_http_resource(resource) as res:
            assert res is resource


class TestHttpResourceProtocol:
    """Test the HttpResourceProtocol."""

    def test_protocol_definition(self) -> None:
        """Test that the protocol is properly defined."""
        # This is more of a compile-time check, but we can verify it's importable
        assert HttpResourceProtocol is not None
        # Protocol is a typing construct, no runtime attributes
