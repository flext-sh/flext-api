"""Test more branches."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from flext_core import FlextResult

from flext_api import FileStorageBackend, StorageConfig

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.asyncio
async def test_file_backend_load_data_failure_and_close(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test file backend load data failure and close."""
    file_path = tmp_path / "store.json"
    # Write invalid json
    file_path.write_text("{not json}", encoding="utf-8")
    backend = FileStorageBackend(StorageConfig(file_path=str(file_path)))
    # Should have reset data to {}
    assert (await backend.keys()).success

    # Patch open to fail save
    async def fail_save() -> FlextResult[None]:
        return FlextResult.fail("io")

    monkeypatch.setattr(backend, "_save_data", fail_save)
    assert not (await backend.clear()).success
    # close path uses _save_data
    assert not (await backend.close()).success
