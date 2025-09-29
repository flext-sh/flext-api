"""Simple tests for flext-api client module.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_api.client import FlextApiClient
from flext_api.config import FlextApiConfig
from flext_api.constants import FlextApiConstants


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
            base_url="https://api.example.com",
            timeout=FlextApiConstants.DEFAULT_TIMEOUT,
            max_retries=FlextApiConstants.DEFAULT_RETRIES,
        )
        client = FlextApiClient(config=config)

        assert client is not None
        assert client.base_url == "https://api.example.com"
        assert client.timeout == FlextApiConstants.DEFAULT_TIMEOUT
        assert client.max_retries == FlextApiConstants.DEFAULT_RETRIES

    def test_client_initialization_with_dict_config(self) -> None:
        """Test client initialization with dictionary config."""
        config_dict = {
            "base_url": "https://api.example.com",
            "timeout": FlextApiConstants.DEFAULT_TIMEOUT,
            "max_retries": FlextApiConstants.DEFAULT_RETRIES,
        }
        client = FlextApiClient(**config_dict)

        assert client is not None
        assert client.base_url == "https://api.example.com"
        assert client.timeout == FlextApiConstants.DEFAULT_TIMEOUT
        assert client.max_retries == FlextApiConstants.DEFAULT_RETRIES
