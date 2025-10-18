"""Generic HTTP API - Minimal facade for HTTP foundation.

Thin entry point providing access to generic HTTP modules.
Follows flext-core patterns with minimal complexity. Domain-agnostic.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_core import FlextResult, FlextService

import flext_api.client as client_module
from flext_api.app import FlextApiApp
from flext_api.client import FlextApiClient
from flext_api.config import FlextWebConfig
from flext_api.constants import FlextApiConstants
from flext_api.exceptions import FlextApiExceptions
from flext_api.models import FlextApiModels
from flext_api.protocols import HttpProtocols
from flext_api.typings import FlextApiTypes
from flext_api.utilities import FlextApiUtilities


class FlextWebApi(FlextService[FlextWebConfig]):
    """Minimal facade for generic HTTP foundation.

    Provides access to all generic HTTP modules without domain coupling.
    Follows railway-oriented error handling and single responsibility principle.
    """

    def __init__(self, config: FlextWebConfig | None = None) -> None:
        """Initialize with optional configuration."""
        super().__init__()
        self._config = config or FlextWebConfig()

    def execute(self) -> FlextResult[FlextWebConfig]:
        """Execute main operation (FlextService interface)."""
        return FlextResult[FlextWebConfig].ok(self._config)

    # Generic module access properties (type-safe)
    @property
    def client(self) -> type[FlextApiClient]:
        """Generic HTTP client functionality."""
        return client_module.FlextApiClient

    @property
    def app(self) -> type[FlextApiApp]:
        """FastAPI application factory."""
        return FlextApiApp

    @property
    def models(self) -> type[HttpModels]:
        """Generic HTTP data models."""
        return HttpModels

    @property
    def constants(self) -> type[FlextApiConstants]:
        """HTTP constants."""
        return FlextApiConstants

    @property
    def config_class(self) -> type[FlextWebConfig]:
        """Generic configuration class."""
        return FlextWebConfig

    @property
    def exceptions(self) -> type[FlextApiExceptions]:
        """HTTP exceptions."""
        return FlextApiExceptions

    @property
    def protocols(self) -> type[HttpProtocols]:
        """Generic protocol definitions."""
        return HttpProtocols

    @property
    def types(self) -> type[FlextApiTypes]:
        """Type definitions."""
        return FlextApiTypes

    @property
    def utilities(self) -> type[FlextApiUtilities]:
        """Utility functions."""
        return FlextApiUtilities
