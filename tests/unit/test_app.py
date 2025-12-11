"""Comprehensive tests for FlextApiApp.

Tests validate FastAPI application creation using real FastAPI instances.
No mocks - uses actual FastAPI application creation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from fastapi import FastAPI

from flext_api.app import FlextApiApp
from flext_api.settings import FlextApiSettings


class TestFlextApiApp:
    """Test FastAPI application factory."""

    def test_create_default_app(self) -> None:
        """Test creating FastAPI app with default configuration."""
        config = FlextApiSettings(base_url="http://test.com")

        app = FlextApiApp.create(config)

        assert isinstance(app, FastAPI)
        assert app.title == "FlextAPI"
        assert app.version == "1.0.0"
        assert app.description == "FlextAPI Application"
        assert app.docs_url == "/docs"
        assert app.redoc_url == "/redoc"
        assert app.openapi_url == "/openapi.json"

    def test_create_custom_app(self) -> None:
        """Test creating FastAPI app with custom parameters."""
        config = FlextApiSettings(base_url="http://test.com")

        app = FlextApiApp.create(
            config,
            title="Custom API",
            version="2.0.0",
            description="Custom Description",
            docs_url="/api-docs",
            redoc_url="/api-redoc",
            openapi_url="/api-openapi.json",
        )

        assert isinstance(app, FastAPI)
        assert app.title == "Custom API"
        assert app.version == "2.0.0"
        assert app.description == "Custom Description"
        assert app.docs_url == "/api-docs"
        assert app.redoc_url == "/api-redoc"
        assert app.openapi_url == "/api-openapi.json"
