"""Application layer for FLEXT API.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

This module contains the application services that orchestrate domain logic
and coordinate between the domain and infrastructure layers.

Uses flext-core patterns for clean architecture implementation.
"""

from __future__ import annotations

from flext_api.application.services.api_service import APIService
from flext_api.application.services.auth_service import AuthService
from flext_api.application.services.base import (
    AuthenticationService,
    BaseAPIService,
    DualRepositoryService,
    MonitoringService,
    PipelineBaseService,
    PluginBaseService,
    SingleRepositoryService,
)
from flext_api.application.services.pipeline_service import PipelineService
from flext_api.application.services.plugin_service import PluginService
from flext_api.application.services.system_service import SystemService

__all__ = [
    # Concrete services
    "APIService",
    "AuthService",
    "AuthenticationService",
    # Base classes
    "BaseAPIService",
    "DualRepositoryService",
    "MonitoringService",
    "PipelineBaseService",
    "PipelineService",
    "PluginBaseService",
    "PluginService",
    "SingleRepositoryService",
    "SystemService",
]
