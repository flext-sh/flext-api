"""Tests for app module.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from fastapi import FastAPI

from flext_api.app import flext_api_create_app


class TestFlextApiApp:
    """Test cases for app creation."""

    def test_create_app(self) -> None:
        """Test creating FastAPI app."""
        app = flext_api_create_app()
        assert isinstance(app, FastAPI)
        if app.title != "FLEXT API":
            msg = f"Expected {'FLEXT API'}, got {app.title}"
            raise AssertionError(msg)
        expected_description = "Enterprise-grade distributed data integration platform"
        if app.description != expected_description:
            msg = f"Expected {expected_description}, got {app.description}"
            raise AssertionError(msg)
        assert app.version == "0.9.0"

    def test_app_routes(self) -> None:
        """Test that app has expected routes."""
        app = flext_api_create_app()

        # Check that routes are available
        route_paths = [getattr(route, "path", str(route)) for route in app.routes]
        if "/health" not in route_paths:
            msg = f"Expected {'/health'} in {route_paths}"
            raise AssertionError(msg)
