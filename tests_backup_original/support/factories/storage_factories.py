"""Storage-related test factories using simple factory functions.

Provides factory functions for storage configurations and backends.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path

from flext_core import FlextTypes


def create_file_storage_config(
    file_path: str | None = None,
    namespace: str = "test",
    *,
    enable_caching: bool = True,
) -> FlextTypes.Core.Dict:
    """Create file storage configuration for testing."""
    return {
        "backend": "file",
        "file_path": file_path or str(Path.cwd() / "test_storage.json"),
        "namespace": namespace,
        "enable_caching": enable_caching,
    }


def create_memory_storage_config(
    namespace: str = "test",
    *,
    enable_caching: bool = True,
    cache_ttl_seconds: int = 300,
) -> FlextTypes.Core.Dict:
    """Create memory storage configuration for testing."""
    return {
        "backend": "memory",
        "namespace": namespace,
        "enable_caching": enable_caching,
        "cache_ttl_seconds": cache_ttl_seconds,
    }
