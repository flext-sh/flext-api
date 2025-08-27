"""Storage backend fixtures for flext-api testing.

Provides reusable pytest fixtures for storage testing with temporary paths.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from pathlib import Path

import pytest

from flext_api.storage import FileStorageBackend, MemoryStorageBackend


@pytest.fixture
def temp_storage_path(tmp_path: Path) -> Path:
    """Provide temporary path for file storage testing."""
    return tmp_path / "test_storage.json"


@pytest.fixture
async def file_storage_backend(
    temp_storage_path: Path,
) -> AsyncGenerator[FileStorageBackend[object]]:
    """Provide configured file storage backend for testing."""
    # FileBackend aceita string como parâmetro, não Config
    backend = FileStorageBackend[object](str(temp_storage_path))
    try:
        yield backend
    finally:
        # Backends não têm método close(), remove a chamada
        pass


@pytest.fixture
async def memory_storage_backend() -> AsyncGenerator[MemoryStorageBackend[object]]:
    """Provide memory storage backend for testing."""
    # MemoryBackend não aceita parâmetros no __init__
    backend = MemoryStorageBackend[object]()
    try:
        yield backend
    finally:
        # Backends não têm método close(), remove a chamada
        pass
