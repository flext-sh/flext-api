"""Unit tests for FlextApiLifecycleManager - HTTP resource lifecycle management.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import math
from collections import UserDict

from flext_api.lifecycle_manager import FlextApiLifecycleManager


class MockSyncResource:
    """Mock sync resource with close method only."""

    def __init__(self) -> None:
        """Initialize mock sync resource."""
        self.closed = False
        self.close_called = False

    def close(self) -> None:
        """Sync close method."""
        self.close_called = True
        self.closed = True


class MockResourceWithoutClose:
    """Mock resource without close methods."""

    def __init__(self) -> None:
        """Initialize mock resource without close method."""
        self.data = "test"


class TestFlextApiLifecycleManager:
    """Test FlextApiLifecycleManager HTTP resource lifecycle management."""

    def test_manage_sync_http_resource_with_close(self) -> None:
        """Test managing sync resource with close method."""
        resource = MockSyncResource()

        managed = FlextApiLifecycleManager.manage_sync_http_resource(resource)

        assert managed is resource
        assert resource.close_called
        assert resource.closed

    def test_manage_sync_http_resource_without_close(self) -> None:
        """Test managing sync resource without close method."""
        resource = MockResourceWithoutClose()

        managed = FlextApiLifecycleManager.manage_sync_http_resource(resource)

        assert managed is resource
        # Should not raise even without close

    def test_manage_sync_http_resource_with_none(self) -> None:
        """Test managing None resource."""
        managed = FlextApiLifecycleManager.manage_sync_http_resource(None)

        assert managed is None

    def test_manage_sync_http_resource_with_string(self) -> None:
        """Test managing string resource."""
        resource = "test_string"

        managed = FlextApiLifecycleManager.manage_sync_http_resource(resource)

        assert managed == resource

    def test_manage_sync_http_resource_multiple_resources(self) -> None:
        """Test managing multiple sync resources in sequence."""
        resource1 = MockSyncResource()
        resource2 = MockSyncResource()

        FlextApiLifecycleManager.manage_sync_http_resource(resource1)
        assert resource1.closed

        FlextApiLifecycleManager.manage_sync_http_resource(resource2)
        assert resource2.closed

    def test_manage_sync_http_resource_non_callable_close(self) -> None:
        """Test managing sync resource with non-callable close attribute."""
        class ResourceWithNonCallableClose:
            close = "not_callable"

        resource = ResourceWithNonCallableClose()

        # Should not raise, just skip non-callable close
        FlextApiLifecycleManager.manage_sync_http_resource(resource)

    def test_manage_sync_http_resource_with_dict(self) -> None:
        """Test managing dictionary resource."""
        resource = {"key": "value"}

        managed = FlextApiLifecycleManager.manage_sync_http_resource(resource)

        assert managed == resource

    def test_manage_sync_http_resource_with_list(self) -> None:
        """Test managing list resource."""
        resource = [1, 2, 3]

        managed = FlextApiLifecycleManager.manage_sync_http_resource(resource)

        assert managed == resource

    def test_manage_sync_http_resource_with_close_dict(self) -> None:
        """Test managing resource that is a dict with close method."""
        class DictWithClose(UserDict):
            def close(self) -> None:
                pass

        resource = DictWithClose({"key": "value"})
        managed = FlextApiLifecycleManager.manage_sync_http_resource(resource)

        assert managed == resource

    def test_manage_sync_http_resource_with_int(self) -> None:
        """Test managing integer resource."""
        resource = 42

        managed = FlextApiLifecycleManager.manage_sync_http_resource(resource)

        assert managed == resource

    def test_manage_sync_http_resource_with_float(self) -> None:
        """Test managing float resource."""
        resource = math.pi

        managed = FlextApiLifecycleManager.manage_sync_http_resource(resource)

        assert managed == resource

    def test_manage_sync_http_resource_with_bool(self) -> None:
        """Test managing boolean resource."""
        resource = True

        managed = FlextApiLifecycleManager.manage_sync_http_resource(resource)

        assert managed == resource

    def test_manage_sync_http_resource_with_empty_string(self) -> None:
        """Test managing empty string resource."""
        resource = ""

        managed = FlextApiLifecycleManager.manage_sync_http_resource(resource)

        assert managed == resource

    def test_manage_sync_http_resource_with_tuple(self) -> None:
        """Test managing tuple resource."""
        resource = (1, 2, 3)

        managed = FlextApiLifecycleManager.manage_sync_http_resource(resource)

        assert managed == resource

    def test_manage_sync_http_resource_with_set(self) -> None:
        """Test managing set resource."""
        resource = {1, 2, 3}

        managed = FlextApiLifecycleManager.manage_sync_http_resource(resource)

        assert managed == resource

    def test_manage_sync_http_resource_callable_close_is_called(self) -> None:
        """Test that callable close attribute is actually called."""
        call_count = 0

        class ResourceWithCallableClose:
            def close(self) -> None:
                nonlocal call_count
                call_count += 1

        resource = ResourceWithCallableClose()
        FlextApiLifecycleManager.manage_sync_http_resource(resource)

        assert call_count == 1

    def test_manage_sync_http_resource_returns_same_reference(self) -> None:
        """Test that manage_sync_http_resource returns same object reference."""
        resource = MockSyncResource()

        managed = FlextApiLifecycleManager.manage_sync_http_resource(resource)

        assert managed is resource  # Same object, not copy

    def test_lifecycle_manager_has_required_methods(self) -> None:
        """Test that FlextApiLifecycleManager has required methods."""
        assert hasattr(FlextApiLifecycleManager, "manage_http_resource")
        assert hasattr(FlextApiLifecycleManager, "manage_sync_http_resource")
        assert callable(FlextApiLifecycleManager.manage_http_resource)
        assert callable(FlextApiLifecycleManager.manage_sync_http_resource)
