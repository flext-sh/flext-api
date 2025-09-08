"""File system testing utilities for flext-api.

Provides file creation and manipulation utilities for testing.


Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import contextlib
import json
import stat
from pathlib import Path

from flext_core import FlextTypes


def create_temp_json_file(path: Path, data: FlextTypes.Core.Dict) -> Path:
    """Create temporary JSON file with data."""
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return path


def create_readonly_file(path: Path, content: str = "{}") -> Path:
    """Create read-only file for permission testing."""
    path.write_text(content, encoding="utf-8")
    path.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
    return path


def restore_file_permissions(path: Path) -> None:
    """Restore normal file permissions."""
    with contextlib.suppress(OSError, PermissionError, FileNotFoundError):
        path.chmod(stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)
