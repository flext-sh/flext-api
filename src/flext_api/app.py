"""Main FastAPI application with complete integration."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from flext_api.routes import (
    auth_router,
    pipelines_router,
    plugins_router,
    system_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan management."""
    yield


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="FLEXT API",
        description="Enterprise API Gateway for FLEXT Platform",
        version="1.0.0",
        lifespan=lifespan,
    )

    # Add security middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "*.flext.com", "testserver"]
    )

    # Include all routers
    app.include_router(auth_router)
    app.include_router(pipelines_router)
    app.include_router(plugins_router)
    app.include_router(system_router)

    @app.get("/")
    async def root() -> dict[str, str]:
        """Root endpoint."""
        return {
            "message": "FLEXT API is running",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/system/health"
        }

    return app


# Create the app instance
app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "flext_api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
