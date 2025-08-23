"""Factory providers using simple factory functions for test object creation.

Uses factory functions for consistent, maintainable test data generation
following SOLID principles and flext-core patterns.
"""

from __future__ import annotations

from tests.support.factories.api_factories import (
    FlextApiClientRequestFactory,
    FlextApiClientResponseFactory,
    FlextApiConfigFactory,
    create_flext_api_client_request,
    create_flext_api_client_response,
    create_flext_api_config,
)
from tests.support.factories.app_factories import (
    FlextApiAppConfigFactory,
    FastAPIApplicationFactory,
    create_flext_api_app_config,
    create_fastapi_application,
)
from tests.support.factories.storage_factories import (
    create_file_storage_config,
    create_memory_storage_config,
)

# Legacy aliases for backwards compatibility
FileStorageConfigFactory = create_file_storage_config
MemoryStorageConfigFactory = create_memory_storage_config

__all__ = [
    "FlextApiClientRequestFactory",
    "FlextApiClientResponseFactory",
    "FlextApiConfigFactory",
    "FlextApiAppConfigFactory",
    "FastAPIApplicationFactory",
    "FileStorageConfigFactory",
    "MemoryStorageConfigFactory",
    "create_flext_api_client_request",
    "create_flext_api_client_response",
    "create_flext_api_config",
    "create_flext_api_app_config",
    "create_fastapi_application",
    "create_file_storage_config",
    "create_memory_storage_config",
]
