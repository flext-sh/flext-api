"""Pytest configuration for flext-api tests.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os

# Test environment setup - local implementation
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from flext_api.main import app, storage

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

# Setup test environment
os.environ["FLEXT_API_TESTING"] = "true"


# Project root fixture
@pytest.fixture
def project_root() -> Path:
    """Get project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def set_test_environment() -> None:
    """Set test environment variables."""
    os.environ["ENVIRONMENT"] = "test"
    os.environ["LOG_LEVEL"] = "DEBUG"


@pytest.fixture
def sample_api_config() -> dict[str, object]:
    """Sample API configuration for testing."""
    return {
        "environment": "test",
        "debug": True,
        "log_level": "DEBUG",
        "database_url": "sqlite:///:memory:",
        "redis_url": "redis://localhost:6379/1",
    }


@pytest.fixture
def sample_pipeline_data() -> dict[str, object]:
    """Sample pipeline data for testing."""
    return {
        "name": "test-pipeline",
        "description": "A test pipeline for unit tests",
        "extractor": "tap-postgres",
        "loader": "target-snowflake",
        "config": {
            "source": {"host": "localhost", "port": 5432},
            "destination": {"account": "test-account"},
        },
    }


@pytest.fixture
def sample_plugin_data() -> dict[str, object]:
    """Sample plugin data for testing."""
    return {
        "name": "tap-postgres",
        "type": "extractor",
        "version": "1.0.0",
        "config": {
            "host": "localhost",
            "port": 5432,
            "database": "test_db",
        },
    }


@pytest.fixture
def sample_user_data() -> dict[str, object]:
    """Sample user data for testing."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "securepassword123",
        "role": "user",
    }


@pytest.fixture
def mock_auth_service() -> AsyncMock:
    """Mock authentication service."""
    mock_service = AsyncMock()
    mock_service.login.return_value.successful = True
    mock_service.login.return_value.data = {
        "access_token": "test-token",
        "token_type": "bearer",
        "expires_in": 3600,
    }
    return mock_service


@pytest.fixture
def mock_pipeline_repository() -> AsyncMock:
    """Mock pipeline repository."""
    mock_repo = AsyncMock()
    mock_repo.create_pipeline.return_value.successful = True
    mock_repo.create_pipeline.return_value.data = {
        "pipeline_id": "test-pipeline-id",
        "status": "created",
    }
    return mock_repo


@pytest.fixture
def mock_plugin_service() -> AsyncMock:
    """Mock plugin service."""
    mock_service = AsyncMock()
    mock_service.install_plugin.return_value.successful = True
    mock_service.install_plugin.return_value.data = {
        "plugin_name": "tap-postgres",
        "status": "installed",
    }
    return mock_service


@pytest.fixture
async def api_client() -> AsyncGenerator[TestClient]:
    """FastAPI test client with mocked database."""
    # Mock database dependencies to avoid psycopg2 requirement
    with (
        patch("flext_api.dependencies.create_async_engine") as mock_engine,
        patch("flext_api.dependencies.async_session_factory") as mock_session,
        patch("flext_api.dependencies.engine") as mock_db_engine,
    ):
        # Configure mocks to avoid database connection
        mock_engine.return_value = AsyncMock()
        mock_session.return_value = AsyncMock()
        mock_db_engine.return_value = AsyncMock()

        with TestClient(app) as client:
            yield client


@pytest.fixture(autouse=True)
def reset_storage() -> None:
    """Reset storage state between tests to ensure isolation."""
    # Skip storage reset - models consolidated to flext-core patterns
    if storage:
        # Basic reset without using old models
        # Clear any maintenance message if stored as a key
        storage.delete("maintenance_message")


@pytest.fixture
def auth_headers() -> dict[str, str]:
    """Provide authentication headers for API requests."""
    return {
        "Authorization": "Bearer test-token",
        "Content-Type": "application/json",
    }


# Pytest configuration
def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers",
        "unit: mark test as unit test (fast, isolated)",
    )
    config.addinivalue_line(
        "markers",
        "integration: mark test as integration test (may require external services)",
    )
    config.addinivalue_line(
        "markers",
        "slow: mark test as slow running",
    )
    config.addinivalue_line(
        "markers",
        "api: mark test as API endpoint test",
    )
    config.addinivalue_line(
        "markers",
        "auth: mark test as authentication-related",
    )
    config.addinivalue_line(
        "markers",
        "pipeline: mark test as pipeline-related",
    )
    config.addinivalue_line(
        "markers",
        "plugin: mark test as plugin-related",
    )


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    """Modify test collection to add markers based on test location."""
    for item in items:
        # Add unit marker to all tests in unit directory
        if "/unit/" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        # Add integration marker to all tests in integration directory
        elif "/integration/" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
            item.add_marker(pytest.mark.slow)
        # Add e2e marker to all tests in e2e directory
        elif "/e2e/" in str(item.fspath):
            item.add_marker(pytest.mark.slow)

        # Add API marker to API-related tests
        if "api" in item.name.lower() or "endpoint" in item.name.lower():
            item.add_marker(pytest.mark.api)

        # Add auth marker to authentication tests
        if "auth" in item.name.lower():
            item.add_marker(pytest.mark.auth)

        # Add pipeline marker to pipeline tests
        if "pipeline" in item.name.lower():
            item.add_marker(pytest.mark.pipeline)

        # Add plugin marker to plugin tests
        if "plugin" in item.name.lower():
            item.add_marker(pytest.mark.plugin)
