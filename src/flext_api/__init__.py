"""FLEXT API - HTTP Foundation Library.

Streamlined HTTP client and API foundation for FLEXT ecosystem.
Direct usage of flext-core patterns without over-engineering.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_api.client import FlextApiClient
from flext_api.config import FlextApiConfig
from flext_api.constants import FlextApiConstants
from flext_api.exceptions import FlextApiExceptions
from flext_api.models import FlextApiModels
from flext_api.storage import FlextApiStorage
from flext_api.utilities import FlextApiUtilities


class FlextApi:
    """Main API class - Single entry point for all flext-api functionality.

    Provides direct access to all flext-api components following FLEXT standards.
    No wrappers or aliases - direct access to the domain modules.
    """

    # Direct access to all domain modules
    Client = FlextApiClient
    Config = FlextApiConfig
    Constants = FlextApiConstants
    Exceptions = FlextApiExceptions
    Models = FlextApiModels
    Storage = FlextApiStorage
    Utilities = FlextApiUtilities

    # Domain-specific functionality shortcuts
    @classmethod
    def create_client(
        cls, base_url: str = "", **kwargs: object
    ) -> FlextApiClient:
        """Create HTTP client with default configuration."""
        return cls.Client(config=None, base_url=base_url, **kwargs)  # type: ignore[arg-type]

    @classmethod
    def create_config(cls, **kwargs: object) -> FlextApiConfig:
        """Create API configuration."""
        return cls.Config(**kwargs)  # type: ignore[arg-type]

    @classmethod
    def get_constants(cls) -> type[FlextApiConstants]:
        """Get API constants class."""
        return cls.Constants

    @classmethod
    def get_models(cls) -> type[FlextApiModels]:
        """Get API models class."""
        return cls.Models

    @classmethod
    def get_exceptions(cls) -> type[FlextApiExceptions]:
        """Get API exceptions class."""
        return cls.Exceptions


__version__ = "0.9.0"

__all__ = [
    "FlextApi",
    "FlextApiClient",
    "FlextApiConfig",
    "FlextApiConstants",
    "FlextApiExceptions",
    "FlextApiModels",
    "FlextApiStorage",
    "FlextApiUtilities",
    "__version__",
]
