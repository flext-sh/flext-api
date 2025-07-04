"""API endpoints for FLEXT API.

This module provides the API endpoint definitions for the FLEXT platform,
organized by functional areas for maintainability and scalability.
"""

from flext_api.endpoints.auth import auth_router
from flext_api.endpoints.pipelines import pipelines_router
from flext_api.endpoints.plugins import plugins_router
from flext_api.endpoints.system import system_router

__all__ = ["auth_router", "pipelines_router", "plugins_router", "system_router"]
