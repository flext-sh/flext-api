"""Factory providers using simple factory functions for test object creation.

Uses factory functions for consistent, maintainable test data generation
following SOLID principles and flext-core patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations
from flext_core import FlextTypes

from .api_factories import (
    FlextFactory,
    FlextApiResponseFactory,
    FlextApiConfigFactory as ApiConfigFactory,
    create_flext_api_client_request,
    create_flext_api_client_response,
    create_flext_api_config,
)
from .app_factories import (
    FlextApiConfigFactory as AppConfigFactory,
    FastAPIApplicationFactory,
    create_flext_api_app_config,
    create_fastapi_application,
)
from .storage_factories import (
    create_file_storage_config,
    create_memory_storage_config,
)

# Legacy aliases for backwards compatibility
FileFactory = create_file_storage_config
MemoryFactory = create_memory_storage_config

# Export both aliases and add backward compatibility
FlextApiConfigFactory = ApiConfigFactory  # Default to API config factory

__all__ = [
    "FlextFactory",
    "FlextApiResponseFactory",
    "FlextApiConfigFactory",  # Backward compatibility
    "ApiConfigFactory",
    "AppConfigFactory",
    "FastAPIApplicationFactory",
    "FileFactory",
    "MemoryFactory",
    "create_flext_api_client_request",
    "create_flext_api_client_response",
    "create_flext_api_config",
    "create_flext_api_app_config",
    "create_fastapi_application",
    "create_file_storage_config",
    "create_memory_storage_config",
]
