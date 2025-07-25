"""Basic tests for FLEXT API main application."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from flext_api.main import app, storage
from flext_api.models.system import MaintenanceMode, SystemStatusType


@pytest.fixture
def client() -> TestClient:
    """Create test client with fresh storage."""
    # Reset storage state before each test
    storage.system_status = SystemStatusType.HEALTHY
    storage.maintenance_mode = MaintenanceMode.NONE
    storage.maintenance_message = None
    storage.alerts.clear()
    storage.metrics.clear()
    storage.backups.clear()
    storage.pipelines.clear()
    storage.executions.clear()
    # Reset uptime start to prevent time drift issues
    from datetime import UTC, datetime

    storage.uptime_start = datetime.now(UTC)

    return TestClient(app)


def test_health_endpoint(client: TestClient) -> None:
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data


def test_readiness_endpoint(client: TestClient) -> None:
    """Test readiness probe endpoint."""
    response = client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert "timestamp" in data


def test_system_status_endpoint(client: TestClient) -> None:
    """Test system status endpoint."""
    response = client.get("/api/v1/system/status")
    assert response.status_code == 200
    data = response.json()
    assert data["system_status"] == "healthy"
    assert "uptime_seconds" in data


def test_list_pipelines_endpoint(client: TestClient) -> None:
    """Test list pipelines endpoint."""
    response = client.get("/api/v1/pipelines")
    if response.status_code != 200:
        # Use structured logging instead of print
        import structlog

        logger = structlog.get_logger(__name__)
        logger.error(
            "Pipeline endpoint error",
            status_code=response.status_code,
            content=response.text,
        )
    assert response.status_code == 200
    data = response.json()
    assert "pipelines" in data
    assert "total_count" in data
    assert "page" in data
    assert "page_size" in data
    assert "has_next" in data
    assert "has_previous" in data


def test_list_plugins_endpoint(client: TestClient) -> None:
    """Test list plugins endpoint with mocked plugin registry."""
    # Create a complete mock module with PluginRegistry
    mock_plugin_module = MagicMock()
    mock_registry_instance = MagicMock()

    # Setup the async method properly
    async def mock_list_plugins(*args: Any, **kwargs: object) -> MagicMock:
        return MagicMock(plugins=[], total_count=0, page=1, page_size=20, total_pages=0)

    mock_registry_instance.list_plugins = mock_list_plugins
    mock_plugin_module.PluginRegistry = lambda: mock_registry_instance

    # Mock the import completely
    with patch.dict("sys.modules", {"flext_plugin.registry": mock_plugin_module}):
        response = client.get("/api/v1/plugins")

        if response.status_code != 200:
            # Use structured logging instead of print
            import structlog

            logger = structlog.get_logger(__name__)
            logger.error(
                "Plugin endpoint error",
                status_code=response.status_code,
                content=response.text,
            )

        assert response.status_code == 200
        data = response.json()
        assert "plugins" in data
        assert "total_count" in data
        # Storage has 3 plugins: tap-oracle-oic, tap-ldap, target-ldap
        assert data["total_count"] == 3
        assert len(data["plugins"]) == 3
        # Check first plugin structure
        first_plugin = data["plugins"][0]
        assert "name" in first_plugin
        assert "plugin_type" in first_plugin
        assert first_plugin["name"] in {"tap-oracle-oic", "tap-ldap", "target-ldap"}


def test_get_plugin_endpoint(client: TestClient) -> None:
    """Test get specific plugin endpoint."""
    response = client.get("/api/v1/plugins/tap-oracle-oic")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "tap-oracle-oic"
    assert data["plugin_type"] == "tap"


def test_get_nonexistent_plugin_endpoint(client: TestClient) -> None:
    """Test get nonexistent plugin endpoint."""
    response = client.get("/api/v1/plugins/nonexistent-plugin")
    assert response.status_code == 404


def test_get_system_alerts_endpoint(client: TestClient) -> None:
    """Test get system alerts endpoint."""
    response = client.get("/api/v1/system/alerts")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_system_metrics_endpoint(client: TestClient) -> None:
    """Test get system metrics endpoint."""
    response = client.get("/api/v1/system/metrics")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_system_backups_endpoint(client: TestClient) -> None:
    """Test get system backups endpoint."""
    response = client.get("/api/v1/system/backups")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
