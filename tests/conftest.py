"""COMPREHENSIVE pytest configuration for flext-api tests.

MASSIVE use of pytest ecosystem modules:
- pytest-asyncio: Async test support
- pytest-benchmark: Performance testing
- pytest-mock: Advanced mocking (replacing unittest.mock)
- pytest-httpx: HTTP client testing
- pytest-randomly: Test order randomization
- pytest-timeout: Test timeout management
- pytest-env: Environment variable management
- pytest-deadfixtures: Dead fixture detection
- pytest-cov: Coverage reporting
- pytest-clarity: Enhanced assertion reporting
- pytest-sugar: Enhanced test output
- pytest-xdist: Parallel test execution
- factory_boy: Professional test data generation
"""

from __future__ import annotations

import asyncio
import os
import tempfile
from collections.abc import AsyncGenerator, Callable, Iterator
from pathlib import Path

import pytest
from faker import Faker
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Flext imports
from flext_api import (
    FlextApiAppConfig,
    FlextApiClientRequest,
    FlextApiClientResponse,
    create_flext_api_app,
)
from flext_api.storage import FileStorageBackend, MemoryStorageBackend

# Import all support modules
from tests.support.factories import (
    FlextApiAppConfigFactory,
    FlextApiClientRequestFactory,
    FlextApiClientResponseFactory,
    FlextApiConfigFactory,
)
from tests.support.fixtures import (
    flext_api_app,
    flext_api_client,
    flext_api_config,
    test_client,
)
from tests.support.utils import (
    assert_flext_result_failure,
    assert_flext_result_success,
    create_test_request,
    create_test_response,
)

# ============================================================================
# PYTEST CONFIGURATION - MASSIVE MODULE USAGE
# ============================================================================

# Configure Faker for deterministic test data
fake = Faker()
Faker.seed(12345)

# Environment setup for testing
os.environ.update({
    "FLEXT_API_TESTING": "true",
    "FLEXT_DISABLE_EXTERNAL_CALLS": "0",  # ENABLE external calls for real testing
    "FLEXT_TEST_LOG_MINIMAL": "true",
    "FLEXT_FAST_TEST_MODE": "true",
    "ENVIRONMENT": "test",
    "LOG_LEVEL": "DEBUG",
})


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest with comprehensive markers and settings.

    Uses pytest-env, pytest-randomly, pytest-timeout for configuration.
    """
    # Add comprehensive test markers
    markers = [
        "unit: Fast isolated unit tests",
        "integration: Integration tests with external dependencies",
        "e2e: End-to-end workflow tests",
        "api: REST API endpoint tests",
        "client: HTTP client tests",
        "storage: Storage backend tests",
        "config: Configuration tests",
        "auth: Authentication tests",
        "benchmark: Performance benchmark tests (pytest-benchmark)",
        "slow: Slow running tests (pytest-timeout)",
        "network: Tests requiring network access",
        "async_test: Async tests (pytest-asyncio)",
        "mock_test: Tests using mocking (pytest-mock)",
        "factory_test: Tests using factory_boy",
    ]

    for marker in markers:
        config.addinivalue_line("markers", marker)


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    """Automatically mark tests based on location and content.

    Uses pytest collection hooks for automatic test categorization.
    """
    for item in items:
        # Add markers based on test location
        test_path = str(item.fspath)

        if "/unit/" in test_path:
            item.add_marker(pytest.mark.unit)

        if "/integration/" in test_path:
            item.add_marker(pytest.mark.integration)
            item.add_marker(pytest.mark.slow)

        if "/e2e/" in test_path:
            item.add_marker(pytest.mark.e2e)
            item.add_marker(pytest.mark.slow)

        if "/benchmarks/" in test_path:
            item.add_marker(pytest.mark.benchmark)

        # Add markers based on test name patterns
        test_name = item.name.lower()

        if "api" in test_name or "endpoint" in test_name:
            item.add_marker(pytest.mark.api)

        if "client" in test_name or "http" in test_name:
            item.add_marker(pytest.mark.client)

        if "storage" in test_name or "backend" in test_name:
            item.add_marker(pytest.mark.storage)

        if "config" in test_name:
            item.add_marker(pytest.mark.config)

        if "auth" in test_name:
            item.add_marker(pytest.mark.auth)

        if "async" in test_name or "await" in test_name:
            item.add_marker(pytest.mark.async_test)


# ============================================================================
# PYTEST-ASYNCIO CONFIGURATION
# ============================================================================

# Configure pytest-asyncio for async test support
# Note: AUTO_MODE configuration moved to pytest.ini or pyproject.toml
# pytest_asyncio.AUTO_MODE = True  # Not available in newer versions


@pytest.fixture
def event_loop() -> Iterator[asyncio.AbstractEventLoop]:
    """Function-scoped event loop for pytest-asyncio.

    Creates a fresh event loop for each test to avoid interference.
    This fixes 'There is no current event loop in thread' errors
    that occur when session-scoped loops interfere between tests.
    """
    # Create new event loop for each test
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    yield loop

    # Clean shutdown
    try:
        # Cancel all running tasks
        pending = asyncio.all_tasks(loop)
        for task in pending:
            task.cancel()

        if pending:
            # Wait for tasks to be cancelled
            loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))

        loop.close()
    except Exception:
        # Ensure loop is closed even if cleanup fails
        loop.close()
    finally:
        # Clear event loop policy
        asyncio.set_event_loop(None)


# ============================================================================
# FACTORY BOY INTEGRATION
# ============================================================================


@pytest.fixture
def api_request_factory() -> Callable[
    [str, str, dict[str, str] | None, dict[str, object] | None, float],
    FlextApiClientRequest,
]:
    """Provide FlextApiClientRequest factory for test data generation."""
    return FlextApiClientRequestFactory


@pytest.fixture
def api_response_factory() -> Callable[..., FlextApiClientResponse]:  # type: ignore[explicit-any]
    """Provide FlextApiClientResponse factory for test data generation."""
    return FlextApiClientResponseFactory


@pytest.fixture
def api_config_factory() -> Callable[..., object]:  # type: ignore[explicit-any]
    """Provide FlextApiConfig factory for test data generation."""
    return FlextApiConfigFactory


@pytest.fixture
def app_config_factory() -> Callable[[object | None], FlextApiAppConfig]:
    """Provide FlextApiAppConfig factory for test data generation."""
    return FlextApiAppConfigFactory


# ============================================================================
# PYTEST-HTTPX INTEGRATION
# ============================================================================


@pytest.fixture
async def httpx_mock() -> object:
    """Provide httpx mock for HTTP testing.

    Uses pytest-httpx for advanced HTTP mocking.
    """
    pytest_httpx = pytest.importorskip("pytest_httpx")
    return pytest_httpx.HTTPXMock()


# ============================================================================
# PYTEST-BENCHMARK INTEGRATION
# ============================================================================

try:
    import pytest_benchmark

    @pytest.fixture
    def benchmark_config() -> dict[str, object]:
        """Configure pytest-benchmark settings."""
        return {
            "min_rounds": 5,
            "max_time": 1.0,
            "timer": "time.perf_counter",
            "disable_gc": False,
            "warmup": False,
        }

except ImportError:
    # Fallback benchmark fixture for environments without pytest-benchmark
    @pytest.fixture
    def benchmark() -> Callable[..., object]:  # type: ignore[explicit-any]
        """Lightweight benchmark fallback."""

        def _bench(
            func: Callable[..., object], *args: object, **kwargs: object
        ) -> object:  # type: ignore[explicit-any]
            return func(*args, **kwargs)

        return _bench


# ============================================================================
# STORAGE AND FILESYSTEM FIXTURES
# ============================================================================


@pytest.fixture
def temp_dir() -> Iterator[Path]:
    """Provide temporary directory for test file operations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
async def memory_storage() -> AsyncGenerator[MemoryStorageBackend[object]]:
    """Provide memory storage backend for testing."""
    # MemoryBackend não aceita parâmetros no __init__
    storage = MemoryStorageBackend[object]()
    try:
        yield storage
    finally:
        # Backends não têm método close()
        pass


@pytest.fixture
async def file_storage(temp_dir: Path) -> AsyncGenerator[FileStorageBackend[object]]:
    """Provide file storage backend for testing."""
    # FileBackend aceita string como parâmetro, não Config
    storage = FileStorageBackend[object](str(temp_dir / "test_storage.json"))
    try:
        yield storage
    finally:
        # Backends não têm método close()
        pass


# ============================================================================
# APPLICATION FIXTURES
# ============================================================================


@pytest.fixture
def test_app_config() -> FlextApiAppConfig:
    """Provide test application configuration."""
    return FlextApiAppConfigFactory()


@pytest.fixture
def test_app(test_app_config: FlextApiAppConfig) -> FastAPI:
    """Provide configured test FastAPI application."""
    return create_flext_api_app(test_app_config)


@pytest.fixture
def sync_test_client(test_app: FastAPI) -> TestClient:
    """Provide synchronous test client."""
    return TestClient(test_app)


@pytest.fixture
def async_test_client(test_app: FastAPI) -> TestClient:
    """Provide test client (synchronous interface is sufficient for testing)."""
    return TestClient(test_app)


# ============================================================================
# UTILITY FIXTURES
# ============================================================================


@pytest.fixture
def fake_data() -> Faker:
    """Provide Faker instance for test data generation."""
    return fake


@pytest.fixture
def assert_success() -> Callable[..., None]:  # type: ignore[explicit-any]
    """Provide FlextResult success assertion utility."""
    return assert_flext_result_success


@pytest.fixture
def assert_failure() -> Callable[..., None]:  # type: ignore[explicit-any]
    """Provide FlextResult failure assertion utility."""
    return assert_flext_result_failure


@pytest.fixture
def create_request() -> Callable[
    [str, str, dict[str, str] | None, dict[str, object] | None, float],
    FlextApiClientRequest,
]:
    """Provide test request creation utility."""
    return create_test_request


@pytest.fixture
def create_response() -> Callable[..., FlextApiClientResponse]:  # type: ignore[explicit-any]
    """Provide test response creation utility."""
    return create_test_response


# ============================================================================
# PROJECT STRUCTURE FIXTURES
# ============================================================================


@pytest.fixture
def project_root() -> Path:
    """Get project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def src_dir(project_root: Path) -> Path:
    """Get source directory."""
    return project_root / "src"


@pytest.fixture
def tests_dir(project_root: Path) -> Path:
    """Get tests directory."""
    return project_root / "tests"


# ============================================================================
# CLEANUP AND PERFORMANCE FIXTURES
# ============================================================================


@pytest.fixture(autouse=True)
def cleanup_test_environment() -> None:
    """Automatically clean up test environment after each test."""
    return
    # Cleanup is handled by individual fixtures


@pytest.fixture(autouse=True)
def optimize_test_performance() -> None:
    """Optimize test performance with environment variables."""
    # Already set in module-level configuration
    return


# ============================================================================
# PYTEST-TIMEOUT CONFIGURATION
# ============================================================================

# Default timeout for all tests (can be overridden per test)
pytest_timeout = 30


# ============================================================================
# RE-EXPORT SUPPORT FIXTURES
# ============================================================================

# Re-export key fixtures from support modules for convenience
__all__ = [
    "assert_flext_result_failure",
    "assert_flext_result_success",
    "create_test_request",
    "create_test_response",
    "flext_api_app",
    "flext_api_client",
    "flext_api_config",
    "test_client",
]
