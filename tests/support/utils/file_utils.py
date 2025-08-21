"""
File system testing utilities for flext-api.

Provides file creation and manipulation utilities for testing.
"""

from __future__ import annotations

import json
import stat
from pathlib import Path
from typing import Any


def create_temp_json_file(path: Path, data: dict[str, Any]) -> Path:
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
    try:
        path.chmod(stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)
    except (OSError, PermissionError, FileNotFoundError):
        pass