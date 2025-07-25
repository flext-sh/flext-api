"""Test configuration for flext-api tests.

Provides test-specific configuration with SQLite database
and mocked external dependencies.
"""

from __future__ import annotations

import os
import tempfile
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

if TYPE_CHECKING:
    from collections.abc import Generator


@pytest.fixture(scope="session")
def test_db_url() -> str:
    """Provide SQLite database URL for testing."""
    # Create temporary database file
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)
    return f"sqlite:///{db_path}"


@pytest.fixture(scope="session")
def async_test_db_url() -> str:
    """Provide async SQLite database URL for testing."""
    # Create temporary database file
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)
    return f"sqlite+aiosqlite:///{db_path}"


@contextmanager
def mock_database_dependencies(async_db_url: str) -> Generator[None]:
    """Mock database dependencies for testing."""
    # Create test async engine
    test_engine = create_async_engine(async_db_url, echo=False)
    test_session_factory = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    with (
        patch("flext_api.dependencies.engine", test_engine),
        patch("flext_api.dependencies.async_session_factory", test_session_factory),
        patch("flext_api.infrastructure.database.session.engine", test_engine),
        patch(
            "flext_api.infrastructure.database.session.async_session_factory",
            test_session_factory,
        ),
    ):
        yield


@contextmanager
def mock_external_services() -> Generator[None]:
    """Mock external service dependencies for testing."""
    # Mock FlextAuthPlatform
    mock_auth_platform = MagicMock()
    mock_auth_platform.initialize.return_value = None
    mock_auth_platform.authenticate_user.return_value = "mock_token"
    mock_auth_platform.get_user_from_token.return_value = {"username": "testuser"}
    mock_auth_platform.logout_user.return_value = True
    mock_auth_platform.refresh_token.return_value = "new_token"

    # Mock FlextPluginPlatform
    mock_plugin_platform = MagicMock()
    mock_plugin_platform.initialize.return_value = None
    mock_plugin_platform.list_plugins.return_value = []
    mock_plugin_platform.install_plugin.return_value = {
        "name": "test-plugin",
        "status": "installed",
    }
    mock_plugin_platform.uninstall_plugin.return_value = True
    mock_plugin_platform.get_plugin_info.return_value = {"name": "test-plugin"}

    with (
        patch(
            "flext_api.application.services.auth_service.FlextAuthPlatform",
            return_value=mock_auth_platform,
        ),
        patch(
            "flext_api.application.services.plugin_service.FlextPluginPlatform",
            return_value=mock_plugin_platform,
        ),
        patch(
            "flext_api.dependencies.FlextAuthPlatform", return_value=mock_auth_platform
        ),
        patch(
            "flext_api.dependencies.FlextPluginPlatform",
            return_value=mock_plugin_platform,
        ),
    ):
        yield


@pytest.fixture
def test_client_with_mocked_deps(async_test_db_url: str) -> Generator[Any]:
    """Create test client with all dependencies mocked."""
    from fastapi.testclient import TestClient

    with mock_database_dependencies(async_test_db_url), mock_external_services():
        from flext_api.main import app

        with TestClient(app) as client:
            yield client


# Test configuration settings
TEST_CONFIG = {
    "project_name": "FLEXT API Test",
    "database_url": "sqlite:///test.db",
    "debug": True,
    "log_level": "DEBUG",
}


def override_get_api_settings() -> Any:
    """Override API settings for testing."""
    from flext_api.infrastructure.config import APIConfig

    return APIConfig(**TEST_CONFIG)
