"""
Factory providers using factory_boy for dynamic test object creation.

Uses factory_boy for consistent, maintainable test data generation
following SOLID principles and flext-core patterns.
"""

from __future__ import annotations

from tests.support.factories.api_factories import (
    FlextApiClientRequestFactory,
    FlextApiClientResponseFactory,
    FlextApiConfigFactory,
)
from tests.support.factories.app_factories import (
    FlextApiAppConfigFactory,
    FastAPIApplicationFactory,
)
from tests.support.factories.storage_factories import (
    FileStorageConfigFactory,
    MemoryStorageConfigFactory,
)

__all__ = [
    "FlextApiClientRequestFactory",
    "FlextApiClientResponseFactory", 
    "FlextApiConfigFactory",
    "FlextApiAppConfigFactory",
    "FastAPIApplicationFactory",
    "FileStorageConfigFactory",
    "MemoryStorageConfigFactory",
]