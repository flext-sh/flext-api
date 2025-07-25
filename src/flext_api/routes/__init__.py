"""API routes package for FLEXT API."""

from __future__ import annotations

from flext_api.endpoints.auth import auth_router

# Temporarily disabled due to missing models
# from flext_api.endpoints.pipelines import pipelines_router
# from flext_api.endpoints.plugins import plugins_router
from flext_api.endpoints.system import system_router

__all__ = ["auth_router", "system_router"]
