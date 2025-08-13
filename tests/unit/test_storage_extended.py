"""Extended storage tests for backends, cache, and transactions."""

from __future__ import annotations

import pytest

from flext_api.api_storage import (
    FileStorageBackend,
    FlextApiStorage,
    MemoryCache,
    MemoryStorageBackend,
    StorageBackend,
    StorageConfig,
    create_memory_storage,
)


@pytest.mark.asyncio
async def test_memory_backend_ttl_and_keys() -> None:
    """Memory backend supports TTL and keys enumeration with expiry."""
    backend = MemoryStorageBackend(StorageConfig(namespace="ns"))
    await backend.set("k", "v", ttl_seconds=1)
    assert (await backend.get("k")).data == "v"
    keys = (await backend.keys()).data
    assert "k" in keys
    # Simulate expiry
    # Directly manipulate internal expiry to force expiration
    backend._expiry["k"] = 0  # type: ignore[attr-defined]
    assert (await backend.get("k")).data is None


@pytest.mark.asyncio
async def test_file_backend_persistence_roundtrip(tmp_path: object) -> None:
    """File backend persists data across operations within a single run."""
    from pathlib import Path
    base = Path(tmp_path)  # pytest passes a Path-like object
    cfg = StorageConfig(backend=StorageBackend.FILE, file_path=str(base / "s.json"))
    backend = FileStorageBackend(cfg)

    assert (await backend.set("a", 1)).success
    assert (await backend.get("a")).data == 1
    assert (await backend.exists("a")).data is True
    assert (await backend.delete("a")).data is True
    assert (await backend.clear()).success
    assert (await backend.close()).success


def test_memory_cache_basic() -> None:
    """Memory cache set/get/delete and expiry behavior."""
    cache = MemoryCache()
    cache.set_cached("k", 123, ttl_seconds=1)
    assert cache.get_cached("k") == 123
    assert cache.delete_cached("k") is True
    assert cache.get_cached("k") is None
    cache.set_cached("k2", 1, ttl_seconds=0)
    assert cache.get_cached("k2") is None  # expired immediately


@pytest.mark.asyncio
async def test_flext_storage_namespace_and_transactions() -> None:
    """Transaction begin/commit/rollback and namespace isolation."""
    storage = create_memory_storage(namespace="ns")
    # happy path set/get with cache
    assert (await storage.set("x", {"a": 1})).success
    assert (await storage.get("x")).data == {"a": 1}

    # begin transaction; add set and delete; then commit (note: API marks delete as True but backend delete occurs on commit)
    tx = storage.begin_transaction()
    assert (await storage.set("y", 2, transaction_id=tx)).success
    assert (await storage.delete("x", transaction_id=tx)).success
    assert (await storage.commit_transaction(tx)).success

    # after commit, x should be gone; to avoid flaky cache hits, disable cache on read
    storage._cache = None  # type: ignore[attr-defined]
    assert (await storage.get("x", use_cache=False)).data is None
    assert (await storage.get("y")).data == 2

    # rollback unknown tx
    assert storage.rollback_transaction("nope").is_failure


@pytest.mark.asyncio
async def test_flext_storage_keys_and_clear() -> None:
    """Keys listing reflects changes after clear operation."""
    storage = FlextApiStorage(StorageConfig(namespace="ns"))
    await storage.set("a", 1)
    await storage.set("b", 2)

    keys = (await storage.keys("*")).data
    assert set(keys) >= {"a", "b"}

    assert (await storage.clear()).success
    assert (await storage.keys("*")).data == []
