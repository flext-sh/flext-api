"""Pytest configuration for flext-api tests - REAL classes only.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest

# Import REAL classes for test fixtures
from flext_api import FlextApi, FlextApiClient, FlextApiConfig, FlextApiStorage


@pytest.fixture
def flext_api() -> FlextApi:
    """Provide FlextApi instance for testing."""
    return FlextApi()


@pytest.fixture
def flext_api_config() -> FlextApiConfig:
    """Provide FlextApiConfig instance for testing."""
    return FlextApiConfig(
        host="127.0.0.1",
        port=8080,
        default_timeout=30.0,
        max_retries=3,
        base_url="https://httpbin.org",
    )


@pytest.fixture
def flext_api_client() -> FlextApiClient:
    """Provide FlextApiClient instance for testing."""
    return FlextApiClient(base_url="https://httpbin.org", timeout=30.0, max_retries=3)


@pytest.fixture
def flext_api_storage() -> FlextApiStorage:
    """Provide FlextApiStorage instance for testing."""
    return FlextApiStorage(storage_name="TestStorage", max_size=100, default_ttl=300)


@pytest.fixture
def sample_api_data() -> dict[str, str | int]:
    """Provide sample API data for testing."""
    return {
        "id": 123,
        "name": "Test User",
        "email": "test@example.com",
        "status": "active",
    }


@pytest.fixture
def sample_headers() -> dict[str, str]:
    """Provide sample HTTP headers for testing."""
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "FlextAPI-Test/0.9.0",
    }


@pytest.fixture
def sample_config_dict() -> dict[str, str | int | float]:
    """Provide sample client config dictionary for testing."""
    return {"base_url": "https://api.example.com", "timeout": 45.0, "max_retries": 5}


# Test markers for organizing test execution
def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: mark test as unit test")
    config.addinivalue_line(
        "markers", "real_classes: mark test as using only REAL classes"
    )
    config.addinivalue_line("markers", "api: mark test as API-related")
    config.addinivalue_line("markers", "client: mark test as client-related")
    config.addinivalue_line("markers", "storage: mark test as storage-related")
    config.addinivalue_line("markers", "models: mark test as models-related")
    config.addinivalue_line("markers", "config: mark test as config-related")


# Pytest collection configuration
def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Modify test items during collection."""
    for item in items:
        # Add 'unit' marker to all tests in this directory
        if "tests_new/unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)

        # Add 'real_classes' marker to all tests (since all use REAL classes)
        item.add_marker(pytest.mark.real_classes)

        # Add module-specific markers based on test file name
        if "test_api.py" in str(item.fspath):
            item.add_marker(pytest.mark.api)
        elif "test_client.py" in str(item.fspath):
            item.add_marker(pytest.mark.client)
        elif "test_storage.py" in str(item.fspath):
            item.add_marker(pytest.mark.storage)
        elif "test_models.py" in str(item.fspath):
            item.add_marker(pytest.mark.models)
        elif "test_config.py" in str(item.fspath):
            item.add_marker(pytest.mark.config)
