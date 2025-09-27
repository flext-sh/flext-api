"""FLEXT API - HTTP Foundation Library.

Streamlined HTTP client and API foundation for FLEXT ecosystem.
Direct usage of flext-core patterns without over-engineering.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import cast

from flext_api.app import FlextApiApp

# Main modules - consolidated following [Project]Constants pattern
from flext_api.client import FlextApiClient
from flext_api.config import FlextApiConfig
from flext_api.constants import FlextApiConstants
from flext_api.exceptions import FlextApiExceptions
from flext_api.models import FlextApiModels
from flext_api.storage import FlextApiStorage
from flext_api.utilities import FlextApiUtilities

__all__ = [
    "FlextApi",
    "FlextApiApp",
    "FlextApiClient",
    "FlextApiConfig",
    "FlextApiConstants",
    "FlextApiExceptions",
    "FlextApiModels",
    "FlextApiStorage",
    "FlextApiUtilities",
    "__version__",
]


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

    # Constants - consolidated from single-class modules
    HttpMethod = FlextApiConstants.HttpMethod
    ClientStatus = FlextApiConstants.ClientStatus
    RequestStatus = FlextApiConstants.RequestStatus
    ServiceStatus = FlextApiConstants.ServiceStatus
    ContentType = FlextApiConstants.ContentType
    StorageBackend = FlextApiConstants.StorageBackend
    AuthenticationType = FlextApiConstants.AuthenticationType
    CacheStrategy = FlextApiConstants.CacheStrategy
    LoggingConstants = FlextApiConstants.LoggingConstants

    # Domain-specific functionality shortcuts
    @classmethod
    def create_client(cls, base_url: str = "", **kwargs: object) -> FlextApiClient:
        """Create HTTP client with default configuration."""
        # Extract known parameters from kwargs with proper type casting
        timeout = (
            cast("int | None", kwargs.get("timeout"))
            if kwargs.get("timeout") is not None
            else None
        )
        max_retries = (
            cast("int | None", kwargs.get("max_retries"))
            if kwargs.get("max_retries") is not None
            else None
        )
        headers = (
            cast("Mapping[str, str] | None", kwargs.get("headers"))
            if kwargs.get("headers") is not None
            else None
        )
        verify_ssl = cast("bool", kwargs.get("verify_ssl", True))

        # Filter out known parameters from kwargs
        {
            k: v
            for k, v in kwargs.items()
            if k not in {"timeout", "max_retries", "headers", "verify_ssl"}
        }

        return cls.Client(
            config=None,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            headers=headers,
            verify_ssl=verify_ssl,
        )

    @classmethod
    def create_config(cls, **kwargs: object) -> FlextApiConfig:
        """Create API configuration using enhanced singleton pattern."""
        # Use enhanced singleton pattern from FlextConfig
        return cast(
            "FlextApiConfig",
            cls.Config.get_or_create_shared_instance(
                project_name="flext-api", **kwargs
            ),
        )

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
