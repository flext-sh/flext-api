"""Main entry point for FLEXT API application.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

This module provides the main FastAPI application instance for import compatibility.
The actual application logic is in app.py following clean architecture patterns.
"""

from __future__ import annotations

# Import the app creation function from app.py
from flext_api.app import flext_api_create_app

# Create the FastAPI app instance
app = flext_api_create_app()

# Create storage instance for compatibility
# (Remove this if storage module doesn't exist)
try:
    from flext_api.storage import FlextAPIStorage
    storage: FlextAPIStorage | None = FlextAPIStorage()
except ImportError:
    storage = None

# Export the app and storage for uvicorn and tests
__all__ = ["app", "storage"]

# Main execution entry point
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)  # noqa: S104
