"""Additional storage tests for file backend paths and utilities."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from flext_api import (
    FlextApiStorage,
    StorageBackend,
    StorageConfig,
)


@pytest.mark.asyncio
async def test_file_backend_persistence_and_clear(tmp_path: Path) -> None:
    """File backend should persist and clear namespace keys correctly."""
    file_path = tmp_path / "store.json"
    storage = create_file_storage(str(file_path), namespace="ns")
    await storage.set("k1", {"a": 1})
    await storage.set("k2", 2)
    assert (await storage.get("k1")).success

    # Under the hood file should exist and contain keys
    data = json.loads(file_path.read_text())
    assert any(k.startswith("ns:") for k in data)

    # Clear should delete namespace keys and persist
    await storage.clear()
    data2 = json.loads(file_path.read_text())
    assert not any(k.startswith("ns:") for k in data2)


@pytest.mark.asyncio
async def test_exists_and_keys_namespace() -> None:
    """Memory backend should support exists and namespaced keys."""
    storage = FlextApiStorage(
        StorageConfig(namespace="ns2", backend=StorageBackend.MEMORY),
    )
    await storage.set("zz", 1)
    assert (await storage.exists("zz")).value is True
    keys = await storage.keys()
    assert keys.success
    assert keys.value == ["zz"]
