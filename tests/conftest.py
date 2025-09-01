"""Pytest configuration for flext-api tests - REAL functionality only.

Focused on testing actual implementation, not mock objects or compatibility layers.
Uses only REAL classes from flext_api with proper FlextResult patterns.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import asyncio
import os
import tempfile
from pathlib import Path

import pytest
from faker import Faker
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Import REAL classes directly - no helpers, no aliases
from flext_api import (
    FlextApi,
    FlextApiApp,
    FlextApiClient,
    FlextApiConfig,
    FlextApiStorage,
    create_flext_api,
    create_flext_api_app,
)

# Configure Faker for deterministic test data
fake = Faker()
Faker.seed(12345)

# Environment setup for testing
os.environ.update({
    "FLEXT_API_TESTING": "true",
    "FLEXT_DISABLE_EXTERNAL_CALLS": "0",  # ENABLE external calls for real testing
    "ENVIRONMENT": "test",
    "LOG_LEVEL": "INFO",
})


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest with essential markers."""
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
        # Add real_classes marker to all tests (since we only use REAL classes)
        item.add_marker(pytest.mark.real_classes)

        # Add unit marker by default
        if not any(
            marker.name in {"integration", "e2e", "slow"}
            for marker in item.iter_markers()
        ):
            item.add_marker(pytest.mark.unit)


# ============================================================================
# CORE FIXTURES - REAL CLASSES ONLY
# ============================================================================


@pytest.fixture
def flext_api() -> FlextApi:
    """Provide real FlextApi instance for testing."""
    return create_flext_api()


@pytest.fixture
def flext_api_config() -> FlextApiConfig:
    """Provide real FlextApiConfig instance for testing."""
    return FlextApiConfig(
        host="127.0.0.1",
        port=8080,
        default_timeout=30.0,
        max_retries=3,
        base_url="https://httpbin.org",
    )


@pytest.fixture
def flext_api_client() -> FlextApiClient:
    """Provide real FlextApiClient instance for testing."""
    return FlextApiClient(base_url="https://httpbin.org", timeout=30.0, max_retries=3)


@pytest.fixture
def flext_api_app() -> FlextApiApp:
    """Provide real FlextApiApp instance for testing."""
    return create_flext_api_app()


@pytest.fixture
def flext_api_storage() -> FlextApiStorage:
    """Provide real FlextApiStorage instance for testing."""
    return FlextApiStorage(storage_name="TestStorage", max_size=100, default_ttl=300)


@pytest.fixture
def fastapi_app(flext_api_app: FlextApiApp) -> FastAPI:
    """Provide real FastAPI app for testing."""
    return flext_api_app.app


@pytest.fixture
def test_client(fastapi_app: FastAPI) -> TestClient:
    """Provide real FastAPI test client."""
    return TestClient(fastapi_app)


# ============================================================================
# DATA FIXTURES
# ============================================================================


@pytest.fixture
def sample_api_data() -> dict[str, object]:
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
def sample_config_dict() -> dict[str, object]:
    """Provide sample client config dictionary for testing."""
    return {"base_url": "https://api.example.com", "timeout": 45.0, "max_retries": 5}


# ============================================================================
# UTILITY FIXTURES
# ============================================================================


@pytest.fixture
def temp_dir() -> Path:
    """Provide temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def event_loop() -> asyncio.AbstractEventLoop:
    """Provide event loop for async testing."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# REAL FUNCTIONALITY HELPERS
# ============================================================================


def assert_flext_result_success(result: object) -> None:
    """Assert that a FlextResult is successful."""
    assert hasattr(result, "success"), "Result should have success attribute"
    assert result.success, (
        f"Result should be successful, got error: {getattr(result, 'error', None)}"
    )
    assert hasattr(result, "data"), "Result should have data attribute"


def assert_flext_result_failure(
    result: object, expected_error: str | None = None
) -> None:
    """Assert that a FlextResult is a failure."""
    assert hasattr(result, "success"), "Result should have success attribute"
    assert not result.success, "Result should not be successful"
    assert hasattr(result, "error"), "Result should have error attribute"
    assert result.error is not None, "Error should not be None for failed result"

    if expected_error:
        assert expected_error.lower() in str(result.error).lower(), (
            f"Expected '{expected_error}' in error message: {result.error}"
        )
