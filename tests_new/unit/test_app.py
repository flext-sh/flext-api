"""Tests for flext_api.app module - REAL classes only.

Tests using only REAL classes:
- FlextApiApp
- create_flext_api_app

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_api import FlextApiApp, create_flext_api_app


class TestFlextApiApp:
    """Test FlextApiApp REAL class functionality."""

    def test_app_creation_direct(self) -> None:
        """Test direct FlextApiApp instantiation."""
        app = FlextApiApp()

        assert app.app_name == "FLEXT API"
        assert app.app_version == "0.9.0"

    def test_app_creation_factory(self) -> None:
        """Test create_flext_api_app factory function."""
        app = create_flext_api_app()

        # Should be a FastAPI instance wrapped in our app
        assert app is not None
        assert hasattr(app, "title")
        assert hasattr(app, "version")

    def test_app_health_endpoint(self) -> None:
        """Test that app has health endpoint available."""
        app = create_flext_api_app()

        # FastAPI app should have routes
        assert hasattr(app, "routes")
        assert len(app.routes) > 0

    def test_app_openapi_docs(self) -> None:
        """Test that app has OpenAPI documentation."""
        app = create_flext_api_app()

        # Should have OpenAPI schema
        assert hasattr(app, "openapi")

        # Should be callable
        openapi_schema = app.openapi()
        assert isinstance(openapi_schema, dict)
        assert "info" in openapi_schema
        assert "paths" in openapi_schema

    def test_app_middleware_support(self) -> None:
        """Test that app supports middleware."""
        app = create_flext_api_app()

        # Should have middleware stack
        assert hasattr(app, "middleware")
        assert hasattr(app, "add_middleware")

    def test_multiple_app_instances(self) -> None:
        """Test multiple app instances work independently."""
        app1 = create_flext_api_app()
        app2 = create_flext_api_app()

        # Both should be valid FastAPI instances
        assert app1 is not None
        assert app2 is not None

        # They should be separate instances
        assert app1 is not app2
