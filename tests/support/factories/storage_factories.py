"""
Factory Boy factories for storage configuration.

Uses factory_boy for consistent storage test data generation.
"""

from __future__ import annotations

import factory
from factory import Faker

from flext_api.storage import StorageConfig


class FileStorageConfigFactory(factory.Factory):
    """Factory for file storage configuration."""
    
    class Meta:
        model = StorageConfig
    
    file_path = Faker("file_path", depth=3, extension="json")


class MemoryStorageConfigFactory(factory.Factory):
    """Factory for memory storage configuration."""
    
    class Meta:
        model = StorageConfig
    
    file_path = None