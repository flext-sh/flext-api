"""Tests to achieve 100% coverage for main.py with REAL execution - NO MOCKS.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import time

import uvicorn
from fastapi.testclient import TestClient

from flext_api import (
    FlextApiAppConfig,
    FlextApiSettings,
    app,
    create_flext_api_app,
    main as main_module,
    storage,
)


class TestMainCoverageComplete:
    """Complete coverage tests for main.py."""

    def test_storage_functionality(self) -> None:
        """Test storage functionality in main.py."""
        # Test that storage is properly imported and instantiated
        assert storage is not None
        assert hasattr(storage, "get")
        assert hasattr(storage, "set")
        assert hasattr(storage, "delete")

        # Test basic storage operations
        storage.set("test_key", "test_value")
        assert storage.get("test_key") == "test_value"
        assert storage.delete("test_key") is True
        assert storage.get("test_key") is None

    def test_real_app_server_functionality(self) -> None:
        """Test REAL app server functionality without mocks."""
        # Test with REAL TestClient to validate app works
        with TestClient(app) as client:
            # Make real HTTP request to root endpoint
            response = client.get("/")
            # Should get some response (may be 404, 200, etc. but not server error)
            assert response.status_code in {200, 404, 422}  # Valid HTTP responses

            # Test health endpoint if it exists
            health_response = client.get("/health")
            # Should be accessible or return proper HTTP status
            assert health_response.status_code in {200, 404, 422}

    def test_real_server_configuration(self) -> None:
        """Test REAL server configuration with actual uvicorn config."""
        # Test that we can create a REAL uvicorn config
        config = uvicorn.Config(
            app=app,
            host="127.0.0.1",
            port=8001,  # Use different port to avoid conflicts
            log_level="debug",
            access_log=False,  # Disable access log for test
        )

        # Verify config is properly created with our app
        assert config.app is app
        assert config.host == "127.0.0.1"
        assert config.port == 8001
        assert config.log_level == "debug"

    def test_main_module_structure(self) -> None:
        """Test main module has correct structure."""
        # Verify main module exports
        assert hasattr(main_module, "app")
        assert hasattr(main_module, "storage")
        assert hasattr(main_module, "__all__")

        # Verify __all__ contains expected exports
        if "app" not in main_module.__all__:
            msg: str = f"Expected {'app'} in {main_module.__all__}"
            raise AssertionError(msg)
        assert "storage" in main_module.__all__

    def test_app_instance_valid(self) -> None:
        """Test that app instance is valid FastAPI app."""
        assert app is not None
        # Check if it has FastAPI-like attributes
        assert hasattr(app, "title")
        assert hasattr(app, "version") or hasattr(app, "description")

    def test_storage_instance_valid(self) -> None:
        """Test that storage instance is valid and functional with REAL operations."""
        # Storage should be a functional wrapper with required methods
        assert storage is not None
        assert hasattr(storage, "get")
        assert hasattr(storage, "set")
        assert hasattr(storage, "delete")

        # Test REAL storage operations with unique keys
        test_key = f"test_valid_{int(time.time() * 1000)}"  # Unique key
        test_value = "real_storage_test_value"

        # REAL set operation
        storage.set(test_key, test_value)

        # REAL get operation
        retrieved_value = storage.get(test_key)
        assert retrieved_value == test_value

        # REAL delete operation
        delete_result = storage.delete(test_key)
        assert delete_result is True

        # Verify deletion worked
        deleted_value = storage.get(test_key)
        assert deleted_value is None

    def test_real_app_creation_and_validation(self) -> None:
        """Test REAL app creation and validation functionality."""
        # Create REAL app with test settings
        test_settings = FlextApiSettings(
            environment="test",
            debug=True,
            log_level="INFO",
            api_host="localhost",
            api_port=8002,
        )

        # Create REAL app config and app
        app_config = FlextApiAppConfig(test_settings)
        real_app = create_flext_api_app(app_config)

        # Validate REAL app properties
        assert real_app is not None
        assert hasattr(real_app, "title")
        assert hasattr(real_app, "version") or hasattr(real_app, "description")

        # Test with REAL client
        with TestClient(real_app) as client:
            response = client.get("/")
            # Should get valid HTTP response from real app
            assert response.status_code in {200, 404, 422}
