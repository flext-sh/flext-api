"""Tests to achieve 100% coverage for app.py."""

from __future__ import annotations

import inspect
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from flext_api.app import flext_api_create_app

# Constants
HTTP_OK = 200


class TestAppCoverageComplete:
    """Complete coverage tests for app.py."""

    def test_health_check_none_data_path(self) -> None:
        """Test health check endpoint when result.data is None (lines 26-27)."""
        # Create the app (will be mocked below)

        # Mock the health_check to return None data
        with patch("flext_api.app.create_flext_api") as mock_create_api:
            mock_api = MagicMock()
            mock_result = MagicMock()
            mock_result.data = None  # This will trigger the None path
            mock_api.health_check.return_value = mock_result
            mock_create_api.return_value = mock_api

            # Create app with mocked API
            test_app = flext_api_create_app()
            client = TestClient(test_app)

            # Make request to health check
            response = client.get("/health")

            # Should return empty dict when data is None
            if response.status_code != HTTP_OK:
                msg = f"Expected {200}, got {response.status_code}"
                raise AssertionError(msg)
            assert response.json() == {}

    def test_health_check_with_data_path(self) -> None:
        """Test health check endpoint when result.data has content."""
        app = flext_api_create_app()
        client = TestClient(app)

        # This should trigger the normal path where data is not None
        response = client.get("/health")

        if response.status_code != HTTP_OK:
            msg = f"Expected {200}, got {response.status_code}"
            raise AssertionError(msg)
        data = response.json()
        assert isinstance(data, dict)
        # Should have health check data from FlextApi

    def test_app_configuration(self) -> None:
        """Test that app is configured correctly."""
        app = flext_api_create_app()

        # Verify app configuration
        if app.title != "FLEXT API":
            msg = f"Expected {'FLEXT API'}, got {app.title}"
            raise AssertionError(msg)
        assert app.description == (
            "Enterprise-grade distributed data integration platform"
        )
        if app.version != "0.9.0":
            msg = f"Expected {'1.0.0'}, got {app.version}"
            raise AssertionError(msg)

    def test_app_has_health_endpoint(self) -> None:
        """Test that app has the health endpoint configured."""
        app = flext_api_create_app()

        # Check that health endpoint exists in routes
        routes = [route.path for route in app.routes]
        if "/health" not in routes:
            msg = f"Expected {'/health'} in {routes}"
            raise AssertionError(msg)

    def test_health_endpoint_async_function(self) -> None:
        """Test that health check endpoint is async."""
        app = flext_api_create_app()

        # Find the health check route
        health_route = None
        for route in app.routes:
            if hasattr(route, "path") and route.path == "/health":
                health_route = route
                break

        assert health_route is not None
        # Verify it's an async function
        if hasattr(health_route, "endpoint"):
            assert inspect.iscoroutinefunction(health_route.endpoint)

    @pytest.mark.asyncio
    async def test_health_check_function_directly(self) -> None:
        """Test the health check function directly to ensure coverage."""
        app = flext_api_create_app()

        # Find and call the health check function directly
        health_route = None
        for route in app.routes:
            if hasattr(route, "path") and route.path == "/health":
                health_route = route
                break

        if health_route and hasattr(health_route, "endpoint"):
            # Call the health check function directly
            result = await health_route.endpoint()
            assert isinstance(result, dict)

    def test_app_creation_multiple_times(self) -> None:
        """Test that app can be created multiple times."""
        app1 = flext_api_create_app()
        app2 = flext_api_create_app()

        # Should create separate instances
        assert app1 is not app2
        if app1.title == app2.title != "FLEXT API":
            msg = f"Expected {'FLEXT API'}, got {app1.title == app2.title}"
            raise AssertionError(msg)
