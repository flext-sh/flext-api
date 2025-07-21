"""Tests for plugin management endpoints."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from flext_api.main import app


@pytest.fixture
def client() -> TestClient:
    """Create test client for plugin endpoints."""
    return TestClient(app)


def test_install_plugin_endpoint(client: TestClient) -> None:
    """Test plugin installation endpoint - PluginManager method not implemented."""
    plugin_data = {
        "name": "tap-csv",
        "plugin_type": "tap",
        "version": "1.0.0",
        "source": "hub",
        "configuration": {"input_file": "data.csv"},
    }

    response = client.post("/api/v1/plugins/install", json=plugin_data)

    assert response.status_code == 503
    data = response.json()
    assert "install_plugin" in data["detail"]
    assert "'PluginManager' object has no attribute 'install_plugin'" in data["detail"]


def test_list_plugins_endpoint_default(client: TestClient) -> None:
    """Test list plugins endpoint - registry not available."""
    response = client.get("/api/v1/plugins")

    assert response.status_code == 503
    data = response.json()
    assert "Plugin registry not available" in data["detail"]


def test_list_plugins_endpoint_with_params(client: TestClient) -> None:
    """Test list plugins endpoint with custom parameters - registry not available."""
    response = client.get(
        "/api/v1/plugins?page=2&page_size=10&category=taps&status=installed",
    )

    assert response.status_code == 503
    data = response.json()
    assert "Plugin registry not available" in data["detail"]


def test_list_plugins_endpoint_invalid_page(client: TestClient) -> None:
    """Test list plugins endpoint with invalid page number."""
    response = client.get("/api/v1/plugins?page=0")

    assert response.status_code == 422  # Validation error


def test_list_plugins_endpoint_invalid_page_size(client: TestClient) -> None:
    """Test list plugins endpoint with invalid page size."""
    response = client.get("/api/v1/plugins?page_size=101")  # Over limit of 100

    assert response.status_code == 422  # Validation error


def test_get_plugin_endpoint(client: TestClient) -> None:
    """Test get specific plugin endpoint with existing plugin."""
    plugin_name = "tap-ldap"
    response = client.get(f"/api/v1/plugins/{plugin_name}")

    assert response.status_code == 200
    data = response.json()

    assert data["name"] == plugin_name
    assert data["version"] == "1.0.0"
    assert data["plugin_type"] == "tap"  # Should be "tap" since name starts with "tap-"
    assert data["description"] == "LDAP tap for user/group extraction"
    assert data["configuration"] == {}
    assert data["status"] == "active"
    assert data["source"] == "hub"
    assert "plugin_id" in data
    assert "updated_at" in data


def test_get_plugin_endpoint_not_found(client: TestClient) -> None:
    """Test get specific plugin endpoint with non-existent plugin."""
    plugin_name = "tap-nonexistent"
    response = client.get(f"/api/v1/plugins/{plugin_name}")

    assert response.status_code == 404
    data = response.json()
    assert f"Plugin '{plugin_name}' not found" in data["detail"]


def test_update_plugin_config_endpoint(client: TestClient) -> None:
    """Test update plugin configuration endpoint."""
    plugin_name = "tap-mysql"
    config_data = {
        "configuration": {"host": "localhost", "port": 3306, "database": "test_db"},
    }

    response = client.put(f"/api/v1/plugins/{plugin_name}/config", json=config_data)

    assert response.status_code == 200
    data = response.json()

    assert data["name"] == plugin_name
    assert data["version"] == "latest"
    assert data["plugin_type"] == "tap"  # Should be "tap" since name starts with "tap-"
    assert "configuration updated successfully" in data["description"]
    assert data["configuration"] == config_data["configuration"]
    assert data["status"] == "active"
    assert data["source"] == "hub"
    assert "plugin_id" in data
    assert "updated_at" in data


def test_update_plugin_config_target_type(client: TestClient) -> None:
    """Test update plugin configuration for target plugin."""
    plugin_name = "target-postgres"
    config_data = {"configuration": {"host": "localhost", "port": 5432}}

    response = client.put(f"/api/v1/plugins/{plugin_name}/config", json=config_data)

    assert response.status_code == 200
    data = response.json()

    assert (
        data["plugin_type"] == "target"
    )  # Should be "target" since name doesn't start with "tap-"
    assert data["status"] == "active"
    assert "plugin_id" in data


def test_update_plugin_config_empty_name(client: TestClient) -> None:
    """Test update plugin configuration with empty name."""
    config_data = {"configuration": {"key": "value"}}

    response = client.put("/api/v1/plugins/ /config", json=config_data)

    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Plugin name is required"


def test_update_plugin_config_invalid_config(client: TestClient) -> None:
    """Test update plugin configuration with invalid configuration."""
    plugin_name = "test-plugin"
    config_data = {
        "configuration": "invalid_config",  # Should be dict, not string
    }

    response = client.put(f"/api/v1/plugins/{plugin_name}/config", json=config_data)

    assert response.status_code == 422  # Validation error from Pydantic
    data = response.json()
    assert "detail" in data


def test_update_plugin_endpoint_not_implemented(client: TestClient) -> None:
    """Test update plugin endpoint - method not available in PluginManager."""
    plugin_name = "tap-csv"
    update_data = {"version": "2.0.0", "force_update": False}

    response = client.put(f"/api/v1/plugins/{plugin_name}/update", json=update_data)

    assert response.status_code == 503
    data = response.json()
    assert "update_plugin" in data["detail"]
    assert "'PluginManager' object has no attribute 'update_plugin'" in data["detail"]


def test_uninstall_plugin_endpoint_not_implemented(client: TestClient) -> None:
    """Test uninstall plugin endpoint - method not available in PluginManager."""
    plugin_name = "tap-csv"

    response = client.delete(f"/api/v1/plugins/{plugin_name}")

    assert response.status_code == 503
    data = response.json()
    assert "uninstall_plugin" in data["detail"]
    assert (
        "'PluginManager' object has no attribute 'uninstall_plugin'" in data["detail"]
    )


def test_get_plugin_stats_endpoint(client: TestClient) -> None:
    """Test get plugin statistics endpoint."""
    response = client.get("/api/v1/plugins/stats")

    assert response.status_code == 200
    data = response.json()

    assert data["total_plugins"] == 0
    assert data["installed_plugins"] == 0
    assert data["plugins_by_type"] == {}
    assert data["plugins_by_status"] == {}
    assert data["plugins_by_source"] == {}
    assert data["recent_installations"] == []
    assert data["update_available_count"] == 0
    assert data["health_summary"] == {}


def test_check_plugin_health_endpoint_not_implemented(client: TestClient) -> None:
    """Test check plugin health endpoint - method not implemented."""
    plugin_name = "tap-csv"

    response = client.post(f"/api/v1/plugins/{plugin_name}/health-check")

    assert response.status_code == 503
    data = response.json()
    assert "check_plugin_health" in data["detail"]
    assert (
        "'PluginManager' object has no attribute 'check_plugin_health'"
        in data["detail"]
    )


def test_install_plugin_minimal_data(client: TestClient) -> None:
    """Test plugin installation with minimal required data - version required."""
    plugin_data = {"name": "target-jsonl", "plugin_type": "target"}

    response = client.post("/api/v1/plugins/install", json=plugin_data)

    assert response.status_code == 400
    data = response.json()
    assert "Plugin name and version required" in data["detail"]


def test_install_plugin_invalid_data(client: TestClient) -> None:
    """Test plugin installation with invalid data."""
    plugin_data = {
        "invalid_field": "test",
        # Missing required 'name' and 'plugin_type' fields
    }

    response = client.post("/api/v1/plugins/install", json=plugin_data)

    assert response.status_code == 422  # Validation error


def test_get_plugin_with_special_characters(client: TestClient) -> None:
    """Test get plugin with special characters in name (non-existent plugin)."""
    plugin_name = "tap-custom_plugin-v2"
    response = client.get(f"/api/v1/plugins/{plugin_name}")

    assert response.status_code == 404
    data = response.json()

    assert f"Plugin '{plugin_name}' not found" in data["detail"]


def test_update_plugin_config_empty_configuration(client: TestClient) -> None:
    """Test update plugin configuration with empty configuration dict."""
    plugin_name = "tap-test"
    config_data: dict[str, dict[str, str]] = {"configuration": {}}

    response = client.put(f"/api/v1/plugins/{plugin_name}/config", json=config_data)

    assert response.status_code == 200
    data = response.json()

    assert data["configuration"] == {}


def test_list_plugins_with_search_param(client: TestClient) -> None:
    """Test list plugins with search parameter - registry not available."""
    response = client.get("/api/v1/plugins?search=postgres")

    assert response.status_code == 503
    data = response.json()
    assert "Plugin registry not available" in data["detail"]
