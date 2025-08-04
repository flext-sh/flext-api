"""FastAPI application entry point.

Main entry point that creates the FastAPI application instance and storage.
Imports the app from app.py and provides uvicorn server configuration for
development. The app instance is used by ASGI servers and testing frameworks.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_api.app import flext_api_create_app
from flext_api.storage import FlextAPIStorage

# Create the FastAPI app instance
app = flext_api_create_app()

# Create storage instance
storage = FlextAPIStorage()

# Export the app and storage for uvicorn and tests
__all__: list[str] = ["app", "storage"]

# Main execution entry point
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)  # noqa: S104
