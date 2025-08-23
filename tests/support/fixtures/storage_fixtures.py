"""Storage backend fixtures for flext-api testing.

Provides reusable pytest fixtures for storage testing with temporary paths.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from pathlib import Path

import pytest

from flext_api.storage import FileStorageBackend, MemoryStorageBackend, StorageConfig


@pytest.fixture
def temp_storage_path(tmp_path: Path) -> Path:
    """Provide temporary path for file storage testing."""
    storage_file = tmp_path / "test_storage.json"
    return storage_file


@pytest.fixture
async def file_storage_backend(temp_storage_path: Path) -> AsyncGenerator[FileStorageBackend[object]]:
    """Provide configured file storage backend for testing."""
    config = StorageConfig(file_path=str(temp_storage_path))
    backend = FileStorageBackend[object](config)
    try:
        yield backend
    finally:
        await backend.close()


@pytest.fixture
async def memory_storage_backend() -> AsyncGenerator[MemoryStorageBackend[object]]:
    """Provide memory storage backend for testing."""
    config = StorageConfig()
    backend = MemoryStorageBackend[object](config)
    try:
        yield backend
    finally:
        await backend.close()
