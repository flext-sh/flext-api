"""FLEXT API - Enterprise FastAPI Gateway.

Copyright (c) 2025 FLEXT Team. All rights reserved.

Built on flext-core foundation for robust API gateway functionality.
Uses modern Python 3.13 patterns and clean architecture.
"""

from __future__ import annotations

__version__ = "0.1.0"

# Domain layer exports (when available)
try:
    from flext_api.domain.entities import APIRequest
    from flext_api.domain.entities import APIResponse
    from flext_api.domain.entities import Pipeline
    from flext_api.domain.entities import Plugin
    from flext_api.domain.repositories import PipelineRepository
    from flext_api.domain.repositories import PluginRepository
    from flext_api.domain.value_objects import PipelineId
    from flext_api.domain.value_objects import PluginId
    from flext_api.domain.value_objects import RequestId
except ImportError:
    # Domain layer not yet refactored
    pass

# Application layer exports (when available)
try:
    from flext_api.application.services import APIService
    from flext_api.application.services import PipelineService
    from flext_api.application.services import PluginService
except ImportError:
    # Application layer not yet refactored
    pass

# Configuration using flext-core patterns
try:
    from flext_api.config import APISettings
    from flext_api.config import get_api_settings
except ImportError:
    # Legacy config not available yet
    pass

# FastAPI app exports
try:
    from flext_api.main import app
    from flext_api.main import create_app
except ImportError:
    # Main app module has syntax errors, will be refactored
    pass

# Core exports that are always available
__all__ = [
    "APIRequest",
    "APIResponse",
    "APIService",
    # Configuration (when available)
    "APISettings",
    # Domain entities (when available)
    "Pipeline",
    # Value objects (when available)
    "PipelineId",
    # Repository interfaces (when available)
    "PipelineRepository",
    # Application services (when available)
    "PipelineService",
    "Plugin",
    "PluginId",
    "PluginRepository",
    "PluginService",
    "RequestId",
    # Version
    "__version__",
    # FastAPI app (when available)
    "app",
    "create_app",
    "get_api_settings",
]
