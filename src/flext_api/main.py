"""Main entry point for FLEXT API application.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

This module provides the main FastAPI application instance for import compatibility.
The actual application logic is in app.py following clean architecture patterns.
"""

from __future__ import annotations

# Import the configured FastAPI app from app.py
from flext_api.app import app
from flext_api.storage import FlextAPIStorage

# Create storage instance
storage = FlextAPIStorage()

# Export the app and storage for uvicorn and tests
__all__ = ["app", "storage"]

# Main execution entry point
if __name__ == "__main__":
    from flext_api.app import main

    main()
