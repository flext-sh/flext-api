"""Tests for FlextPluginService - Real comprehensive coverage."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from flext_api.application.services.plugin_service import FlextPluginService
from flext_api.models.plugin import PluginInstallRequest, PluginSource


class TestPluginService:
    """Comprehensive tests for FlextPluginService."""

    @pytest.fixture
    def plugin_service(self) -> FlextPluginService:
        """Create plugin service instance."""
        return FlextPluginService()

    @pytest.fixture
    def valid_install_request(self) -> PluginInstallRequest:
        """Create valid plugin install request."""
        return PluginInstallRequest(
            plugin_name="tap-test",
            plugin_version="1.0.0",
            source=PluginSource.HUB,
            configuration={"setting1": "value1"},
        )

    async def test_list_plugins_success(
        self, plugin_service: FlextPluginService
    ) -> None:
        """Test successful plugin listing."""
        result = await plugin_service.list_plugins()

        assert result.is_success
        assert result.data is not None
        assert isinstance(result.data, list)

    async def test_list_plugins_with_category_filter(
        self, plugin_service: FlextPluginService
    ) -> None:
        """Test plugin listing with category filter."""
        result = await plugin_service.list_plugins(category="tap")

        assert result.is_success
        assert result.data is not None
        assert isinstance(result.data, list)

    async def test_list_plugins_with_status_filter(
        self, plugin_service: FlextPluginService
    ) -> None:
        """Test plugin listing with status filter."""
        result = await plugin_service.list_plugins(status="installed")

        assert result.is_success
        assert result.data is not None
        assert isinstance(result.data, list)

    async def test_get_plugin_by_name_success(
        self, plugin_service: FlextPluginService
    ) -> None:
        """Test successful plugin retrieval by name."""
        result = await plugin_service.get_plugin_by_name("tap-oracle-oic")

        assert result.is_success
        assert result.data is not None
        assert result.data["name"] == "tap-oracle-oic"

    async def test_get_plugin_by_name_not_found(
        self, plugin_service: FlextPluginService
    ) -> None:
        """Test plugin retrieval for non-existent plugin."""
        result = await plugin_service.get_plugin_by_name("non-existent-plugin")

        assert not result.is_success
        assert "Plugin not found" in result.error

    async def test_get_plugin_by_name_empty_name(
        self, plugin_service: FlextPluginService
    ) -> None:
        """Test plugin retrieval with empty name."""
        result = await plugin_service.get_plugin_by_name("")

        assert not result.is_success
        assert "Plugin name cannot be empty" in result.error

    async def test_install_plugin_success(
        self,
        plugin_service: FlextPluginService,
        valid_install_request: PluginInstallRequest,
    ) -> None:
        """Test successful plugin installation."""
        result = await plugin_service.install_plugin(valid_install_request)

        assert result.is_success
        assert result.data is not None
        assert "installation_id" in result.data
        assert "plugin_name" in result.data

    async def test_install_plugin_already_installed(
        self, plugin_service: FlextPluginService
    ) -> None:
        """Test installing already installed plugin."""
        request = PluginInstallRequest(
            plugin_name="tap-oracle-oic",  # Already in storage
            plugin_version="1.0.0",
            source=PluginSource.HUB,
        )

        result = await plugin_service.install_plugin(request)

        # Should still succeed (update/reinstall)
        assert result.is_success

    async def test_install_plugin_invalid_name(
        self, plugin_service: FlextPluginService
    ) -> None:
        """Test installing plugin with invalid name."""
        request = PluginInstallRequest(
            plugin_name="",
            plugin_version="1.0.0",
            source=PluginSource.HUB,
        )

        result = await plugin_service.install_plugin(request)

        assert not result.is_success
        assert "Plugin installation failed" in result.error

    async def test_install_plugin_invalid_version(
        self, plugin_service: FlextPluginService
    ) -> None:
        """Test installing plugin with invalid version."""
        request = PluginInstallRequest(
            plugin_name="tap-test",
            plugin_version="",
            source=PluginSource.HUB,
        )

        result = await plugin_service.install_plugin(request)

        assert not result.is_success
        assert "Plugin installation failed" in result.error

    async def test_uninstall_plugin_success(
        self, plugin_service: FlextPluginService
    ) -> None:
        """Test successful plugin uninstallation."""
        result = await plugin_service.uninstall_plugin("tap-oracle-oic")

        assert result.is_success
        assert result.data is not None
        assert "message" in result.data

    async def test_uninstall_plugin_not_found(
        self, plugin_service: FlextPluginService
    ) -> None:
        """Test uninstalling non-existent plugin."""
        result = await plugin_service.uninstall_plugin("non-existent-plugin")

        assert not result.is_success
        assert "Plugin uninstallation failed" in result.error

    async def test_uninstall_plugin_empty_name(
        self, plugin_service: FlextPluginService
    ) -> None:
        """Test uninstalling plugin with empty name."""
        result = await plugin_service.uninstall_plugin("")

        assert not result.is_success
        assert "Plugin uninstallation failed" in result.error

    async def test_update_plugin_success(
        self, plugin_service: FlextPluginService
    ) -> None:
        """Test successful plugin update."""
        result = await plugin_service.update_plugin("tap-oracle-oic", "2.0.0")

        assert result.is_success
        assert result.data is not None
        assert "update_id" in result.data

    async def test_update_plugin_not_found(
        self, plugin_service: FlextPluginService
    ) -> None:
        """Test updating non-existent plugin."""
        result = await plugin_service.update_plugin("non-existent-plugin", "2.0.0")

        assert not result.is_success
        assert "Plugin update failed" in result.error

    async def test_update_plugin_invalid_version(
        self, plugin_service: FlextPluginService
    ) -> None:
        """Test updating plugin with invalid version."""
        result = await plugin_service.update_plugin("tap-oracle-oic", "")

        assert not result.is_success
        assert "Plugin update failed" in result.error

    async def test_configure_plugin_success(
        self, plugin_service: FlextPluginService
    ) -> None:
        """Test successful plugin configuration."""
        config = {"host": "localhost", "port": 5432}
        result = await plugin_service.configure_plugin("tap-oracle-oic", config)

        assert result.is_success
        assert result.data is not None
        assert "configuration_id" in result.data

    async def test_configure_plugin_not_found(
        self, plugin_service: FlextPluginService
    ) -> None:
        """Test configuring non-existent plugin."""
        config = {"host": "localhost"}
        result = await plugin_service.configure_plugin("non-existent-plugin", config)

        assert not result.is_success
        assert "Plugin configuration failed" in result.error

    async def test_configure_plugin_empty_config(
        self, plugin_service: FlextPluginService
    ) -> None:
        """Test configuring plugin with empty configuration."""
        result = await plugin_service.configure_plugin("tap-oracle-oic", {})

        assert result.is_success  # Empty config should be allowed

    async def test_validate_plugin_success(
        self, plugin_service: FlextPluginService
    ) -> None:
        """Test successful plugin validation."""
        result = await plugin_service.validate_plugin("tap-oracle-oic")

        assert result.is_success
        assert result.data is not None
        assert "validation_result" in result.data

    async def test_validate_plugin_not_found(
        self, plugin_service: FlextPluginService
    ) -> None:
        """Test validating non-existent plugin."""
        result = await plugin_service.validate_plugin("non-existent-plugin")

        assert not result.is_success
        assert "Plugin validation failed" in result.error

    async def test_get_plugin_status_success(
        self, plugin_service: FlextPluginService
    ) -> None:
        """Test getting plugin status."""
        result = await plugin_service.get_plugin_status("tap-oracle-oic")

        assert result.is_success
        assert result.data is not None
        assert "status" in result.data

    async def test_get_plugin_status_not_found(
        self, plugin_service: FlextPluginService
    ) -> None:
        """Test getting status for non-existent plugin."""
        result = await plugin_service.get_plugin_status("non-existent-plugin")

        assert not result.is_success
        assert "Plugin status check failed" in result.error

    async def test_discover_plugins_success(
        self, plugin_service: FlextPluginService
    ) -> None:
        """Test plugin discovery."""
        result = await plugin_service.discover_plugins()

        assert result.is_success
        assert result.data is not None
        assert isinstance(result.data, list)

    async def test_discover_plugins_with_source(
        self, plugin_service: FlextPluginService
    ) -> None:
        """Test plugin discovery with specific source."""
        result = await plugin_service.discover_plugins(source=PluginSource.HUB)

        assert result.is_success
        assert result.data is not None
        assert isinstance(result.data, list)

    async def test_search_plugins_success(
        self, plugin_service: FlextPluginService
    ) -> None:
        """Test plugin search."""
        result = await plugin_service.search_plugins("oracle")

        assert result.is_success
        assert result.data is not None
        assert isinstance(result.data, list)

    async def test_search_plugins_empty_query(
        self, plugin_service: FlextPluginService
    ) -> None:
        """Test plugin search with empty query."""
        result = await plugin_service.search_plugins("")

        assert result.is_success
        assert result.data is not None
        assert isinstance(result.data, list)

    async def test_error_handling_exception(
        self, plugin_service: FlextPluginService
    ) -> None:
        """Test error handling when exceptions occur."""
        with patch.object(plugin_service, "_get_storage") as mock_storage:
            mock_storage.side_effect = Exception("Unexpected error")

            result = await plugin_service.list_plugins()

            assert not result.is_success
            assert "Failed to list plugins" in result.error

    async def test_install_from_github_source(
        self, plugin_service: FlextPluginService
    ) -> None:
        """Test installing plugin from GitHub source."""
        request = PluginInstallRequest(
            plugin_name="tap-github",
            plugin_version="1.0.0",
            source=PluginSource.GITHUB,
            source_url="https://github.com/user/tap-github",
        )

        result = await plugin_service.install_plugin(request)

        assert result.is_success

    async def test_install_from_local_source(
        self, plugin_service: FlextPluginService
    ) -> None:
        """Test installing plugin from local source."""
        request = PluginInstallRequest(
            plugin_name="tap-local",
            plugin_version="1.0.0",
            source=PluginSource.LOCAL,
            source_path="./plugins/tap-local",
        )

        result = await plugin_service.install_plugin(request)

        assert result.is_success
