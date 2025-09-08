"""Tests for storage module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import sys

sys.path.insert(0, "/home/marlonsc/flext/flext-core/src")

from flext_tests import FlextMatchers

from flext_api import FlextApiStorage


class TestFlextApiStorage:
    """Test cases for storage functionality using flext_tests utilities."""

    def test_storage_creation(self) -> None:
        """Test creating storage instance."""
        storage = FlextApiStorage(())
        assert storage is not None

    def test_get_nonexistent_key(self) -> None:
        """Test getting non-existent key returns appropriate result."""
        storage = FlextApiStorage(())
        result = storage.get("nonexistent")

        # Use FlextMatchers for proper result assertion
        FlextMatchers.assert_result_failure(result)
        assert "not found" in (result.error or "").lower()

    def test_set_and_get(self) -> None:
        """Test setting and getting value."""
        storage = FlextApiStorage(())

        # Use simple value for storage (not tuple format)
        set_result = storage.set("key1", "value1")
        FlextMatchers.assert_result_success(set_result)

        result = storage.get("key1")
        FlextMatchers.assert_result_success(result)

        # The result should contain the simple value
        assert result.value == "value1"

    def test_delete_existing_key(self) -> None:
        """Test deleting existing key."""
        storage = FlextApiStorage(())

        # Use simple value for storage
        set_result = storage.set("key1", "value1")
        FlextMatchers.assert_result_success(set_result)

        result = storage.delete("key1")
        FlextMatchers.assert_result_success(result)
        assert result.value is None  # Delete returns None on success

        # Key should be gone
        get_result = storage.get("key1")
        FlextMatchers.assert_result_failure(get_result)
        assert "not found" in (get_result.error or "").lower()

    def test_delete_nonexistent_key(self) -> None:
        """Test deleting non-existent key."""
        storage = FlextApiStorage(())
        result = storage.delete("nonexistent")

        # Deleting nonexistent key should return failure
        FlextMatchers.assert_result_failure(result)
        assert "not found" in (result.error or "").lower()

    def test_overwrite_key(self) -> None:
        """Test overwriting existing key."""
        storage = FlextApiStorage(())

        # Set initial value
        set1_result = storage.set("key1", "value1")
        FlextMatchers.assert_result_success(set1_result)

        # Overwrite with new value
        set2_result = storage.set("key1", "value2")
        FlextMatchers.assert_result_success(set2_result)

        result = storage.get("key1")
        FlextMatchers.assert_result_success(result)
        assert result.value == "value2"  # Simple value comparison
