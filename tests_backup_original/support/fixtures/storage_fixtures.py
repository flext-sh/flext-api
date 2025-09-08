"""Storage backend fixtures for flext-api testing.

Provides reusable pytest fixtures for storage testing with temporary paths.


Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from pathlib import Path

import pytest
from flext_core import FlextTypes


# Mock storage backends for testing
class File:
    """Mock file storage backend for testing."""

    def __init__(self, path: str = "./storage") -> None:
        self.base_path = Path(path)
        self.base_path.mkdir(exist_ok=True)

    def execute(self) -> str:
        """Mock execute method."""
        return "file_executed"


class Memory:
    """Mock memory storage backend for testing."""

    def __init__(self) -> None:
        self.data: FlextTypes.Core.Dict = {}

    def execute(self) -> str:
        """Mock execute method."""
        return "memory_executed"


@pytest.fixture
def temp_storage_path(tmp_path: Path) -> Path:
    """Provide temporary path for file storage testing."""
    return tmp_path / "test_storage.json"


@pytest.fixture
async def file_storage_backend(
    temp_storage_path: Path,
) -> AsyncGenerator[File]:
    """Provide configured file storage backend for testing."""
    # FileBackend aceita string como parâmetro, não Config
    backend = File(str(temp_storage_path))
    try:
        yield backend
    finally:
        # Backends não têm método close(), remove a chamada
        pass


@pytest.fixture
async def memory_storage_backend() -> AsyncGenerator[Memory]:
    """Provide memory storage backend for testing."""
    # MemoryBackend não aceita parâmetros no __init__
    backend = Memory()
    try:
        yield backend
    finally:
        # Backends não têm método close(), remove a chamada
        pass
