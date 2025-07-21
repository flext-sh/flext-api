"""Application services for FLEXT API.

This module contains the application services that implement business logic
using flext-core patterns and dependency injection.
"""

# Try to import APIService - caught by try/except in main __init__.py
from __future__ import annotations

from contextlib import suppress

from flext_api.application.services.auth_service import AuthService
from flext_api.application.services.pipeline_service import PipelineService
from flext_api.application.services.plugin_service import PluginService
from flext_api.application.services.system_service import SystemService

with suppress(ImportError):
    from flext_api.application.services.api_service import APIService

__all__ = [
    "APIService",  # Will be added when implemented
    "AuthService",
    "PipelineService",
    "PluginService",
    "SystemService",
]
