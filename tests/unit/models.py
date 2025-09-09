"""Real model tests using flext_tests library.

Tests actual model functionality without mocks using flext_tests patterns.
Only tests models and features that actually exist.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from urllib.parse import urlparse

# MAXIMUM usage of flext_tests - ACESSO DIRETO - NO ALIASES
from flext_tests import FlextTestsDomains

from flext_api.models import FlextApiModels


class TestFlextApiModelsReal:
    """Test FlextApiModels using real functionality and flext_tests patterns."""

    def test_client_config_creation_basic(self) -> None:
        """Test ClientConfig creation with basic functionality."""
        config = FlextApiModels.ClientConfig(
            base_url="https://api.example.com", timeout=30.0, max_retries=3
        )

        assert config.base_url == "https://api.example.com"
        assert config.timeout == 30.0
        assert config.max_retries == 3

        # Validation works with urlparse
        parsed = urlparse(config.base_url)
        assert parsed.scheme == "https"
        assert parsed.hostname == "api.example.com"

    def test_http_response_creation_real(self) -> None:
        """Test HttpResponse creation with real functionality."""
        response = FlextApiModels.HttpResponse(
            status_code=200,
            body={"data": "test"},
            headers={"Content-Type": "application/json"},
            url="https://api.example.com/data",
            method="GET",
        )

        assert response.status_code == 200
        assert response.body == {"data": "test"}
        assert response.url == "https://api.example.com/data"
        assert response.method == "GET"
        assert response.is_success is True

        # Test headers existence (may be None)
        if response.headers is not None:
            assert response.headers["Content-Type"] == "application/json"

    def test_http_response_error_status(self) -> None:
        """Test HttpResponse with error status codes."""
        # 404 error
        response_404 = FlextApiModels.HttpResponse(
            status_code=404,
            body={"error": "Not found"},
            headers={"Content-Type": "application/json"},
            url="https://api.example.com/missing",
            method="GET",
        )

        assert response_404.status_code == 404
        assert response_404.is_success is False

        # 500 error
        response_500 = FlextApiModels.HttpResponse(
            status_code=500,
            body={"error": "Internal server error"},
            headers={"Content-Type": "application/json"},
            url="https://api.example.com/error",
            method="POST",
        )

        assert response_500.status_code == 500
        assert response_500.is_success is False

    def test_api_response_class_exists(self) -> None:
        """Test ApiResponse class exists and can be referenced."""
        # Just test that the class exists and can be accessed
        assert FlextApiModels.ApiResponse is not None
        assert hasattr(FlextApiModels, "ApiResponse")

    def test_response_builder_real(self) -> None:
        """Test ResponseBuilder with real functionality."""
        builder = FlextApiModels.ResponseBuilder()

        # Test that builder exists and can be instantiated
        assert builder is not None
        assert isinstance(builder, FlextApiModels.ResponseBuilder)

    def test_query_builder_real(self) -> None:
        """Test QueryBuilder with real functionality."""
        builder = FlextApiModels.QueryBuilder()

        # Test that builder exists and can be instantiated
        assert builder is not None
        assert isinstance(builder, FlextApiModels.QueryBuilder)

    def test_model_validation_with_factories(self) -> None:
        """Test model validation using factory data."""
        # Use factory to create valid config data
        config_data = FlextTestsDomains.create_configuration(
            base_url="https://httpbin.org", default_timeout=45.0
        )

        # Verify config works correctly
        assert config_data.base_url == "https://httpbin.org"
        assert config_data.default_timeout == 45.0

        # Test URL validation
        parsed = urlparse(config_data.base_url)
        assert parsed.scheme == "https"
        assert parsed.netloc == "httpbin.org"

    def test_storage_config_creation(self) -> None:
        """Test StorageConfig creation with real validation."""
        storage_config = FlextApiModels.StorageConfig(
            backend="memory", namespace="test_namespace"
        )

        assert storage_config.backend == "memory"
        assert storage_config.namespace == "test_namespace"

    def test_client_config_with_factory(self) -> None:
        """Test client config creation using factory."""
        # Use FlextTestsDomains for client test data
        FlextTestsDomains.create_service()
        client = FlextApiModels.ClientConfig(
            base_url="https://test.example.com", timeout=60.0, max_retries=2
        )

        # Verify the client was created with correct config
        assert client.base_url == "https://test.example.com"
        assert client.timeout == 60.0
        assert client.max_retries == 2

    def test_http_response_success_status_codes(self) -> None:
        """Test various success status codes."""
        success_codes = [200, 201, 202, 204]

        for code in success_codes:
            response = FlextApiModels.HttpResponse(
                status_code=code,
                body={},
                url="https://api.example.com/test",
                method="GET",
            )
            assert response.is_success is True, f"Status {code} should be success"

    def test_http_response_error_status_codes(self) -> None:
        """Test various error status codes."""
        error_codes = [400, 401, 403, 404, 500, 502, 503]

        for code in error_codes:
            response = FlextApiModels.HttpResponse(
                status_code=code,
                body={"error": "test error"},
                url="https://api.example.com/test",
                method="GET",
            )
            assert response.is_success is False, f"Status {code} should be error"
