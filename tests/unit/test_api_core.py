"""Test FLEXT API Core Components - Comprehensive testing with flext_tests integration.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import cast

import pytest
from pydantic import ValidationError

from flext_api import FlextApiClient
from flext_api.constants import FlextApiConstants
from flext_api.typings import FlextApiTypes
from flext_tests import FlextTestsDomains


class TestFlextApiClient:
    """Test FlextApiClient using flext_tests patterns and real functionality."""

    def test_client_class_exists(self) -> None:
        """Test FlextApiClient class exists and is importable."""
        assert FlextApiClient is not None
        assert hasattr(FlextApiClient, "__init__")
        assert hasattr(FlextApiClient, "base_url")
        assert hasattr(FlextApiClient, "timeout")
        assert hasattr(FlextApiClient, "max_retries")

    def test_create_flext_api_factory(self) -> None:
        """Test FlextApiClient constructor using flext_tests patterns."""
        api = FlextApiClient(base_url="https://api.example.com")

        # Verify constructor creates proper instance
        assert isinstance(api, FlextApiClient)
        assert api.base_url == "https://api.example.com"

    def test_client_creation_with_flext_tests_config(self) -> None:
        """Test client creation with FlextTestsDomains config - ACESSO DIRETO."""
        # Use FlextTestsDomains for realistic client configuration
        config_data = FlextTestsDomains.create_configuration()

        base_url = str(config_data.get("base_url", "https://httpbin.org"))
        timeout = cast(
            "int", config_data.get("timeout", FlextApiConstants.DEFAULT_TIMEOUT)
        )
        max_retries = cast(
            "int", config_data.get("max_retries", FlextApiConstants.DEFAULT_RETRIES)
        )

        client = FlextApiClient(
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
        )

        # Verify configuration using real values
        assert client.base_url == base_url
        assert client.timeout == timeout
        assert client.max_retries == max_retries

    def test_client_properties_with_factory_data(self) -> None:
        """Test client properties with test configuration data."""
        base_url = "https://api-service.example.com"
        timeout = FlextApiConstants.DEVELOPMENT_TIMEOUT
        max_retries = 5

        client = FlextApiClient(
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
        )

        assert isinstance(client.base_url, str)
        assert client.base_url == base_url
        assert isinstance(client.timeout, int)
        assert client.timeout == int(timeout)
        assert isinstance(client.max_retries, int)
        assert client.max_retries == max_retries

    def test_client_with_configuration_data(
        self,
        sample_configuration_data: FlextApiTypes.Core.ResponseDict,
    ) -> None:
        """Test client with configuration data from conftest fixture."""
        # Use configuration data from FlextTestsDomains via conftest
        base_url = str(sample_configuration_data.get("base_url", "https://httpbin.org"))
        timeout = cast(
            "int",
            sample_configuration_data.get("timeout", FlextApiConstants.DEFAULT_TIMEOUT),
        )
        max_retries = cast(
            "int",
            sample_configuration_data.get(
                "max_retries", FlextApiConstants.DEFAULT_RETRIES
            ),
        )

        client = FlextApiClient(
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
        )

        # Verify client uses configuration correctly
        assert client.base_url == base_url
        assert client.timeout == timeout
        assert client.max_retries == max_retries

    def test_client_initialization_variations(self) -> None:
        """Test various client initialization patterns using flext_tests data."""
        # Test with FlextTestsDomains data - ACESSO DIRETO
        config_scenarios = [
            FlextTestsDomains.create_configuration(),
            FlextTestsDomains.create_service(),
            {
                "base_url": "https://api.test.com",
                "timeout": FlextApiConstants.DEVELOPMENT_TIMEOUT,
                "max_retries": 2,
            },
        ]

        clients = []
        for config in config_scenarios:
            base_url = str(
                config.get("base_url", "https://default.example.com")
            ).replace("_", "-")
            client = FlextApiClient(base_url=base_url)
            clients.append(client)

        # All clients should be independent instances
        assert len(clients) == 3
        for i, client in enumerate(clients):
            for j, other_client in enumerate(clients):
                if i != j:
                    assert client is not other_client

    def test_multiple_clients_independence(self) -> None:
        """Test multiple client instances are independent using factory data."""
        # Create clients using FlextTestsDomains - ACESSO DIRETO
        service1 = FlextTestsDomains.create_service()
        service2 = FlextTestsDomains.create_service()

        client1 = FlextApiClient(
            base_url=f"https://{str(service1.get('name', 'service1')).replace('_', '-')}.example.com",
        )
        client2 = FlextApiClient(
            base_url=f"https://{str(service2.get('name', 'service2')).replace('_', '-')}.example.com",
        )

        # Clients should be independent
        assert client1 is not client2
        assert client1.base_url != client2.base_url

    def test_client_interface_methods(self) -> None:
        """Test client interface methods exist."""
        # Use FlextTestsDomains for configuration - ACESSO DIRETO
        config_data = FlextTestsDomains.create_configuration()
        base_url = str(config_data.get("base_url", "https://httpbin.org"))

        client = FlextApiClient(base_url=base_url)

        # Verify methods exist
        assert hasattr(client, "request")
        assert hasattr(client, "get")
        assert hasattr(client, "post")
        assert hasattr(client, "put")
        assert hasattr(client, "delete")

        # Verify they are callable
        assert callable(client.request)
        assert callable(client.get)
        assert callable(client.post)
        assert callable(client.put)
        assert callable(client.delete)

    def test_client_configuration_validation(self) -> None:
        """Test client validates configuration properly using flext_tests patterns."""
        # Use FlextTestsDomains for realistic test data - ACESSO DIRETO
        config_data = FlextTestsDomains.create_configuration()

        # Valid configuration should work
        valid_base_url = str(config_data.get("base_url", "https://api.example.com"))
        client = FlextApiClient(base_url=valid_base_url)
        assert client.base_url == valid_base_url

        # Empty base_url should raise validation error during initialization
        with pytest.raises(ValidationError) as exc_info:
            FlextApiClient(base_url="")

        # Should raise validation error for base_url
        error_message = str(exc_info.value).lower()
        assert "base_url" in error_message

    def test_client_property_types_validation(self) -> None:
        """Test client property types are properly validated."""
        base_url = "https://test-service.example.com"

        client = FlextApiClient(
            base_url=base_url, timeout=FlextApiConstants.DEFAULT_TIMEOUT, max_retries=5
        )

        assert isinstance(client.base_url, str)
        assert isinstance(client.timeout, (int, float))
        assert isinstance(client.max_retries, int)

    def test_client_with_service_data(
        self,
        sample_service_data: FlextApiTypes.Core.ResponseDict,
    ) -> None:
        """Test client with service data from conftest fixture."""
        # Build URL from service data
        service_name = str(sample_service_data.get("name", "testservice"))
        base_url = f"https://{service_name}.api.example.com"

        # Service names with underscores are invalid in URLs, so expect validation error
        with pytest.raises(ValidationError) as exc_info:
            FlextApiClient(base_url=base_url)

        # Should raise validation error for invalid URL
        error_message = str(exc_info.value).lower()
        assert "base_url" in error_message or "url" in error_message

    def test_client_advanced_features_exist(self) -> None:
        """Test client has advanced features using flext_tests patterns."""
        # Use FlextTestsDomains for configuration - ACESSO DIRETO
        config_data = FlextTestsDomains.create_configuration()
        base_url = str(config_data.get("base_url", "https://httpbin.org"))

        client = FlextApiClient(base_url=base_url)

        # Client should have these properties/attributes
        assert hasattr(client, "client_config")
        assert hasattr(client, "_connection_manager")
        # Check that essential HTTP methods exist
        assert hasattr(client, "get")
        assert hasattr(client, "post")
        assert hasattr(client, "put")
        assert hasattr(client, "delete")
        assert hasattr(client, "request")

        # Config should be accessible
        assert client.client_config is not None
        config_dict = client.client_config.get_configuration_dict()
        assert "base_url" in config_dict

        # Test connection manager functionality
        assert client._connection_manager is not None
        assert hasattr(client._connection_manager, "get_connection")
        assert hasattr(client._connection_manager, "is_connected")

    def test_client_factory_function_consistency(self) -> None:
        """Test FlextApiClient constructor creates consistent clients."""
        # Multiple calls should create independent instances
        client1 = FlextApiClient(base_url="https://api.example.com")
        client2 = FlextApiClient(base_url="https://api.example.com")

        # Should be different instances but same configuration
        assert client1 is not client2
        assert client1.base_url == client2.base_url
        assert client1.timeout == client2.timeout
        assert client1.max_retries == client2.max_retries

    def test_client_type_validation_with_flext_tests(self) -> None:
        """Test client is proper type using flext_tests validation."""
        # Create client using factory
        result = FlextApiClient.create_flext_api()
        assert result.is_success

        api_client = result.value["client"]

        assert isinstance(api_client, FlextApiClient)
        assert type(api_client).__name__ == "FlextApiClient"

        # Should be a class instance, not a type
        assert not isinstance(api_client, type)

    def test_client_attributes_persistence_with_factory_data(self) -> None:
        """Test client attributes persist after creation using factory data."""
        # Use FlextTestsDomains for test data - ACESSO DIRETO
        config_data = FlextTestsDomains.create_configuration()
        base_url = str(config_data.get("base_url", "https://persistent.example.com"))

        client = FlextApiClient(base_url=base_url)

        # Attributes should persist
        original_base_url = client.base_url
        original_timeout = client.timeout

        # After operations, attributes should still be there
        _ = str(client)  # String conversion
        _ = repr(client)  # Repr operation

        assert client.base_url == original_base_url
        assert client.timeout == original_timeout
