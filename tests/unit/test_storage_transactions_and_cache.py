"""Transaction and cache behavior tests for storage backends."""

from __future__ import annotations

import pytest

from flext_api.api_storage import FlextApiStorage, StorageBackend, StorageConfig


@pytest.mark.asyncio
async def test_transaction_commit_set_and_delete_and_cache() -> None:
    """Transaction commit persists set/delete and populates cache."""
    storage = FlextApiStorage(
        StorageConfig(
            namespace="txn",
            backend=StorageBackend.MEMORY,
            enable_caching=True,
        ),
    )
    tx = storage.begin_transaction()
    assert (await storage.set("a", 1, transaction_id=tx)).success
    assert (await storage.set("b", 2, transaction_id=tx)).success
    assert (await storage.delete("a", transaction_id=tx)).success
    assert (await storage.commit_transaction(tx)).success

    # After commit, key a should be absent, b present
    assert (await storage.get("a")).data is None
    assert (await storage.get("b")).data == 2

    # Cache should serve subsequent fetch
    res_cached = await storage.get("b")
    assert res_cached.success
    assert res_cached.data == 2


@pytest.mark.asyncio
async def test_transaction_rollback_and_clear_cache_and_close() -> None:
    """Rollback clears changes; clear() empties cache; close() succeeds."""
    storage = FlextApiStorage(
        StorageConfig(
            namespace="rb",
            backend=StorageBackend.MEMORY,
            enable_caching=True,
        ),
    )
    tx = storage.begin_transaction()
    await storage.set("x", 99, transaction_id=tx)
    assert storage.rollback_transaction(tx).success
    assert (await storage.get("x")).data is None

    # Setting and then clearing
    await storage.set("y", 1)
    assert (await storage.clear()).success
    assert (await storage.keys()).data == []

    # Close should succeed when there are no active transactions
    assert (await storage.close()).success


@pytest.mark.asyncio
async def test_cache_ttl_expiration_via_time_monkeypatch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """TTL expiration is respected using a time monkeypatch."""
    storage = FlextApiStorage(
        StorageConfig(
            namespace="ttl",
            backend=StorageBackend.MEMORY,
            enable_caching=True,
            cache_ttl_seconds=10,
        ),
    )
    # Monkeypatch time to control expiry
    import time as _time  # noqa: PLC0415

    base = _time.time()
    monkeypatch.setattr("time.time", lambda: base)
    await storage.set("k", "v", ttl_seconds=5)
    assert (await storage.get("k")).data == "v"

    # Advance beyond TTL
    monkeypatch.setattr("time.time", lambda: base + 6)
    assert (await storage.get("k")).data is None
    assert (await storage.exists("k")).data is False
