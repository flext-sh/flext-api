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

    # Pattern matching (wildcard)
    keys = await storage.keys("a*")
    assert keys.success
    assert set(keys.data or []) >= {"a", "alpha"}

    # Inject unknown operation in transaction to hit error branch
    tx = storage.begin_transaction()
    storage._transactions[tx].operations.append(("unknown", "ns:zzz", None))
    res = await storage.commit_transaction(tx)
    assert not res.success
