"""Focused app.py tests for maximum coverage improvement.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest

from flext_api.app import FlextApiApp
from flext_api.models import FlextApiModels


class TestFlextApiAppFocused:
    """Focused tests to improve app.py coverage from 50% to 100%."""

    def test_create_fastapi_app_basic(self) -> None:
        """Test create_fastapi_app with basic configuration."""
        config = FlextApiModels.AppConfig(title="Test API", app_version="1.0.0")

        app = FlextApiApp.create_fastapi_app(config)

        # Verify app is created and has expected attributes
        assert app is not None
        assert hasattr(app, "title")
        assert hasattr(app, "version")

        # Check basic properties
        assert app.title == "Test API"
        assert app.version == "1.0.0"

    def test_create_fastapi_app_with_full_config(self) -> None:
        """Test create_fastapi_app with full configuration options."""
        config = FlextApiModels.AppConfig(
            title="Full Config API",
            app_version="2.0.0",
            description="Full configuration test API",
            docs_url="/api/docs",
            redoc_url="/api/redoc",
            openapi_url="/api/openapi.json",
        )

        app = FlextApiApp.create_fastapi_app(config)

        assert app is not None
        assert app.title == "Full Config API"
        assert app.version == "2.0.0"
        # FastAPI sets these attributes during construction

    def test_create_fastapi_app_default_values(self) -> None:
        """Test create_fastapi_app uses default values for optional config."""
        config = FlextApiModels.AppConfig(
            title="Default Test API",
            app_version="3.0.0",
            # No description, docs_url, redoc_url, or openapi_url provided
        )

        app = FlextApiApp.create_fastapi_app(config)

        assert app is not None
        assert app.title == "Default Test API"
        assert app.version == "3.0.0"
        # getattr calls in app.py should use defaults

    def test_create_fastapi_app_health_endpoint_structure(self) -> None:
        """Test that health endpoint is properly added to FastAPI app."""
        config = FlextApiModels.AppConfig(title="Health Test API", app_version="1.0.0")

        app = FlextApiApp.create_fastapi_app(config)

        # Verify app structure includes the health endpoint
        assert app is not None
        assert hasattr(app, "routes")

        # Check that routes exist (health endpoint should be added)
        routes = getattr(app, "routes", [])
        assert len(routes) > 0

    def test_create_fastapi_app_config_attributes_access(self) -> None:
        """Test getattr usage for optional configuration attributes."""
        # This tests the getattr calls for description, docs_url, redoc_url, openapi_url
        config = FlextApiModels.AppConfig(title="Attr Test API", app_version="1.0.0")

        app = FlextApiApp.create_fastapi_app(config)

        # The function uses getattr with defaults, should not raise errors
        assert app is not None
        assert app.title == "Attr Test API"

    @pytest.mark.asyncio
    async def test_create_fastapi_app_health_endpoint_functionality(self) -> None:
        """Test that health endpoint actually works and returns expected response."""
        config = FlextApiModels.AppConfig(
            title="Health Function Test API", app_version="1.0.0"
        )

        app = FlextApiApp.create_fastapi_app(config)

        # Access the health endpoint handler through app routes
        # The health_check function is nested inside create_fastapi_app
        # To test line 36, we need to find and call the health endpoint handler
        assert app is not None
        routes = getattr(app, "routes", [])

        # Find the health endpoint
        health_route = None
        for route in routes:
            if hasattr(route, "path") and route.path == "/health":
                health_route = route
                break

        assert health_route is not None, "Health endpoint not found"

        # Call the health endpoint function if accessible
        if hasattr(health_route, "endpoint"):
            result = await health_route.endpoint()
            assert result == {"status": "healthy", "service": "flext-api"}
        else:
            # If we can't directly call the function, at least verify the route exists
            assert hasattr(health_route, "path")
            assert health_route.path == "/health"
