"""FLEXT API App Module.

Compatibility module that bridges to api_app.py functionality.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from fastapi import FastAPI
from flext_core import FlextResult

from flext_api.api_app import app as _app

# Re-export the main app
app = _app


def flext_api_create_app() -> object:
    """Create a minimal FastAPI app for compatibility tests.

    This app exposes /health and uses `create_flext_api()` so tests can patch it
    and force specific behaviors (like returning None data).
    """
    compat_app = FastAPI(
        title="FLEXT API",
        version="0.9.0",
        description="Enterprise-grade distributed data integration platform",
    )

    @compat_app.get("/health")
    async def health() -> dict[str, object]:
        api = create_flext_api()
        # health_check in compat API returns a result object directly (sync)
        result = api.health_check()  # type: ignore[attr-defined]
        try:
            data = getattr(result, "data", None)
        except Exception:
            data = None
        return {} if data is None else data

    return compat_app


def create_flext_api() -> object:
    """Create FlextAPI for test compatibility.

    Returns a mock-compatible API object.
    """

    class FlextAPI:
        def health_check(self) -> object:
            return FlextResult.ok({"status": "healthy"})

    return FlextAPI()


# Export compatibility interface
__all__ = [
    "app",
    "create_flext_api",
    "flext_api_create_app",
]
