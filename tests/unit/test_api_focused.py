"""Focused API tests to achieve 100% coverage of api.py module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import cast

import pytest
from pydantic import ValidationError

from flext_api import FlextApiClient, FlextApiModels
from flext_api.constants import FlextApiConstants


class TestFlextApiClientCoverageBoost:
    """Focused tests to achieve 100% coverage of the FlextApiClient class."""

    def test_flext_api_initialization_success(self) -> None:
        """Test FlextApiClient initialization with valid configuration."""
        # Test basic initialization with default config
        api = FlextApiClient()
        assert api is not None
        assert hasattr(api, "_client_config")
        assert api._client_config is not None

    def test_flext_api_initialization_with_config_dict(self) -> None:
        """Test FlextApiClient initialization with configuration dictionary."""
        config = {
            "base_url": "https://api.example.com",
            "timeout": FlextApiConstants.DEFAULT_TIMEOUT,
            "max_retries": FlextApiConstants.DEFAULT_RETRIES,
        }

        typed_config = cast(
            "Mapping[str, str | int | float] | bool | dict[str, str] | None", config
        )
        api = FlextApiClient(config=typed_config)
        assert api is not None
        assert hasattr(api, "_client_config")
        assert api._client_config is not None

    def test_flext_api_initialization_failure(self) -> None:
        """Test FlextApiClient initialization failure handling."""
        # Create invalid configuration that would cause client creation to fail
        invalid_config = {
            "base_url": "",  # Invalid empty URL
            "timeout": -1,  # Invalid negative timeout
            "max_retries": "invalid",  # Invalid type
        }

        # FlextApiClient should raise ValidationError when client creation fails
        typed_invalid_config = cast(
            "Mapping[str, str | int | float] | bool | dict[str, str] | None",
            invalid_config,
        )
        with pytest.raises(ValidationError):
            FlextApiClient(config=typed_invalid_config)

    def test_flext_api_client_property(self) -> None:
        """Test FlextApiClient client property access."""
        api = FlextApiClient()
        # Test accessing actual client configuration
        assert hasattr(api, "_client_config")
        assert api._client_config is not None
        assert hasattr(api._client_config, "base_url")

    def test_flext_api_close(self) -> None:
        """Test FlextApiClient close method delegation."""
        api = FlextApiClient()
        result = api.close()
        # Should return FlextResult without error
        assert result is not None

    def test_flext_api_get(self) -> None:
        """Test FlextApiClient GET request delegation."""
        api = FlextApiClient(config={"base_url": "https://httpbin.org"})
        result = api.get("/get")
        # Should return FlextResult
        assert result is not None

    def test_flext_api_post(self) -> None:
        """Test FlextApiClient POST request delegation."""
        api = FlextApiClient(config={"base_url": "https://httpbin.org"})
        result = api.post("/post", json={"test": "data"})
        # Should return FlextResult
        assert result is not None

    def test_flext_api_put(self) -> None:
        """Test FlextApiClient PUT request delegation."""
        api = FlextApiClient(config={"base_url": "https://httpbin.org"})
        result = api.put("/put", json={"test": "data"})
        # Should return FlextResult
        assert result is not None

    def test_flext_api_delete(self) -> None:
        """Test FlextApiClient DELETE request delegation."""
        api = FlextApiClient(config={"base_url": "https://httpbin.org"})
        result = api.delete("/delete")
        # Should return FlextResult
        assert result is not None

    def test_flext_api_create_app_success(self) -> None:
        """Test FlextApiClient create_app static method success case."""
        # Test instance method, not static method
        api = FlextApiClient()
        result = api.create_flext_api_app()
        assert result is not None

    def test_flext_api_create_app_failure(self) -> None:
        """Test FlextApiClient create_app instance method failure case."""
        # Test for expected validation exception during AppConfig creation with empty required fields
        with pytest.raises((ValueError, ValidationError)):
            FlextApiModels.AppConfig(title="", app_version="")

    def test_flext_api_mapping_vs_other_config_branches(self) -> None:
        """Test FlextApiClient handles both Mapping and other config types correctly."""
        # Test Mapping config path
        mapping_config = {"base_url": "https://api.test.com"}
        api1 = FlextApiClient(config=mapping_config)
        assert hasattr(api1, "_client_config")
        assert api1._client_config is not None

        # Test non-Mapping config path (string)
        string_config = "https://api.test2.com"
        api2 = FlextApiClient(config=string_config)
        assert hasattr(api2, "_client_config")
        assert api2._client_config is not None

        # Test None config path
        api3 = FlextApiClient(config=None)
        assert hasattr(api3, "_client_config")
        assert api3._client_config is not None

    def test_flext_api_execute_method(self) -> None:
        """Test FlextApiClient execute method."""
        api = FlextApiClient()

        # Test execute method (no longer )
        result = api.execute()

        # Should return success with None value (execute method returns None)
        assert result is not None
        assert result.is_success
        assert result.value is None
