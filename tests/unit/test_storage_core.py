"""Tests for storage module.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import pytest

from flext_api import FlextAPIStorage
from flext_api.storage import StorageConfig


class TestFlextAPIStorage:
    """Test cases for storage functionality."""

    def test_storage_creation(self) -> None:
        """Test creating storage instance."""
        storage = FlextAPIStorage(StorageConfig())
        assert storage is not None

    @pytest.mark.asyncio
    async def test_get_nonexistent_key(self) -> None:
        """Test getting non-existent key returns None."""
        storage = FlextAPIStorage(StorageConfig())
        result = await storage.get("nonexistent")
        assert result.success
        assert result.data is None

    @pytest.mark.asyncio
    async def test_set_and_get(self) -> None:
        """Test setting and getting value."""
        storage = FlextAPIStorage(StorageConfig())
        set_result = await storage.set("key1", "value1")
        assert set_result.success

        result = await storage.get("key1")
        assert result.success
        if result.data != "value1":
            msg = f"Expected 'value1', got {result.data}"
            raise AssertionError(msg)

    @pytest.mark.asyncio
    async def test_delete_existing_key(self) -> None:
        """Test deleting existing key."""
        storage = FlextAPIStorage(StorageConfig())
        set_result = await storage.set("key1", "value1")
        assert set_result.success

        result = await storage.delete("key1")
        assert result.success
        if not result.data:
            msg = f"Expected True, got {result.data}"
            raise AssertionError(msg)

        # Key should be gone
        get_result = await storage.get("key1")
        assert get_result.success
        assert get_result.data is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_key(self) -> None:
        """Test deleting non-existent key."""
        storage = FlextAPIStorage(StorageConfig())
        result = await storage.delete("nonexistent")
        assert result.success
        if result.data:
            msg = f"Expected False, got {result.data}"
            raise AssertionError(msg)

    @pytest.mark.asyncio
    async def test_overwrite_key(self) -> None:
        """Test overwriting existing key."""
        storage = FlextAPIStorage(StorageConfig())

        # Set initial value
        set1_result = await storage.set("key1", "value1")
        assert set1_result.success

        # Overwrite with new value
        set2_result = await storage.set("key1", "value2")
        assert set2_result.success

        result = await storage.get("key1")
        assert result.success
        if result.data != "value2":
            msg = f"Expected 'value2', got {result.data}"
            raise AssertionError(msg)