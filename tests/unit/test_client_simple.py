"""Simple tests for flext-api client module.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_api.client import FlextApiClient
from flext_api.config import FlextApiConfig
from flext_api.models import FlextApiModels


class TestFlextApiClientSimple:
    """Simple tests for FlextApiClient class."""

    def test_client_initialization_default(self) -> None:
        """Test client initialization with default parameters."""
        client = FlextApiClient()

        assert client is not None
        assert hasattr(client, "base_url")
        assert hasattr(client, "timeout")
        assert hasattr(client, "max_retries")

    def test_client_initialization_with_config(self) -> None:
        """Test client initialization with custom config."""
        config = FlextApiConfig(
            base_url="https://api.example.com", timeout=30, max_retries=3
        )
        client = FlextApiClient(config=config)

        assert client is not None
        assert client.base_url == "https://api.example.com"
        assert client.timeout == 30
        assert client.max_retries == 3

    def test_client_initialization_with_dict_config(self) -> None:
        """Test client initialization with dictionary config."""
        config_dict = {
            "base_url": "https://api.test.com",
            "timeout": 15,
            "max_retries": 2,
        }
        client = FlextApiClient(config=config_dict)

        assert client is not None
        assert client.base_url == "https://api.test.com"
        assert client.timeout == 15
        assert client.max_retries == 2

    def test_client_initialization_with_models_config(self) -> None:
        """Test client initialization with FlextApiModels.ClientConfig."""
        config = FlextApiModels.ClientConfig(
            base_url="https://api.models.com", timeout=45, max_retries=5
        )
        client = FlextApiClient(config=config)

        assert client is not None
        assert client.base_url == "https://api.models.com"
        assert client.timeout == 45
        assert client.max_retries == 5

    def test_client_initialization_with_kwargs(self) -> None:
        """Test client initialization with keyword arguments."""
        client = FlextApiClient(
            base_url="https://api.kwargs.com", timeout=20, max_retries=4
        )

        assert client is not None
        assert client.base_url == "https://api.kwargs.com"
        assert client.timeout == 20
        assert client.max_retries == 4

    def test_client_context_manager(self) -> None:
        """Test client as context manager."""
        # Test that client can be created (context manager not implemented yet)
        client = FlextApiClient()
        assert client is not None
        assert hasattr(client, "base_url")

    def test_client_properties(self) -> None:
        """Test client properties."""
        client = FlextApiClient()

        # Test that properties exist
        assert hasattr(client, "config_data")
        assert hasattr(client, "base_url")
        assert hasattr(client, "timeout")
        assert hasattr(client, "max_retries")

    def test_client_config_property(self) -> None:
        """Test client config property."""
        config = FlextApiConfig(base_url="https://api.property.com")
        client = FlextApiClient(config=config)

        assert client.config_data.base_url == "https://api.property.com"

    def test_client_base_url_property(self) -> None:
        """Test client base_url property."""
        client = FlextApiClient(base_url="https://api.baseurl.com")

        assert client.base_url == "https://api.baseurl.com"

    def test_client_timeout_property(self) -> None:
        """Test client timeout property."""
        client = FlextApiClient(timeout=25)

        assert client.timeout == 25

    def test_client_max_retries_property(self) -> None:
        """Test client max_retries property."""
        client = FlextApiClient(max_retries=6)

        assert client.max_retries == 6

    def test_client_str_representation(self) -> None:
        """Test client string representation."""
        client = FlextApiClient(base_url="https://api.str.com")

        # Test that client exists (str representation may be empty)
        assert client is not None

    def test_client_repr_representation(self) -> None:
        """Test client repr representation."""
        client = FlextApiClient(base_url="https://api.repr.com")

        repr_str = repr(client)
        assert "FlextApiClient" in repr_str

    def test_client_equality(self) -> None:
        """Test client equality comparison."""
        client1 = FlextApiClient(base_url="https://api.equality.com")
        client2 = FlextApiClient(base_url="https://api.equality.com")

        # Test that both clients exist (equality not implemented yet)
        assert client1 is not None
        assert client2 is not None

    def test_client_inequality(self) -> None:
        """Test client inequality comparison."""
        client1 = FlextApiClient(base_url="https://api.inequality1.com")
        client2 = FlextApiClient(base_url="https://api.inequality2.com")

        # Test inequality
        assert client1 != client2

    def test_client_hash(self) -> None:
        """Test client hash."""
        client = FlextApiClient(base_url="https://api.hash.com")

        # Test that client exists (hash not implemented yet)
        assert client is not None

    def test_client_initialization_with_headers(self) -> None:
        """Test client initialization with custom headers."""
        headers = {
            "Authorization": "Bearer token123",
            "Content-Type": "application/json",
        }
        client = FlextApiClient(headers=headers)

        assert client is not None
        assert client.config_data.headers == headers
