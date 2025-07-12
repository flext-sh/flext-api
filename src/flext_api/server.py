"""FLEXT API Server entry point."""

from __future__ import annotations

import uvicorn

from flext_api.app import app
from flext_api.config import get_api_settings
from flext_observability.logging import get_logger

logger = get_logger(__name__)


def main() -> None:
    """Main function to start the FLEXT API server.

    Returns:
        None

    """
    settings = get_api_settings()

    logger.info(
        "Starting FLEXT API server",
        host=settings.host,
        port=settings.port,
        workers=settings.workers,
        version=settings.version,
    )

    if settings.reload:
        # Development mode with auto-reload
        uvicorn.run(
            "flext_api.app:app",
            **settings.uvicorn_kwargs,
        )
    else:
        # Production mode
        uvicorn.run(
            app,
            **settings.uvicorn_kwargs,
        )


if __name__ == "__main__":
    main()
