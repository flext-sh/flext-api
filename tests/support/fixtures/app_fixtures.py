"""FastAPI application fixtures for flext-api testing.

Provides reusable pytest fixtures for FastAPI apps and test clients.
"""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from flext_api import FlextApiConfig, create_flext_api_app
from tests.support.factories import FlextApiConfigFactory


@pytest.fixture
def flext_api_app_config() -> FlextApiConfig:
    """Provide test app configuration using factory."""
    return FlextApiConfigFactory()


@pytest.fixture
def flext_api_app(flext_api_app_config: FlextApiConfig) -> FastAPI:
    """Provide configured FLEXT API app for testing."""
    return create_flext_api_app(flext_api_app_config)


@pytest.fixture
def test_client(flext_api_app: FastAPI) -> TestClient:
    """Provide TestClient for synchronous API testing."""
    return TestClient(flext_api_app)


@pytest.fixture
async def async_test_client(flext_api_app: FastAPI) -> TestClient:
    """Provide async TestClient for asynchronous API testing."""
    # Note: TestClient handles async automatically
    return TestClient(flext_api_app)
