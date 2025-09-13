"""FLEXT API - Enumeration definitions.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from enum import StrEnum

from flext_core import FlextTypes


class StorageBackend(StrEnum):
    """Storage backend types for flext-api."""

    MEMORY = "memory"
    FILE = "file"
    REDIS = "redis"
    DATABASE = "database"


__all__: FlextTypes.Core.StringList = [
    "StorageBackend",
]
