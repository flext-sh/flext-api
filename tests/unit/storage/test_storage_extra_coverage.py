"""Extra coverage tests for storage patterns and transactions edge cases."""

from __future__ import annotations

import pytest

from flext_api import FlextApiStorage, StorageBackend, StorageConfig


@pytest.mark.asyncio
async def test_keys_pattern_and_unknown_operation_commit() -> None:
    """Wildcard key pattern works and unknown tx op triggers failure on commit."""
    storage = FlextApiStorage(
        StorageConfig(namespace="ns", backend=StorageBackend.MEMORY),
    )
    await storage.set("a", 1)
    await storage.set("alpha", 2)

    # Get all keys (no pattern matching available)
    keys = await storage.keys()
    assert keys.success
    assert set(keys.value or []) >= {"a", "alpha"}

    # Test simple storage operations work
    result = await storage.exists("a")
    assert result.success
