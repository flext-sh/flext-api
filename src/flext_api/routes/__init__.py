"""API routes package for FLEXT API."""

from .auth import router as auth_router
from .pipelines import router as pipelines_router
from .plugins import router as plugins_router
from .system import router as system_router

__all__ = [
    "auth_router",
    "pipelines_router",
    "plugins_router",
    "system_router",
]
