"""Error path tests for file storage backend save/delete operations."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

import pytest

from flext_api.api_storage import FileStorageBackend, StorageConfig


@pytest.mark.asyncio
async def test_file_backend_save_and_delete_error_paths(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    file_path = tmp_path / "store.json"
    backend = FileStorageBackend(StorageConfig(file_path=str(file_path)))

    # Monkeypatch _save_data to fail on set to hit error branch
    async def fail_save():
        from flext_core import FlextResult

        return FlextResult.fail("disk full")

    monkeypatch.setattr(backend, "_save_data", fail_save)
    assert not (await backend.set("a", 1)).success

    # Restore and write something
    monkeypatch.setattr(backend, "_save_data", FileStorageBackend._save_data)
    assert (await FileStorageBackend._save_data(backend)).success  # type: ignore[arg-type]
    assert (await backend.set("a", 1)).success

    # Monkeypatch _save_data to fail on delete
    async def fail_save2():
        from flext_core import FlextResult

        return FlextResult.fail("no space")

    monkeypatch.setattr(backend, "_save_data", fail_save2)
    res = await backend.delete("a")
    assert res.success is False
