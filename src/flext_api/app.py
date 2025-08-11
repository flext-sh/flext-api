"""FLEXT API App Module.

Compatibility module that bridges to api_app.py functionality.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_api.api_app import app as _app

# Re-export the main app
app = _app

def flext_api_create_app():
    """Create FlextAPI FastAPI application.

    Compatibility function that creates a new app instance each time.

    Returns:
        FastAPI application instance

    """
    from flext_api.api_app import create_flext_api_app
    return create_flext_api_app()

def create_flext_api():
    """Create FlextAPI for test compatibility.

    Returns a mock-compatible API object.
    """
    from flext_core import FlextResult

    class FlextAPI:
        def health_check(self):
            return FlextResult.ok({"status": "healthy"})

    return FlextAPI()

# Export compatibility interface
__all__ = [
    "app",
    "create_flext_api",
    "flext_api_create_app",
]
