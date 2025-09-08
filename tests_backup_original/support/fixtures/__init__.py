"""Unified fixture library for flext-api tests.

Provides reusable pytest fixtures following SOLID principles
and flext-core patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations
from flext_core import FlextTypes
from tests.support.fixtures.api_fixtures import (
    flext_api_client,
    flext_api_config,
    http_client_session,
)
from tests.support.fixtures.app_fixtures import (
    flext_api_app,
    test_client,
)
from tests.support.fixtures.storage_fixtures import (
    file_storage_backend,
    memory_storage_backend,
    temp_storage_path,
)

__all__ = [
    "flext_api_client",
    "flext_api_config",
    "http_client_session",
    "flext_api_app",
    "test_client",
    "file_storage_backend",
    "memory_storage_backend",
    "temp_storage_path",
]
