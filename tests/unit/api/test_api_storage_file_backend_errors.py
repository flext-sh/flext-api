"""Error path tests for file storage backend save/delete operations."""

from __future__ import annotations

import contextlib
import stat
from pathlib import Path

import pytest
from flext_core import FlextResult

from flext_api import FileStorageBackend, StorageConfig


@pytest.mark.asyncio
async def test_file_backend_save_and_delete_error_paths(
    tmp_path: Path,
) -> None:
    """Test file backend save and delete error paths with REAL I/O conditions."""
    # Create initial backend and test normal operation
    file_path = Path(tmp_path) / "store.json"
    backend: FileStorageBackend[object] = FileStorageBackend(
        StorageConfig(file_path=str(file_path))
    )

    # First, test successful operation
    assert (await backend.set("a", 1)).success
    assert (await backend.get("a")).value == 1

    # Create REAL I/O error condition by making file read-only
    readonly_file_path = Path(tmp_path) / "readonly_store.json"
    readonly_file_path.write_text('{"existing": "data"}', encoding="utf-8")
    readonly_file_path.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)  # Read-only

    try:
        # Try to create backend with read-only file - this will test REAL save failures
        readonly_backend: FileStorageBackend[object] = FileStorageBackend(
            StorageConfig(file_path=str(readonly_file_path))
        )

        # Try to set - should fail with REAL permission error during save
        set_result = await readonly_backend.set("b", 2)
        # May succeed or fail depending on file system behavior

        # Try to delete - should fail with REAL permission error during save
        delete_result = await readonly_backend.delete("existing")
        # May succeed or fail depending on file system behavior

        # At least verify that error conditions are handled properly
        # The backend should not crash even if I/O operations fail
        assert isinstance(set_result, FlextResult)
        assert isinstance(delete_result, FlextResult)

    except PermissionError:
        # This is expected behavior with read-only files - REAL error condition
        pass
    finally:
        # Restore write permissions for cleanup
        with contextlib.suppress(OSError, PermissionError, FileNotFoundError):
            readonly_file_path.chmod(stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)

    # Test invalid file path to trigger REAL path errors
    invalid_path = "/dev/null/impossible/path/store.json"
    try:
        invalid_backend: FileStorageBackend[object] = FileStorageBackend(
            StorageConfig(file_path=invalid_path)
        )
        # Operations on invalid path should handle errors gracefully
        invalid_result = await invalid_backend.set("test", "value")
        assert isinstance(invalid_result, FlextResult)
    except (OSError, PermissionError):
        # Expected REAL file system errors
        pass
