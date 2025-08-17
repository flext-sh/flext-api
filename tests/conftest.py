"""Pytest configuration for flext-api tests.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT
"""

import asyncio
import os
from collections.abc import AsyncGenerator, Callable, Iterator
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from faker import Faker
from fastapi.testclient import TestClient

from flext_api import FlextApiClient, app

# Garanta um loop corrente no thread principal para pytest-asyncio (Py3.13)
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())


# Configure faker for consistent test data
fake = Faker()
Faker.seed(12345)  # Deterministic fake data


# Setup test environment
os.environ["FLEXT_API_TESTING"] = "true"


def _ensure_event_loop() -> None:
    """Certifica que existe um loop corrente no thread principal."""
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())


def pytest_sessionstart(session: pytest.Session) -> None:  # type: ignore[override]  # noqa: ARG001
    """Avoid pre-creating event loops at session start."""
    _ensure_event_loop()


def pytest_runtest_setup(item: pytest.Item) -> None:  # type: ignore[override]  # noqa: ARG001
    """Avoid altering event loop before each test."""
    _ensure_event_loop()


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
        "version": "0.9.0",
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
    # Storage is now managed within the app instance via app.state.storage
    # No need to reset external storage reference


@pytest.fixture
def auth_headers() -> dict[str, str]:
    """Provide authentication headers for API requests."""
    return {
        "Authorization": "Bearer test-token",
        "Content-Type": "application/json",
    }


@pytest.fixture
async def cleanup_client_sessions() -> AsyncGenerator[None]:
    """DRY fixture to cleanup all FlextApiClient sessions after async tests."""
    # Pre-test: ensure clean state
    await FlextApiClient.cleanup_all_sessions()

    try:
        yield
    finally:
        # Post-test: cleanup any remaining sessions
        await FlextApiClient.cleanup_all_sessions()


@pytest.fixture(autouse=True)
def sync_cleanup_client_sessions() -> None:
    """Sync fixture to ensure client cleanup for sync tests."""
    # For sync tests, we just skip the cleanup since they shouldn't use async client


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


# ============================================================================
# EVENT LOOP FIXTURES - Enhanced asyncio support
# ============================================================================


@pytest.fixture(scope="session")
def event_loop() -> Iterator[asyncio.AbstractEventLoop]:
    """Loop de evento de sessão compatível com pytest-asyncio."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    else:
        asyncio.set_event_loop(loop)

    # Não fechamos o loop explicitamente para evitar falhas de tarefas tardias
    return loop


# ============================================================================
# PERFORMANCE OPTIMIZATION FIXTURES
# ============================================================================


@pytest.fixture(autouse=True)
def optimize_test_performance() -> None:
    """Optimize test performance by disabling unnecessary features in test mode."""
    # Disable external network calls
    os.environ["FLEXT_DISABLE_EXTERNAL_CALLS"] = "true"
    # Reduce logging verbosity for performance
    os.environ["FLEXT_TEST_LOG_MINIMAL"] = "true"
    # Enable fast test mode
    os.environ["FLEXT_FAST_TEST_MODE"] = "true"


# -----------------------------------------------------------------------------
# Benchmark fixture fallback (define only if pytest-benchmark is NOT installed)
# -----------------------------------------------------------------------------
try:  # pragma: no cover - optional dependency
    import pytest_benchmark  # noqa: F401
except Exception:  # plugin not available; provide lightweight shim

    @pytest.fixture
    def benchmark() -> Callable[[Callable[..., object]], object]:
        """Lightweight benchmark shim that simply calls the function under test.

        Provides compatibility for tests that expect the `benchmark` fixture
        without requiring the pytest-benchmark plugin for local runs.
        """

        def _bench(
            func: Callable[..., object],
            *args: object,
            **kwargs: object,
        ) -> object:
            return func(*args, **kwargs)

        return _bench
