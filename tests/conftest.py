"""Test configuration and fixtures for flext-api tests.

This module provides shared fixtures and configuration for all flext-api tests.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import os
import tempfile
import uuid
import warnings
from collections.abc import Generator
from pathlib import Path
from typing import cast

import pytest
from faker import Faker
from fastapi import FastAPI
from fastapi.testclient import TestClient
from flext_core import FlextConstants, FlextContainer
from flext_tests import FlextTestDocker, FlextTestsDomains

from flext_api import (
    FlextApiClient,
    FlextApiConfig,
    FlextApiStorage,
)

# Type aliases for testing - use expanded types directly
# Note: FlextApiTypes.ResponseDict and .WebHeaders are PEP 695 type aliases
# They don't exist at runtime, so we use the expanded types
ResponseDict = dict[str, object]  # Matches FlextApiTypes.ResponseDict
WebHeaders = dict[str, str | list[str]]  # Matches FlextApiTypes.WebHeaders

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
    """Provide FlextApiClient using FlextApiConfig.

    Returns:
        FlextApiClient: Configured client instance.

    """
    config_data = FlextTestsDomains.create_configuration()

    base_url = str(
        config_data.get(
            "base_url",
            f"http://{FlextConstants.Platform.DEFAULT_HOST}:{FlextConstants.Platform.FLEXT_API_PORT}",
        )
    )
    timeout_value = config_data.get("timeout", FlextConstants.Network.DEFAULT_TIMEOUT)
    timeout = float(
        timeout_value
        if isinstance(timeout_value, (int, float, str))
        else FlextConstants.Network.DEFAULT_TIMEOUT
    )

    max_retries_value = config_data.get(
        "max_retries", FlextConstants.Reliability.MAX_RETRY_ATTEMPTS
    )
    max_retries = int(
        max_retries_value
        if isinstance(max_retries_value, (int, float, str))
        else FlextConstants.Reliability.MAX_RETRY_ATTEMPTS
    )

    config = FlextApiConfig(
        base_url=base_url,
        timeout=timeout,
        max_retries=max_retries,
    )
    return FlextApiClient(config)


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
def sample_api_data() -> ResponseDict:
    """Sample API data using FlextTestsDomains.

    Returns:
        FlextApiTypes.ResponseDict: Sample API data.

    """
    return FlextTestsDomains.api_response_data()


@pytest.fixture
def sample_headers() -> WebHeaders:
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
def sample_config_dict() -> ResponseDict:
    """Sample config dictionary using FlextTestsDomains.

    Returns:
        FlextApiTypes.ResponseDict: Sample configuration data.

    """
    return FlextTestsDomains.create_configuration()


@pytest.fixture
def sample_user_data() -> ResponseDict:
    """Sample user data using FlextTestsDomains.

    Returns:
        FlextApiTypes.ResponseDict: Sample user data.

    """
    return cast("ResponseDict", FlextTestsDomains.create_user())


@pytest.fixture
def sample_service_data() -> ResponseDict:
    """Sample service data using FlextTestsDomains.

    Returns:
        FlextApiTypes.ResponseDict: Sample service data.

    """
    return FlextTestsDomains.create_service()


@pytest.fixture
def sample_payload_data() -> dict[str, object]:
    """Sample payload data using FlextTestsDomains.

    Returns:
        FlextApiTypes.ResponseDict: Sample payload data.

    """
    return FlextTestsDomains.create_payload()


@pytest.fixture
def sample_configuration_data() -> dict[str, object]:
    """Sample configuration data using FlextTestsDomains.

    Returns:
        FlextApiTypes.ResponseDict: Sample configuration data.

    """
    return FlextTestsDomains.create_configuration()


# ============================================================================
# VALIDATION FIXTURES using flext_tests EM ABSOLUTO
# ============================================================================


@pytest.fixture
def valid_email_cases() -> list[tuple[str, bool]]:
    """Valid email cases from FlextTestsDomains.

    Returns:
        list[tuple[str, bool]]: List of (email, is_valid) tuples.

    """
    return FlextTestsDomains.valid_email_cases()


# Removed invalid_email_cases fixture as the method doesn't exist in FlextTestsDomains


# Removed age fixtures as the methods don't exist in FlextTestsDomains


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


# Async event loop fixture removed - synchronous implementation only


# ============================================================================
# DIRECT ACCESS TO flext_tests - NO ALIASES
# ============================================================================

# Tests should import directly:
# from flext_tests import FlextTestsMatchers, FlextTestsDomains, FlextTestsUtilities
# FlextTestsMatchers.assert_result_success(result)
# FlextTestsDomains.create_user()
# FlextTestsUtilities.create_test_result(success=True, data=data)


# ============================================================================
# DOCKER TEST FIXTURES - FlextTestDocker integration
# ============================================================================


@pytest.fixture(scope="session")
def docker_manager() -> Generator[FlextTestDocker]:
    """Provide FlextTestDocker instance for containerized testing.

    This fixture provides access to FlextTestDocker for managing test containers.
    Containers are automatically cleaned up after test session.

    Yields:
        FlextTestDocker: Configured docker manager instance

    Note:
        Uses session scope to avoid recreating containers for each test.
        Containers remain running between tests but are cleaned up at session end.

    """
    manager = FlextTestDocker()

    # Register pytest fixtures that wrap FlextTestDocker operations
    # This provides backward compatibility and easier testing
    try:
        yield manager
    finally:
        # Cleanup: stop all test containers at session end
        try:
            cleanup_result = manager.cleanup_all_test_containers()
            if not cleanup_result.is_success:
                warnings.warn(
                    f"Docker cleanup failed: {cleanup_result.error}",
                    UserWarning,
                    stacklevel=2,
                )
        except Exception as e:
            warnings.warn(f"Docker cleanup error: {e}", UserWarning, stacklevel=2)


@pytest.fixture
def httpbin_container(docker_manager: FlextTestDocker) -> Generator[str]:
    """Provide httpbin test container for HTTP testing.

    Starts httpbin container if not already running, yields container name.
    Container remains running for the test but is not stopped afterward.

    Args:
        docker_manager: FlextTestDocker instance

    Yields:
        str: Container name for use in tests

    Note:
        Container persists between tests for performance but is cleaned up
        at session end by docker_manager fixture.

    """
    container_name = "flext-api-httpbin-test"

    # Start httpbin container
    start_result = docker_manager.start_container(
        name=container_name,
        image="kennethreitz/httpbin:latest",
        ports={"80/tcp": 8080},  # Map container port 80 to host port 8080
    )

    if start_result.is_failure:
        pytest.skip(f"Could not start httpbin container: {start_result.error}")

    try:
        yield container_name
    finally:
        # Container remains running for other tests
        # Will be cleaned up by session-scoped docker_manager fixture
        pass
