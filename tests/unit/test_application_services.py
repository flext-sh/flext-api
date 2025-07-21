"""Tests for FLEXT API application services."""

from __future__ import annotations

from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from flext_core.domain.types import ServiceResult

from flext_api.application.services.auth_service import AuthService
from flext_api.application.services.plugin_service import PluginService
from flext_api.domain.entities import Plugin, PluginType
from flext_api.models.auth import UserAPI


class TestAuthService:
    """Test AuthService implementation."""

    @pytest.fixture
    def mock_auth_service(self) -> AsyncMock:
        """Create mock authentication service."""
        mock = AsyncMock()
        mock.authenticate_user = AsyncMock()
        mock.create_user = AsyncMock()
        return mock

    @pytest.fixture
    def mock_session_manager(self) -> AsyncMock:
        """Create mock session manager."""
        mock = AsyncMock()
        mock.terminate_session = AsyncMock()
        mock.refresh_token = AsyncMock()
        mock.validate_token = AsyncMock()
        return mock

    @pytest.fixture
    def auth_service(
        self,
        mock_auth_service: AsyncMock,
        mock_session_manager: AsyncMock,
    ) -> AuthService:
        """Create AuthService instance for testing."""
        return AuthService(mock_auth_service, mock_session_manager)

    @pytest.mark.asyncio
    async def test_login_success(
        self,
        auth_service: AuthService,
        mock_auth_service: AsyncMock,
    ) -> None:
        """Test successful login."""
        # Mock successful authentication
        mock_user = Mock()
        mock_user.id = "user123"
        mock_user.username = "testuser"
        mock_session = Mock()
        mock_session.id = "session123"
        mock_session.token = "token123"

        mock_auth_service.authenticate_user.return_value = ServiceResult.ok(
            (
                mock_user,
                mock_session,
            ),
        )

        result = await auth_service.login("test@example.com", "password123")

        assert result.is_success
        data = result.unwrap()
        assert data["access_token"] == "token123"
        assert data["token_type"] == "bearer"
        assert data["username"] == "testuser"

        mock_auth_service.authenticate_user.assert_called_once()

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(
        self,
        auth_service: AuthService,
        mock_auth_service: AsyncMock,
    ) -> None:
        """Test login with invalid credentials."""
        mock_auth_service.authenticate_user.return_value = ServiceResult.fail(
            "Invalid credentials",
        )

        result = await auth_service.login("test@example.com", "wrongpassword")

        assert not result.is_success
        assert result.error is not None
        assert "Invalid credentials" in result.error

    @pytest.mark.asyncio
    async def test_login_missing_email(self, auth_service: AuthService) -> None:
        """Test login with missing email."""
        result = await auth_service.login("", "password123")

        assert not result.is_success
        assert result.error is not None
        assert "Email and password are required" in result.error

    @pytest.mark.asyncio
    async def test_login_missing_password(self, auth_service: AuthService) -> None:
        """Test login with missing password."""
        result = await auth_service.login("test@example.com", "")

        assert not result.is_success
        assert result.error is not None
        assert "Email and password are required" in result.error

    @pytest.mark.asyncio
    async def test_login_with_device_info(
        self,
        auth_service: AuthService,
        mock_auth_service: AsyncMock,
    ) -> None:
        """Test login with device information."""
        mock_user = Mock()
        mock_user.id = "user123"
        mock_user.username = "testuser"
        mock_session = Mock()
        mock_session.id = "session123"
        mock_session.token = "token123"

        mock_auth_service.authenticate_user.return_value = ServiceResult.ok(
            (
                mock_user,
                mock_session,
            ),
        )

        device_info = {"ip_address": "192.168.1.1", "user_agent": "Mozilla/5.0"}

        result = await auth_service.login(
            "test@example.com",
            "password123",
            device_info,
        )

        assert result.is_success

        # Verify device info was passed to auth service
        call_args = mock_auth_service.authenticate_user.call_args
        assert call_args.kwargs["ip_address"] == "192.168.1.1"
        assert call_args.kwargs["user_agent"] == "Mozilla/5.0"

    @pytest.mark.asyncio
    async def test_logout_success(
        self,
        auth_service: AuthService,
        mock_session_manager: AsyncMock,
    ) -> None:
        """Test successful logout."""
        mock_session_manager.terminate_session.return_value = ServiceResult.ok(True)

        result = await auth_service.logout("session123")

        assert result.is_success
        assert result.unwrap() is True

        mock_session_manager.terminate_session.assert_called_once_with("session123")

    @pytest.mark.asyncio
    async def test_logout_failure(
        self,
        auth_service: AuthService,
        mock_session_manager: AsyncMock,
    ) -> None:
        """Test logout failure."""
        mock_session_manager.terminate_session.return_value = ServiceResult.fail(
            "Session not found",
        )

        result = await auth_service.logout("invalid_session")

        assert not result.is_success
        assert result.error is not None
        assert "Session not found" in result.error

    @pytest.mark.asyncio
    async def test_refresh_token_success(
        self,
        auth_service: AuthService,
        mock_session_manager: AsyncMock,
    ) -> None:
        """Test successful token refresh."""
        token_data = {
            "access_token": "new_token123",
            "refresh_token": "new_refresh123",
            "expires_in": 3600,
            "session_id": "session123",
        }

        mock_session_manager.refresh_token.return_value = ServiceResult.ok(token_data)

        result = await auth_service.refresh_token("refresh123")

        assert result.is_success
        data = result.unwrap()
        assert data["access_token"] == "new_token123"
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 3600

    @pytest.mark.asyncio
    async def test_refresh_token_invalid(
        self,
        auth_service: AuthService,
        mock_session_manager: AsyncMock,
    ) -> None:
        """Test refresh with invalid token."""
        mock_session_manager.refresh_token.return_value = ServiceResult.fail(
            "Invalid refresh token",
        )

        result = await auth_service.refresh_token("invalid_refresh")

        assert not result.is_success
        assert result.error is not None
        assert "Invalid refresh token" in result.error

    @pytest.mark.asyncio
    async def test_register_success(
        self,
        auth_service: AuthService,
        mock_auth_service: AsyncMock,
    ) -> None:
        """Test successful user registration."""
        mock_user_data = Mock()
        mock_user_data.roles = ["user"]

        mock_auth_service.create_user.return_value = ServiceResult.ok(mock_user_data)

        result = await auth_service.register(
            "testuser",
            "test@example.com",
            "password123",
        )

        assert result.is_success
        data = result.unwrap()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert data["role"] == "user"

    @pytest.mark.asyncio
    async def test_register_without_create_user_method(
        self,
        auth_service: AuthService,
        mock_auth_service: AsyncMock,
    ) -> None:
        """Test registration when auth service doesn't have create_user method."""
        # Remove create_user method from mock
        del mock_auth_service.create_user

        result = await auth_service.register(
            "testuser",
            "test@example.com",
            "password123",
        )

        assert result.is_success
        data = result.unwrap()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert data["message"] == "User created successfully"

    @pytest.mark.asyncio
    async def test_register_with_custom_role(
        self,
        auth_service: AuthService,
        mock_auth_service: AsyncMock,
    ) -> None:
        """Test registration with custom role."""
        mock_user_data = Mock()
        mock_user_data.roles = ["admin"]

        mock_auth_service.create_user.return_value = ServiceResult.ok(mock_user_data)

        result = await auth_service.register(
            "admin_user",
            "admin@example.com",
            "password123",
            "admin",
        )

        assert result.is_success
        data = result.unwrap()
        assert data["role"] == "admin"

        # Verify role was passed to auth service
        call_args = mock_auth_service.create_user.call_args
        assert call_args.kwargs["role"] == "admin"

    @pytest.mark.asyncio
    async def test_register_failure(
        self,
        auth_service: AuthService,
        mock_auth_service: AsyncMock,
    ) -> None:
        """Test registration failure."""
        mock_auth_service.create_user.return_value = ServiceResult.fail(
            "Username already exists",
        )

        result = await auth_service.register(
            "existing_user",
            "test@example.com",
            "password123",
        )

        assert not result.is_success
        assert result.error is not None
        assert "Username already exists" in result.error

    @pytest.mark.asyncio
    async def test_validate_token_success(
        self,
        auth_service: AuthService,
        mock_session_manager: AsyncMock,
    ) -> None:
        """Test successful token validation."""
        token_data = {
            "username": "testuser",
            "roles": ["user"],
            "is_active": True,
            "is_admin": False,
        }

        mock_session_manager.validate_token.return_value = ServiceResult.ok(token_data)

        result = await auth_service.validate_token("valid_token")

        assert result.is_success
        user = result.unwrap()
        assert isinstance(user, UserAPI)
        assert user.username == "testuser"
        assert user.roles == ["user"]
        assert user.is_active is True
        assert user.is_admin is False

    @pytest.mark.asyncio
    async def test_validate_token_invalid(
        self,
        auth_service: AuthService,
        mock_session_manager: AsyncMock,
    ) -> None:
        """Test validation with invalid token."""
        mock_session_manager.validate_token.return_value = ServiceResult.fail(
            "Token expired",
        )

        result = await auth_service.validate_token("invalid_token")

        assert not result.is_success
        assert result.error is not None
        assert "Invalid token" in result.error

    @pytest.mark.asyncio
    async def test_login_exception_handling(
        self,
        auth_service: AuthService,
        mock_auth_service: AsyncMock,
    ) -> None:
        """Test login exception handling."""
        mock_auth_service.authenticate_user.side_effect = Exception(
            "Database connection failed",
        )

        result = await auth_service.login("test@example.com", "password123")

        assert not result.is_success
        assert result.error is not None
        assert "Login failed: Database connection failed" in result.error

    @pytest.mark.asyncio
    async def test_logout_exception_handling(
        self,
        auth_service: AuthService,
        mock_session_manager: AsyncMock,
    ) -> None:
        """Test logout exception handling."""
        mock_session_manager.terminate_session.side_effect = Exception(
            "Redis connection failed",
        )

        result = await auth_service.logout("session123")

        assert not result.is_success
        assert result.error is not None
        assert "Logout failed: Redis connection failed" in result.error


class TestPluginService:
    """Test PluginService implementation."""

    @pytest.fixture
    def mock_plugin_repo(self) -> AsyncMock:
        """Create mock plugin repository."""
        mock = AsyncMock()
        mock.save = AsyncMock()
        mock.get = AsyncMock()
        mock.get_by_id = AsyncMock()  # For backward compatibility
        mock.list = AsyncMock()
        mock.delete = AsyncMock()
        return mock

    @pytest.fixture
    def plugin_service(self, mock_plugin_repo: AsyncMock) -> PluginService:
        """Create PluginService instance for testing."""
        return PluginService(mock_plugin_repo)

    @pytest.fixture
    def sample_plugin(self) -> Plugin:
        """Create sample plugin for testing."""
        return Plugin(
            name="test-plugin",
            plugin_type=PluginType.TAP,
            version="1.0.0",
            description="Test plugin",
            enabled=True,
            author="Test Author",
        )

    @pytest.mark.asyncio
    async def test_install_plugin_success(
        self,
        plugin_service: PluginService,
        mock_plugin_repo: AsyncMock,
        sample_plugin: Plugin,
    ) -> None:
        """Test successful plugin installation."""
        mock_plugin_repo.save.return_value = sample_plugin
        mock_plugin_repo.list.return_value = []  # No duplicates

        result = await plugin_service.install_plugin(
            name="test-plugin",
            plugin_type=PluginType.TAP,
            version="1.0.0",
            description="Test plugin",
            author="Test Author",
        )

        assert result.is_success
        plugin = result.unwrap()
        assert plugin.name == "test-plugin"
        assert plugin.plugin_type == PluginType.TAP
        assert plugin.version == "1.0.0"

        mock_plugin_repo.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_install_plugin_with_string_type(
        self,
        plugin_service: PluginService,
        mock_plugin_repo: AsyncMock,
        sample_plugin: Plugin,
    ) -> None:
        """Test plugin installation with string plugin type."""
        mock_plugin_repo.save.return_value = sample_plugin
        mock_plugin_repo.list.return_value = []

        result = await plugin_service.install_plugin(
            name="test-plugin",
            plugin_type="tap",  # String instead of enum
            version="1.0.0",
        )

        assert result.is_success
        plugin = result.unwrap()
        assert plugin.plugin_type == PluginType.TAP

    @pytest.mark.asyncio
    async def test_install_plugin_with_full_config(
        self,
        plugin_service: PluginService,
        mock_plugin_repo: AsyncMock,
    ) -> None:
        """Test plugin installation with full configuration."""
        config = {"input_file": "data.csv", "delimiter": ","}
        capabilities = ["read", "write"]

        # Create a plugin with the expected configuration
        expected_plugin = Plugin(
            name="test-plugin",
            plugin_type=PluginType.TAP,
            version="1.0.0",
            description="Test plugin",
            plugin_config=config,
            author="Test Author",
            repository_url="https://github.com/test/plugin",
            documentation_url="https://docs.test.com",
            capabilities=capabilities,
            enabled=True,
        )

        mock_plugin_repo.save.return_value = expected_plugin
        mock_plugin_repo.list.return_value = []

        result = await plugin_service.install_plugin(
            name="test-plugin",
            plugin_type=PluginType.TAP,
            version="1.0.0",
            description="Test plugin",
            config=config,
            author="Test Author",
            repository_url="https://github.com/test/plugin",
            documentation_url="https://docs.test.com",
            capabilities=capabilities,
        )

        assert result.is_success
        plugin = result.unwrap()
        assert plugin.plugin_config == config
        assert plugin.author == "Test Author"
        assert plugin.repository_url == "https://github.com/test/plugin"
        assert plugin.documentation_url == "https://docs.test.com"
        assert plugin.capabilities == capabilities

    @pytest.mark.asyncio
    async def test_install_plugin_duplicate(
        self,
        plugin_service: PluginService,
        mock_plugin_repo: AsyncMock,
    ) -> None:
        """Test installing duplicate plugin."""
        # Mock existing plugin with same name and version
        existing_plugin = Plugin(
            name="test-plugin",
            version="1.0.0",
            plugin_type=PluginType.TAP,
        )
        mock_plugin_repo.list.return_value = ServiceResult.ok([existing_plugin])

        result = await plugin_service.install_plugin(
            name="test-plugin",
            plugin_type=PluginType.TAP,
            version="1.0.0",
        )

        assert not result.is_success
        assert result.error is not None
        assert "Plugin with same name and version already exists" in result.error

    @pytest.mark.asyncio
    async def test_get_plugin_success(
        self,
        plugin_service: PluginService,
        mock_plugin_repo: AsyncMock,
        sample_plugin: Plugin,
    ) -> None:
        """Test successful plugin retrieval."""
        plugin_id = sample_plugin.id
        mock_plugin_repo.get.return_value = sample_plugin

        result = await plugin_service.get_plugin(plugin_id)

        assert result.is_success
        plugin = result.unwrap()
        assert plugin.name == "test-plugin"

        mock_plugin_repo.get.assert_called_once_with(plugin_id)

    @pytest.mark.asyncio
    async def test_get_plugin_not_found(
        self,
        plugin_service: PluginService,
        mock_plugin_repo: AsyncMock,
    ) -> None:
        """Test getting non-existent plugin."""
        plugin_id = uuid4()
        mock_plugin_repo.get.return_value = None

        result = await plugin_service.get_plugin(plugin_id)

        assert not result.is_success
        assert result.error is not None
        assert "Plugin not found" in result.error

    @pytest.mark.asyncio
    async def test_list_plugins_basic(
        self,
        plugin_service: PluginService,
        mock_plugin_repo: AsyncMock,
    ) -> None:
        """Test basic plugin listing."""
        plugins = [
            Plugin(name="plugin1", plugin_type=PluginType.TAP),
            Plugin(name="plugin2", plugin_type=PluginType.TARGET),
        ]
        mock_plugin_repo.list.return_value = plugins

        result = await plugin_service.list_plugins()

        assert result.is_success
        plugin_list = result.unwrap()
        assert len(plugin_list) == 2
        assert plugin_list[0].name == "plugin1"
        assert plugin_list[1].name == "plugin2"

    @pytest.mark.asyncio
    async def test_list_plugins_with_filters(
        self,
        plugin_service: PluginService,
        mock_plugin_repo: AsyncMock,
    ) -> None:
        """Test plugin listing with filters."""
        plugins = [Plugin(name="tap-plugin", plugin_type=PluginType.TAP, enabled=True)]
        mock_plugin_repo.list.return_value = plugins

        result = await plugin_service.list_plugins(
            plugin_type="tap",
            enabled=True,
            limit=10,
            offset=0,
        )

        assert result.is_success

        # Verify filters were passed to repository
        call_args = mock_plugin_repo.list.call_args
        assert call_args.kwargs["plugin_type"] == "tap"
        assert call_args.kwargs["enabled"] is True
        assert call_args.kwargs["limit"] == 10
        assert call_args.kwargs["offset"] == 0

    @pytest.mark.asyncio
    async def test_update_plugin_success(
        self,
        plugin_service: PluginService,
        mock_plugin_repo: AsyncMock,
        sample_plugin: Plugin,
    ) -> None:
        """Test successful plugin update."""
        plugin_id = sample_plugin.id
        mock_plugin_repo.get.return_value = sample_plugin

        # Create updated plugin
        updated_plugin = Plugin(
            id=sample_plugin.id,
            name="updated-plugin",
            plugin_type=sample_plugin.plugin_type,
            version=sample_plugin.version,
            description="Updated description",
            enabled=False,
        )
        mock_plugin_repo.save.return_value = updated_plugin

        result = await plugin_service.update_plugin(
            plugin_id,
            name="updated-plugin",
            description="Updated description",
            enabled=False,
        )

        assert result.is_success
        plugin = result.unwrap()
        assert plugin.name == "updated-plugin"
        assert plugin.description == "Updated description"
        assert plugin.enabled is False

    @pytest.mark.asyncio
    async def test_update_plugin_not_found(
        self,
        plugin_service: PluginService,
        mock_plugin_repo: AsyncMock,
    ) -> None:
        """Test updating non-existent plugin."""
        plugin_id = uuid4()
        mock_plugin_repo.get.return_value = None

        result = await plugin_service.update_plugin(plugin_id, name="new-name")

        assert not result.is_success
        assert result.error is not None
        assert "Plugin not found" in result.error

    @pytest.mark.asyncio
    async def test_update_plugin_with_config_and_capabilities(
        self,
        plugin_service: PluginService,
        mock_plugin_repo: AsyncMock,
        sample_plugin: Plugin,
    ) -> None:
        """Test updating plugin with config and capabilities."""
        plugin_id = sample_plugin.id
        mock_plugin_repo.get.return_value = sample_plugin
        mock_plugin_repo.save.return_value = sample_plugin

        new_config = {"new_setting": "value"}
        new_capabilities = ["read", "write", "execute"]

        result = await plugin_service.update_plugin(
            plugin_id,
            config=new_config,
            capabilities=new_capabilities,
        )

        assert result.is_success

    @pytest.mark.asyncio
    async def test_uninstall_plugin_success(
        self,
        plugin_service: PluginService,
        mock_plugin_repo: AsyncMock,
        sample_plugin: Plugin,
    ) -> None:
        """Test successful plugin uninstallation."""
        plugin_id = sample_plugin.id
        mock_plugin_repo.get.return_value = sample_plugin
        mock_plugin_repo.delete.return_value = True

        result = await plugin_service.uninstall_plugin(plugin_id)

        assert result.is_success
        data = result.unwrap()
        assert data["uninstalled"] is True
        assert data["plugin_id"] == str(plugin_id)

        mock_plugin_repo.delete.assert_called_once_with(plugin_id)

    @pytest.mark.asyncio
    async def test_uninstall_plugin_not_found(
        self,
        plugin_service: PluginService,
        mock_plugin_repo: AsyncMock,
    ) -> None:
        """Test uninstalling non-existent plugin."""
        plugin_id = uuid4()
        mock_plugin_repo.get.return_value = None

        result = await plugin_service.uninstall_plugin(plugin_id)

        assert not result.is_success
        assert result.error is not None
        assert "Plugin not found" in result.error

    @pytest.mark.asyncio
    async def test_enable_plugin(
        self,
        plugin_service: PluginService,
        mock_plugin_repo: AsyncMock,
        sample_plugin: Plugin,
    ) -> None:
        """Test enabling a plugin."""
        plugin_id = sample_plugin.id
        sample_plugin.enabled = False  # Start disabled
        mock_plugin_repo.get.return_value = sample_plugin

        # Create enabled version
        enabled_plugin = Plugin(
            id=sample_plugin.id,
            name=sample_plugin.name,
            plugin_type=sample_plugin.plugin_type,
            version=sample_plugin.version,
            enabled=True,
        )
        mock_plugin_repo.save.return_value = enabled_plugin

        result = await plugin_service.enable_plugin(plugin_id)

        assert result.is_success
        plugin = result.unwrap()
        assert plugin.enabled is True

    @pytest.mark.asyncio
    async def test_disable_plugin(
        self,
        plugin_service: PluginService,
        mock_plugin_repo: AsyncMock,
        sample_plugin: Plugin,
    ) -> None:
        """Test disabling a plugin."""
        plugin_id = sample_plugin.id
        sample_plugin.enabled = True  # Start enabled
        mock_plugin_repo.get.return_value = sample_plugin

        # Create disabled version
        disabled_plugin = Plugin(
            id=sample_plugin.id,
            name=sample_plugin.name,
            plugin_type=sample_plugin.plugin_type,
            version=sample_plugin.version,
            enabled=False,
        )
        mock_plugin_repo.save.return_value = disabled_plugin

        result = await plugin_service.disable_plugin(plugin_id)

        assert result.is_success
        plugin = result.unwrap()
        assert plugin.enabled is False

    @pytest.mark.asyncio
    async def test_duplicate_check_with_repository_error(
        self,
        plugin_service: PluginService,
        mock_plugin_repo: AsyncMock,
    ) -> None:
        """Test duplicate check handles repository errors gracefully."""
        # Mock repository error during duplicate check
        mock_plugin_repo.list.side_effect = ConnectionError("Database unavailable")
        mock_plugin_repo.save.return_value = Plugin(
            name="test",
            plugin_type=PluginType.TAP,
            version="1.0.0",
        )

        # Should not fail installation due to duplicate check error
        result = await plugin_service.install_plugin(
            name="test-plugin",
            plugin_type=PluginType.TAP,
            version="1.0.0",
        )

        assert (
            result.is_success
        )  # Installation proceeds despite duplicate check failure

    @pytest.mark.asyncio
    async def test_install_plugin_exception_handling(
        self,
        plugin_service: PluginService,
        mock_plugin_repo: AsyncMock,
    ) -> None:
        """Test plugin installation exception handling."""
        mock_plugin_repo.list.return_value = []
        mock_plugin_repo.save.side_effect = Exception("Database error")

        result = await plugin_service.install_plugin(
            name="test-plugin",
            plugin_type=PluginType.TAP,
            version="1.0.0",
        )

        assert not result.is_success
        assert result.error is not None
        assert "Failed to install plugin: Database error" in result.error

    @pytest.mark.asyncio
    async def test_get_plugin_exception_handling(
        self,
        plugin_service: PluginService,
        mock_plugin_repo: AsyncMock,
    ) -> None:
        """Test get plugin exception handling."""
        plugin_id = uuid4()
        mock_plugin_repo.get.side_effect = Exception("Database error")

        result = await plugin_service.get_plugin(plugin_id)

        assert not result.is_success
        assert result.error is not None
        assert "Failed to get plugin: Database error" in result.error

    @pytest.mark.asyncio
    async def test_list_plugins_exception_handling(
        self,
        plugin_service: PluginService,
        mock_plugin_repo: AsyncMock,
    ) -> None:
        """Test list plugins exception handling."""
        mock_plugin_repo.list.side_effect = Exception("Database error")

        result = await plugin_service.list_plugins()

        assert not result.is_success
        assert result.error is not None
        assert "Failed to list plugins: Database error" in result.error

    @pytest.mark.asyncio
    async def test_update_plugin_exception_handling(
        self,
        plugin_service: PluginService,
        mock_plugin_repo: AsyncMock,
    ) -> None:
        """Test update plugin exception handling."""
        plugin_id = uuid4()
        mock_plugin_repo.get.side_effect = Exception("Database error")

        result = await plugin_service.update_plugin(plugin_id, name="new-name")

        assert not result.is_success
        assert result.error is not None
        assert "Failed to get plugin: Database error" in result.error

    @pytest.mark.asyncio
    async def test_uninstall_plugin_exception_handling(
        self,
        plugin_service: PluginService,
        mock_plugin_repo: AsyncMock,
    ) -> None:
        """Test uninstall plugin exception handling."""
        plugin_id = uuid4()
        mock_plugin_repo.get.side_effect = Exception("Database error")

        result = await plugin_service.uninstall_plugin(plugin_id)

        assert not result.is_success
        assert result.error is not None
        assert "Plugin not found" in result.error
