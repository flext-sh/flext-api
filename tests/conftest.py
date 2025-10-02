"""Test configuration and fixtures for flext-api tests.

This module provides shared fixtures and configuration for all flext-api tests.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
import tempfile
import uuid
from collections.abc import Generator
from pathlib import Path

import pytest
from faker import Faker
from fastapi import FastAPI
from fastapi.testclient import TestClient

# DIRECT imports from flext_api - verified classes
from flext_api import (
    FlextApiClient,
    FlextApiConfig,
    FlextApiStorage,
)
from flext_api.typings import FlextApiTypes
from flext_core import FlextConstants, FlextContainer
from flext_tests import FlextTestsDomains

# Configure Faker for deterministic test data
fake = Faker()
Faker.seed(12345)

# Environment setup for testing
os.environ.update(
    {
        "FLEXT_API_TESTING": "true",
        "FLEXT_DISABLE_EXTERNAL_CALLS": "0",
        "ENVIRONMENT": "test",
        "LOG_LEVEL": "INFO",
    },
)


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest markers."""
    markers = [
        "unit: Fast isolated unit tests",
        "integration: Integration tests with external dependencies",
        "e2e: End-to-end workflow tests",
        "api: REST API endpoint tests",
        "client: HTTP client tests",
        "storage: Storage backend tests",
        "config: Configuration tests",
        "real_classes: Tests using only REAL classes",
        "slow: Slow running tests",
        "network: Tests requiring network access",
    ]

    for marker in markers:
        config.addinivalue_line("markers", marker)


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Modify test items during collection."""
    for item in items:
        # Add real_classes marker to all tests
        item.add_marker(pytest.mark.real_classes)

        # Add unit marker by default
        if not any(
            marker.name in {"integration", "e2e", "slow"}
            for marker in item.iter_markers()
        ):
            item.add_marker(pytest.mark.unit)


# ============================================================================
# FLEXT-API FIXTURES using flext_tests EM ABSOLUTO
# ============================================================================


@pytest.fixture
def flext_api_storage() -> FlextApiStorage:
    """Provide FlextApiStorage using flext_tests configuration.

    Returns:
        FlextApiStorage: Configured storage instance.

    """
    # Use FlextTestsDomains for configuration data
    config_data = FlextTestsDomains.create_configuration()
    config_data["namespace"] = "TestStorage"
    config_data["enable_caching"] = True

    return FlextApiStorage(config_data)


@pytest.fixture
def flext_api_client() -> FlextApiClient:
    """Provide FlextApiClient using flext_tests configuration.

    Returns:
        FlextApiClient: Configured client instance.

    """
    # Use FlextTestsDomains for realistic config values
    config_data = FlextTestsDomains.create_configuration()

    base_url_val = config_data.get(
        "base_url",
        f"http://{FlextConstants.Platform.DEFAULT_HOST}:{FlextConstants.Platform.FLEXT_API_PORT}",
    )
    timeout_val = config_data.get("timeout", FlextConstants.Network.DEFAULT_TIMEOUT)
    retries_val = config_data.get(
        "max_retries", FlextConstants.Reliability.MAX_RETRY_ATTEMPTS
    )

    base_url = (
        str(base_url_val)
        if base_url_val is not None
        else f"http://{FlextConstants.Platform.DEFAULT_HOST}:{FlextConstants.Platform.FLEXT_API_PORT}"
    )
    timeout = (
        int(timeout_val)
        if isinstance(timeout_val, (int, float, str))
        else FlextConstants.Network.DEFAULT_TIMEOUT
    )
    max_retries = (
        int(retries_val)
        if isinstance(retries_val, (int, str))
        else FlextConstants.Reliability.MAX_RETRY_ATTEMPTS
    )

    return FlextApiClient(
        base_url=base_url,
        timeout=timeout,
        max_retries=max_retries,
    )


@pytest.fixture
def flext_api_config() -> FlextApiConfig:
    """Provide FlextApiConfig using flext_tests configuration.

    Returns:
        FlextApiConfig: Configuration instance.

    """
    return FlextApiConfig()


@pytest.fixture
def clean_container() -> FlextContainer:
    """Provide clean FlextContainer instance for testing.

    Returns:
        FlextContainer: Clean container instance.

    """
    # Create a separate container instance for testing (not the global one)
    container = FlextContainer()
    container.clear()  # Clear any existing registrations
    return container


@pytest.fixture
def fastapi_app() -> FastAPI:
    """Provide FastAPI app using flext_tests service data.

    Returns:
        FastAPI: Configured FastAPI application.

    """
    service_data = FlextTestsDomains.create_service()

    return FastAPI(
        title=str(service_data.get("name", "FLEXT API Test")),
        version=str(service_data.get("version", "0.9.0")),
        description=str(service_data.get("description", "Test API")),
    )


@pytest.fixture
def test_client(fastapi_app: FastAPI) -> TestClient:
    """Provide FastAPI test client.

    Returns:
        TestClient: Configured test client.

    """
    return TestClient(fastapi_app)


# ============================================================================
# DATA FIXTURES using flext_tests EM ABSOLUTO
# ============================================================================


@pytest.fixture
def sample_api_data() -> FlextApiTypes.Core.ResponseDict:
    """Sample API data using FlextTestsDomains.

    Returns:
        FlextApiTypes.Core.ResponseDict: Sample API data.

    """
    return FlextTestsDomains.api_response_data()


@pytest.fixture
def sample_headers() -> FlextApiTypes.HttpHeaders:
    """Sample HTTP headers using flext_tests.

    Returns:
        FlextApiTypes.HttpHeaders: Sample HTTP headers.

    """
    service_data = FlextTestsDomains.create_service()
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": f"{service_data.get('name', 'FlextAPI')}-Test/{service_data.get('version', '0.9.0')}",
        "X-Request-ID": str(uuid.uuid4()),
    }


@pytest.fixture
def sample_config_dict() -> FlextApiTypes.Core.ResponseDict:
    """Sample config dictionary using FlextTestsDomains.

    Returns:
        FlextApiTypes.Core.ResponseDict: Sample configuration data.

    """
    return FlextTestsDomains.create_configuration()


@pytest.fixture
def sample_user_data() -> FlextApiTypes.Core.ResponseDict:
    """Sample user data using FlextTestsDomains.

    Returns:
        FlextApiTypes.Core.ResponseDict: Sample user data.

    """
    return FlextTestsDomains.create_user()


@pytest.fixture
def sample_service_data() -> FlextApiTypes.Core.ResponseDict:
    """Sample service data using FlextTestsDomains.

    Returns:
        FlextApiTypes.Core.ResponseDict: Sample service data.

    """
    return FlextTestsDomains.create_service()


@pytest.fixture
def sample_payload_data() -> FlextApiTypes.Core.ResponseDict:
    """Sample payload data using FlextTestsDomains.

    Returns:
        FlextApiTypes.Core.ResponseDict: Sample payload data.

    """
    return FlextTestsDomains.create_payload()


@pytest.fixture
def sample_configuration_data() -> FlextApiTypes.Core.ResponseDict:
    """Sample configuration data using FlextTestsDomains.

    Returns:
        FlextApiTypes.Core.ResponseDict: Sample configuration data.

    """
    return FlextTestsDomains.create_configuration()


# ============================================================================
# VALIDATION FIXTURES using flext_tests EM ABSOLUTO
# ============================================================================


@pytest.fixture
def valid_email_cases() -> list[str]:
    """Valid email cases from FlextTestsDomains.

    Returns:
        list[str]: List of valid email addresses.

    """
    return FlextTestsDomains.valid_email_cases()


@pytest.fixture
def invalid_email_cases() -> list[str]:
    """Invalid email cases from FlextTestsDomains.

    Returns:
        list[str]: List of invalid email addresses.

    """
    return FlextTestsDomains.invalid_email_cases()


@pytest.fixture
def valid_ages() -> list[int]:
    """Valid age cases from FlextTestsDomains.

    Returns:
        list[int]: List of valid ages.

    """
    return FlextTestsDomains.valid_ages()


@pytest.fixture
def invalid_ages() -> list[int]:
    """Invalid age cases from FlextTestsDomains.

    Returns:
        list[int]: List of invalid ages.

    """
    return FlextTestsDomains.invalid_ages()


# ============================================================================
# UTILITY FIXTURES using flext_tests EM ABSOLUTO
# ============================================================================


@pytest.fixture
def temp_dir() -> Generator[Path]:
    """Provide temporary directory for testing.

    Yields:
        Path: Temporary directory path.

    """
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def event_loop() -> Generator[AbstractEventLoop]:
    """Provide event loop for testing.

    Yields:
        AbstractEventLoop: Event loop for testing.

    """
    loop = new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# DIRECT ACCESS TO flext_tests - NO ALIASES
# ============================================================================

# Tests should import directly:
# from flext_tests import FlextTestsMatchers, FlextTestsDomains, FlextTestsUtilities
# FlextTestsMatchers.assert_result_success(result)
# FlextTestsDomains.create_user()
# FlextTestsUtilities.create_test_result(success=True, data=data)
