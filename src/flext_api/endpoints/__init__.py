"""API endpoints for FLEXT API.

This module provides the API endpoint definitions for the FLEXT platform,
organized by functional areas for maintainability and scalability.
"""

from .auth import auth_router
from .pipelines import pipelines_router
from .plugins import plugins_router
from .system import system_router

__all__ = ["auth_router", "pipelines_router", "plugins_router", "system_router"]
