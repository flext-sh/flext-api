"""Tests for storage module.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import pytest

from flext_api import FlextApiStorage, StorageConfig


class TestFlextApiStorage:
    """Test cases for storage functionality."""

    def test_storage_creation(self) -> None:
        """Test creating storage instance."""
        storage = FlextApiStorage(StorageConfig())
        assert storage is not None

    @pytest.mark.asyncio
    async def test_get_nonexistent_key(self) -> None:
        """Test getting non-existent key returns appropriate result."""
        storage = FlextApiStorage(StorageConfig())
        result = await storage.get("nonexistent")
        # Storage can either return success with None or failure with error - both are valid patterns
        if result.success:
            assert result.value is None
        else:
            assert "not found" in (result.error or "").lower()

    @pytest.mark.asyncio
    async def test_set_and_get(self) -> None:
        """Test setting and getting value."""
        storage = FlextApiStorage(StorageConfig())
        set_result = await storage.set("key1", "value1")
        assert set_result.success

        result = await storage.get("key1")
        assert result.success
        if result.value != "value1":
            msg = f"Expected 'value1', got {result.value}"
            raise AssertionError(msg)

    @pytest.mark.asyncio
    async def test_delete_existing_key(self) -> None:
        """Test deleting existing key."""
        storage = FlextApiStorage(StorageConfig())
        set_result = await storage.set("key1", "value1")
        assert set_result.success

        result = await storage.delete("key1")
        assert result.success
        if not result.value:
            msg = f"Expected True, got {result.value}"
            raise AssertionError(msg)

        # Key should be gone
        get_result = await storage.get("key1")
        # Storage can either return success with None or failure with error - both are valid patterns
        if get_result.success:
            assert get_result.value is None
        else:
            assert "not found" in (get_result.error or "").lower()

    @pytest.mark.asyncio
    async def test_delete_nonexistent_key(self) -> None:
        """Test deleting non-existent key."""
        storage = FlextApiStorage(StorageConfig())
        result = await storage.delete("nonexistent")
        assert result.success
        if result.value:
            msg = f"Expected False, got {result.value}"
            raise AssertionError(msg)

    @pytest.mark.asyncio
    async def test_overwrite_key(self) -> None:
        """Test overwriting existing key."""
        storage = FlextApiStorage(StorageConfig())

        # Set initial value
        set1_result = await storage.set("key1", "value1")
        assert set1_result.success

        # Overwrite with new value
        set2_result = await storage.set("key1", "value2")
        assert set2_result.success

        result = await storage.get("key1")
        assert result.success
        if result.value != "value2":
            msg = f"Expected 'value2', got {result.value}"
            raise AssertionError(msg)
