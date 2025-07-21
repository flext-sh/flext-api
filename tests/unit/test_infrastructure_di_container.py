"""Tests for FLEXT API DI container configuration."""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from flext_api.application.services.auth_service import AuthService
from flext_api.application.services.pipeline_service import PipelineService
from flext_api.application.services.plugin_service import PluginService
from flext_api.application.services.system_service import SystemService
from flext_api.infrastructure.di_container import configure_api_dependencies
from flext_api.infrastructure.repositories.memory_repositories import (
    InMemoryPipelineRepository,
)


@pytest.fixture
def mock_container() -> Mock:
    """Create mock container for testing."""
    container = Mock()
    container.register = Mock()
    container.register_singleton = Mock()
    return container


@pytest.fixture
def mock_settings() -> Mock:
    """Create mock API settings for testing."""
    settings = Mock()
    settings.configure_dependencies = Mock()
    return settings


@patch("flext_api.infrastructure.di_container.get_container")
@patch("flext_api.infrastructure.di_container.get_api_settings")
def test_configure_api_dependencies(
    mock_get_settings: Mock,
    mock_get_container: Mock,
    mock_container: Mock,
    mock_settings: Mock,
) -> None:
    """Test configuring API dependencies."""
    mock_get_container.return_value = mock_container
    mock_get_settings.return_value = mock_settings

    configure_api_dependencies()

    # Verify container was retrieved
    mock_get_container.assert_called_once()
    mock_get_settings.assert_called_once()

    # Verify settings registered
    mock_container.register.assert_called_once_with(type(mock_settings), mock_settings)

    # Verify repository registered as singleton
    mock_container.register_singleton.assert_any_call(
        InMemoryPipelineRepository,
        factory=InMemoryPipelineRepository,
    )

    # Verify auth service registered as singleton
    mock_container.register_singleton.assert_any_call(
        AuthService,
        factory=AuthService,
    )

    # Verify settings dependency configuration called
    mock_settings.configure_dependencies.assert_called_once_with(mock_container)


@patch("flext_api.infrastructure.di_container.get_container")
@patch("flext_api.infrastructure.di_container.get_api_settings")
def test_configure_api_dependencies_imports_services(
    mock_get_settings: Mock,
    mock_get_container: Mock,
    mock_container: Mock,
    mock_settings: Mock,
) -> None:
    """Test that all application services are imported properly."""
    mock_get_container.return_value = mock_container
    mock_get_settings.return_value = mock_settings

    # This should not raise ImportError
    configure_api_dependencies()

    # The function should complete without errors, ensuring all imports work
    assert mock_get_container.called
    assert mock_get_settings.called


@patch("flext_api.infrastructure.di_container.get_container")
@patch("flext_api.infrastructure.di_container.get_api_settings")
def test_configure_api_dependencies_with_exception(
    mock_get_settings: Mock,
    mock_get_container: Mock,
    mock_container: Mock,
    mock_settings: Mock,
) -> None:
    """Test configure dependencies handles exceptions properly."""
    mock_get_container.return_value = mock_container
    mock_get_settings.return_value = mock_settings

    # Make settings.configure_dependencies raise an exception
    mock_settings.configure_dependencies.side_effect = Exception("Configuration error")

    # Should raise the exception
    with pytest.raises(Exception, match="Configuration error"):
        configure_api_dependencies()


@patch("flext_api.infrastructure.di_container.get_container")
@patch("flext_api.infrastructure.di_container.get_api_settings")
def test_configure_api_dependencies_singleton_registrations(
    mock_get_settings: Mock,
    mock_get_container: Mock,
    mock_container: Mock,
    mock_settings: Mock,
) -> None:
    """Test that singleton registrations are made correctly."""
    mock_get_container.return_value = mock_container
    mock_get_settings.return_value = mock_settings

    configure_api_dependencies()

    # Check that register_singleton was called with correct arguments
    calls = mock_container.register_singleton.call_args_list

    # Should have at least 2 singleton registrations (repository and auth service)
    assert len(calls) >= 2

    # Verify InMemoryPipelineRepository registration
    repo_call = calls[0]
    assert repo_call[0][0] == InMemoryPipelineRepository
    assert repo_call[1]["factory"] == InMemoryPipelineRepository

    # Verify AuthService registration
    auth_call = calls[1]
    assert auth_call[0][0] == AuthService
    assert auth_call[1]["factory"] == AuthService


@patch("flext_api.infrastructure.di_container.get_container")
@patch("flext_api.infrastructure.di_container.get_api_settings")
def test_configure_api_dependencies_service_imports(
    mock_get_settings: Mock,
    mock_get_container: Mock,
    mock_container: Mock,
    mock_settings: Mock,
) -> None:
    """Test that service imports don't fail."""
    mock_get_container.return_value = mock_container
    mock_get_settings.return_value = mock_settings

    # Test that all service classes can be imported and referenced
    services = [AuthService, PipelineService, PluginService, SystemService]

    for service in services:
        assert service is not None
        assert hasattr(service, "__name__")

    # Run configuration
    configure_api_dependencies()

    # Should complete without import errors
    assert mock_get_container.called


def test_auth_service_can_be_imported() -> None:
    """Test that AuthService can be imported correctly."""
    from flext_api.application.services.auth_service import AuthService

    assert AuthService is not None
    assert hasattr(AuthService, "__init__")


def test_pipeline_service_can_be_imported() -> None:
    """Test that PipelineService can be imported correctly."""
    from flext_api.application.services.pipeline_service import PipelineService

    assert PipelineService is not None
    assert hasattr(PipelineService, "__init__")


def test_plugin_service_can_be_imported() -> None:
    """Test that PluginService can be imported correctly."""
    from flext_api.application.services.plugin_service import PluginService

    assert PluginService is not None
    assert hasattr(PluginService, "__init__")


def test_system_service_can_be_imported() -> None:
    """Test that SystemService can be imported correctly."""
    from flext_api.application.services.system_service import SystemService

    assert SystemService is not None
    assert hasattr(SystemService, "__init__")


def test_memory_repository_can_be_imported() -> None:
    """Test that InMemoryPipelineRepository can be imported correctly."""
    from flext_api.infrastructure.repositories.memory_repositories import (
        InMemoryPipelineRepository,
    )

    assert InMemoryPipelineRepository is not None
    assert hasattr(InMemoryPipelineRepository, "__init__")
