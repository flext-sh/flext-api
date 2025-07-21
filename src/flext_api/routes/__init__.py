"""API routes package for FLEXT API."""

from __future__ import annotations

from flext_api.routes.auth import router as auth_router
from flext_api.routes.pipelines import pipelines_router
from flext_api.routes.plugins import router as plugins_router
from flext_api.routes.system import router as system_router

__all__ = [
    "auth_router",
    "pipelines_router",
    "plugins_router",
    "system_router",
]
