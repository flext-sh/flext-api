"""Tests for FLEXT API infrastructure repository implementations."""

from __future__ import annotations

from typing import Any
from unittest.mock import patch
from uuid import uuid4

import pytest

from flext_api.domain.entities import (
    APIPipeline as Pipeline,
    PipelineStatus,
    Plugin,
    PluginType,
)
from flext_api.infrastructure.repositories.pipeline_repository import (
    InMemoryPipelineRepository,
)


class TestInMemoryPipelineRepository:
    """Test InMemoryPipelineRepository implementation."""

    @pytest.fixture
    def repository(self) -> Any:
        """Create REAL repository instance for testing."""
        # Use the REAL implementation - bypass decorator for testing
        from flext_api.infrastructure.repositories.pipeline_repository import (
            InMemoryPipelineRepository,
        )

        # Get the actual class implementation (bypassing decorator)
        actual_class = (
            InMemoryPipelineRepository.__wrapped__
            if hasattr(InMemoryPipelineRepository, "__wrapped__")
            else InMemoryPipelineRepository
        )

        # Create actual repository instance - NO MOCKS
        return actual_class()

    @pytest.fixture
    def sample_pipeline(self) -> Any:
        """Create sample pipeline for testing."""
        return Pipeline(
            name="test-pipeline",
            description="Test pipeline description",
            pipeline_status=PipelineStatus.ACTIVE,
            endpoint="/api/test",
            owner_id=None,  # Simplified to avoid Pydantic forward reference issues
            project_id=None,
        )

    def test_repository_initialization(self, repository: Any) -> None:
        """Test repository initializes correctly."""
        assert repository._pipelines == {}

    @pytest.mark.asyncio
    async def test_save_pipeline(self, repository: Any, sample_pipeline: Any) -> None:
        """Test saving pipeline to repository."""
        result = await repository.save(sample_pipeline)

        assert result.success
        assert result.data == sample_pipeline
        assert sample_pipeline.id in repository._pipelines
        assert repository._pipelines[sample_pipeline.id] == sample_pipeline

    @pytest.mark.asyncio
    async def test_get_pipeline_by_id(
        self,
        repository: Any,
        sample_pipeline: Any,
    ) -> None:
        """Test getting pipeline by ID."""
        # Save pipeline first
        await repository.save(sample_pipeline)

        # Get by ID
        result = await repository.get(sample_pipeline.id)
        assert result.success
        assert result.data == sample_pipeline

        # Get non-existing pipeline
        non_existing_id = uuid4()
        result = await repository.get(non_existing_id)
        assert not result.success

    @pytest.mark.asyncio
    async def test_list_pipelines_basic(self, repository: Any) -> None:
        """Test listing pipelines with basic functionality."""
        # Create multiple pipelines
        pipeline1 = Pipeline(name="pipeline-1", pipeline_status=PipelineStatus.ACTIVE)
        pipeline2 = Pipeline(name="pipeline-2", pipeline_status=PipelineStatus.INACTIVE)
        pipeline3 = Pipeline(name="pipeline-3", pipeline_status=PipelineStatus.RUNNING)

        await repository.save(pipeline1)
        await repository.save(pipeline2)
        await repository.save(pipeline3)

        # List all pipelines
        result = await repository.list()
        assert result.success
        pipelines = result.data
        assert len(pipelines) == 3

        # Pipelines should be sorted by created_at descending
        assert pipelines[0].name == "pipeline-3"  # Last created
        assert pipelines[2].name == "pipeline-1"  # First created

    @pytest.mark.asyncio
    async def test_list_pipelines_with_owner_filter(self, repository: Any) -> None:
        """Test listing pipelines filtered by owner."""
        owner1 = uuid4()
        owner2 = uuid4()

        pipeline1 = Pipeline(name="pipeline-1", owner_id=owner1)
        pipeline2 = Pipeline(name="pipeline-2", owner_id=owner2)
        pipeline3 = Pipeline(name="pipeline-3", owner_id=owner1)

        await repository.save(pipeline1)
        await repository.save(pipeline2)
        await repository.save(pipeline3)

        # Filter by owner1
        result = await repository.list(owner_id=owner1)
        assert result.success
        pipelines = result.data
        assert len(pipelines) == 2
        assert all(p.owner_id == owner1 for p in pipelines)

    @pytest.mark.asyncio
    async def test_list_pipelines_with_project_filter(self, repository: Any) -> None:
        """Test listing pipelines filtered by project."""
        project1 = uuid4()
        project2 = uuid4()

        pipeline1 = Pipeline(name="pipeline-1", project_id=project1)
        pipeline2 = Pipeline(name="pipeline-2", project_id=project2)
        pipeline3 = Pipeline(name="pipeline-3", project_id=project1)

        await repository.save(pipeline1)
        await repository.save(pipeline2)
        await repository.save(pipeline3)

        # Filter by project1
        result = await repository.list(project_id=project1)
        assert result.success
        pipelines = result.data
        assert len(pipelines) == 2
        assert all(p.project_id == project1 for p in pipelines)

    @pytest.mark.asyncio
    async def test_list_pipelines_with_status_filter(self, repository: Any) -> None:
        """Test listing pipelines filtered by status."""
        pipeline1 = Pipeline(name="pipeline-1", pipeline_status=PipelineStatus.ACTIVE)
        pipeline2 = Pipeline(name="pipeline-2", pipeline_status=PipelineStatus.RUNNING)
        pipeline3 = Pipeline(name="pipeline-3", pipeline_status=PipelineStatus.ACTIVE)

        await repository.save(pipeline1)
        await repository.save(pipeline2)
        await repository.save(pipeline3)

        # Filter by ACTIVE status
        result = await repository.list(status="active")
        assert result.success
        pipelines = result.data
        assert len(pipelines) == 2
        assert all(p.pipeline_status == PipelineStatus.ACTIVE for p in pipelines)

    @pytest.mark.asyncio
    async def test_list_pipelines_with_invalid_status_filter(
        self,
        repository: Any,
    ) -> None:
        """Test listing pipelines with invalid status filter."""
        pipeline1 = Pipeline(name="pipeline-1", pipeline_status=PipelineStatus.ACTIVE)
        await repository.save(pipeline1)

        # Use invalid status - should return empty list (no pipelines match invalid status)
        result = await repository.list(status="invalid_status")
        assert result.success
        pipelines = result.data or []
        assert len(pipelines) == 0  # No pipelines match invalid status

    @pytest.mark.asyncio
    async def test_list_pipelines_with_pagination(self, repository: Any) -> None:
        """Test listing pipelines with pagination."""
        # Create 5 pipelines
        for i in range(5):
            pipeline = Pipeline(name=f"pipeline-{i}")
            await repository.save(pipeline)

        # Get first 2 pipelines
        result = await repository.list(limit=2, offset=0)
        assert result.success
        pipelines = result.data
        assert len(pipelines) == 2

        # Get next 2 pipelines
        result = await repository.list(limit=2, offset=2)
        assert result.success
        pipelines = result.data
        assert len(pipelines) == 2

        # Get last pipeline
        result = await repository.list(limit=2, offset=4)
        assert result.success
        pipelines = result.data
        assert len(pipelines) == 1

    @pytest.mark.asyncio
    async def test_delete_pipeline(self, repository: Any, sample_pipeline: Any) -> None:
        """Test deleting pipeline from repository."""
        # Save pipeline first
        await repository.save(sample_pipeline)
        assert sample_pipeline.id in repository._pipelines

        # Delete pipeline
        result = await repository.delete(sample_pipeline.id)
        assert result.success
        assert result.data is True
        assert sample_pipeline.id not in repository._pipelines

        # Try to delete non-existing pipeline
        non_existing_id = uuid4()
        result = await repository.delete(non_existing_id)
        assert not result.success

    @pytest.mark.asyncio
    async def test_count_pipelines(self, repository: Any) -> None:
        """Test counting pipelines in repository."""
        # Initially empty
        count_result = await repository.count()
        assert count_result.success
        assert count_result.data == 0

        # Add some pipelines
        for i in range(3):
            pipeline = Pipeline(name=f"pipeline-{i}")
            await repository.save(pipeline)

        count_result = await repository.count()
        assert count_result.success
        assert count_result.data == 3


class TestInMemoryPluginRepository:
    """Test InMemoryPluginRepository implementation."""

    @pytest.fixture
    def repository(self) -> Any:
        """Create repository instance for testing."""
        # Import the actual implementation from infrastructure
        from flext_api.infrastructure.repositories.plugin_repository import (
            InMemoryPluginRepository,
        )

        return InMemoryPluginRepository()

    @pytest.fixture
    def sample_plugin(self) -> Any:
        """Create sample plugin for testing."""
        return Plugin(
            name="test-plugin",
            plugin_type=PluginType.TAP,
            version="1.0.0",
            description="Test plugin description",
            author="Test Author",
            enabled=True,
        )

    def test_repository_initialization(self, repository: Any) -> None:
        """Test repository initializes correctly."""
        assert repository._storage == {}

    @pytest.mark.asyncio
    async def test_save_plugin(self, repository: Any, sample_plugin: Any) -> None:
        """Test saving plugin to repository."""
        result = await repository.save(sample_plugin)

        assert result.success
        assert result.data == sample_plugin
        assert sample_plugin.id in repository._storage
        assert repository._storage[sample_plugin.id] == sample_plugin

    @pytest.mark.asyncio
    async def test_get_plugin_by_id(self, repository: Any, sample_plugin: Any) -> None:
        """Test getting plugin by ID."""
        # Save plugin first
        await repository.save(sample_plugin)

        # Get by ID
        result = await repository.get(sample_plugin.id)
        assert result.success
        assert result.data == sample_plugin

        # Get non-existing plugin
        non_existing_id = uuid4()
        result = await repository.get(non_existing_id)
        assert not result.success

    @pytest.mark.asyncio
    async def test_get_plugin_by_name(
        self,
        repository: Any,
        sample_plugin: Any,
    ) -> None:
        """Test getting plugin by name."""
        # Save plugin first
        await repository.save(sample_plugin)

        # Get by name (using find_by_name method)
        result = await repository.find_by_name(sample_plugin.name)
        assert result == sample_plugin

        # Get non-existing plugin
        result = await repository.find_by_name("non-existing-plugin")
        assert result is None

    @pytest.mark.asyncio
    async def test_list_plugins_basic(self, repository: Any) -> None:
        """Test listing plugins with basic functionality."""
        # Create multiple plugins
        plugin1 = Plugin(name="plugin-a", plugin_type=PluginType.TAP)
        plugin2 = Plugin(name="plugin-b", plugin_type=PluginType.TARGET)
        plugin3 = Plugin(name="plugin-c", plugin_type=PluginType.TRANSFORM)

        await repository.save(plugin1)
        await repository.save(plugin2)
        await repository.save(plugin3)

        # List all plugins
        result = await repository.list()
        assert result.success
        plugins = result.data or []
        assert len(plugins) == 3

        # Plugins should be sorted by name
        assert plugins[0].name == "plugin-a"
        assert plugins[1].name == "plugin-b"
        assert plugins[2].name == "plugin-c"

    @pytest.mark.asyncio
    async def test_list_plugins_with_type_filter(self, repository: Any) -> None:
        """Test listing plugins filtered by type."""
        plugin1 = Plugin(name="plugin-1", plugin_type=PluginType.TAP)
        plugin2 = Plugin(name="plugin-2", plugin_type=PluginType.TARGET)
        plugin3 = Plugin(name="plugin-3", plugin_type=PluginType.TAP)

        await repository.save(plugin1)
        await repository.save(plugin2)
        await repository.save(plugin3)

        # Filter by TAP type
        result = await repository.list(plugin_type="tap")
        assert result.success
        plugins = result.data or []
        assert len(plugins) == 2
        assert all(p.plugin_type == PluginType.TAP for p in plugins)

    @pytest.mark.asyncio
    async def test_list_plugins_with_enabled_filter(self, repository: Any) -> None:
        """Test listing plugins filtered by enabled status."""
        plugin1 = Plugin(name="plugin-1", enabled=True)
        plugin2 = Plugin(name="plugin-2", enabled=False)
        plugin3 = Plugin(name="plugin-3", enabled=True)

        await repository.save(plugin1)
        await repository.save(plugin2)
        await repository.save(plugin3)

        # Repository doesn't support enabled filtering in its interface,
        # so we test by listing all and manually filtering
        result = await repository.list()
        assert result.success
        plugins = result.data or []

        # Filter manually for enabled status
        enabled_plugins = [p for p in plugins if p.enabled is True]
        disabled_plugins = [p for p in plugins if p.enabled is False]
        assert len(enabled_plugins) == 2
        assert len(disabled_plugins) == 1
        assert all(p.enabled is True for p in enabled_plugins)
        assert disabled_plugins[0].enabled is False

    @pytest.mark.asyncio
    async def test_list_plugins_with_pagination(self, repository: Any) -> None:
        """Test listing plugins with pagination."""
        # Create 5 plugins
        for i in range(5):
            plugin = Plugin(name=f"plugin-{i:02d}")  # Zero-padded for proper sorting
            await repository.save(plugin)

        # Get first 2 plugins
        result = await repository.list(limit=2, offset=0)
        assert result.success
        plugins = result.data or []
        assert len(plugins) == 2

        # Get next 2 plugins
        result = await repository.list(limit=2, offset=2)
        assert result.success
        plugins = result.data or []
        assert len(plugins) == 2

        # Get last plugin
        result = await repository.list(limit=2, offset=4)
        assert result.success
        plugins = result.data or []
        assert len(plugins) == 1

    @pytest.mark.asyncio
    async def test_list_plugins_with_multiple_filters(self, repository: Any) -> None:
        """Test listing plugins with multiple filters."""
        plugin1 = Plugin(name="plugin-1", plugin_type=PluginType.TAP, enabled=True)
        plugin2 = Plugin(name="plugin-2", plugin_type=PluginType.TAP, enabled=False)
        plugin3 = Plugin(name="plugin-3", plugin_type=PluginType.TARGET, enabled=True)

        await repository.save(plugin1)
        await repository.save(plugin2)
        await repository.save(plugin3)

        # Filter by TAP type only (repository doesn't support enabled filtering)
        result = await repository.list(plugin_type="tap")
        assert result.success
        plugins = result.data or []

        # Filter manually for enabled status since repository doesn't support it
        tap_enabled_plugins = [p for p in plugins if p.enabled is True]
        assert len(tap_enabled_plugins) == 1
        assert tap_enabled_plugins[0].name == "plugin-1"

    @pytest.mark.asyncio
    async def test_delete_plugin(self, repository: Any, sample_plugin: Any) -> None:
        """Test deleting plugin from repository."""
        # Save plugin first
        await repository.save(sample_plugin)
        assert sample_plugin.id in repository._storage

        # Delete plugin
        result = await repository.delete(sample_plugin.id)
        assert result.success
        assert result.data is True
        assert sample_plugin.id not in repository._storage

        # Try to delete non-existing plugin
        non_existing_id = uuid4()
        result = await repository.delete(non_existing_id)
        assert not result.success

    @pytest.mark.asyncio
    async def test_count_plugins(self, repository: Any) -> None:
        """Test counting plugins in repository."""
        # Initially empty
        count_result = await repository.count()
        assert count_result.success
        assert count_result.data == 0

        # Add some plugins
        for i in range(3):
            plugin = Plugin(name=f"plugin-{i}")
            await repository.save(plugin)

        count_result = await repository.count()
        assert count_result.success
        assert count_result.data == 3

    @pytest.mark.asyncio
    async def test_repository_independence(self) -> None:
        """Test that repository instances are independent."""
        from flext_api.infrastructure.repositories.plugin_repository import (
            InMemoryPluginRepository,
        )

        repo1 = InMemoryPluginRepository()
        repo2 = InMemoryPluginRepository()

        plugin1 = Plugin(name="plugin-1", version="1.0.0", plugin_type=PluginType.TAP)
        plugin2 = Plugin(
            name="plugin-2",
            version="1.0.0",
            plugin_type=PluginType.TARGET,
        )

        await repo1.save(plugin1)
        await repo2.save(plugin2)

        # Each repository should have only its own plugin
        count1_result = await repo1.count()
        count2_result = await repo2.count()
        assert count1_result.success
        assert count1_result.data == 1
        assert count2_result.success
        assert count2_result.data == 1

        # Note: get_by_name_and_version method does not exist in interface
        # Using list() with filters would be the appropriate interface method
        plugins1_result = await repo1.list()
        plugins2_result = await repo2.list()

        assert plugins1_result.success
        assert plugins2_result.success

        # Check that each repo contains only its own plugin
        plugins1 = plugins1_result.data or []
        plugins2 = plugins2_result.data or []

        plugin1_names = [p.name for p in plugins1]
        plugin2_names = [p.name for p in plugins2]

        assert "plugin-1" in plugin1_names
        assert "plugin-2" not in plugin1_names
        assert "plugin-2" in plugin2_names
        assert "plugin-1" not in plugin2_names


class TestRepositoryLogging:
    """Test repository logging functionality."""

    @pytest.mark.asyncio
    async def test_pipeline_repository_logging(self) -> None:
        """Test pipeline repository logs operations correctly."""
        # Use the REAL implementation directly - bypass decorator if present
        actual_class = (
            InMemoryPipelineRepository.__wrapped__
            if hasattr(InMemoryPipelineRepository, "__wrapped__")
            else InMemoryPipelineRepository
        )
        repository = actual_class()
        pipeline = Pipeline(name="test-pipeline")

        with patch(
            "flext_api.infrastructure.repositories.pipeline_repository.logger",
        ) as mock_logger:
            await repository.save(pipeline)

            mock_logger.info.assert_called_once_with(
                "Created pipeline: %s",
                pipeline.id,
            )

    @pytest.mark.asyncio
    async def test_plugin_repository_logging(self) -> None:
        """Test plugin repository logs operations correctly."""
        from flext_api.infrastructure.repositories.plugin_repository import (
            InMemoryPluginRepository,
        )

        repository = InMemoryPluginRepository()
        plugin = Plugin(name="test-plugin", plugin_type=PluginType.TAP)

        with patch(
            "flext_api.infrastructure.repositories.plugin_repository.logger",
        ) as mock_logger:
            await repository.save(plugin)

            mock_logger.info.assert_called_once_with(
                "Plugin created successfully: %s",
                plugin.name,
            )

    @pytest.mark.asyncio
    async def test_pipeline_delete_logging(self) -> None:
        """Test pipeline repository logs delete operations correctly."""
        # Use the REAL implementation directly - bypass decorator if present
        actual_class = (
            InMemoryPipelineRepository.__wrapped__
            if hasattr(InMemoryPipelineRepository, "__wrapped__")
            else InMemoryPipelineRepository
        )
        repository = actual_class()
        pipeline = Pipeline(name="test-pipeline")

        await repository.save(pipeline)

        with patch(
            "flext_api.infrastructure.repositories.pipeline_repository.logger",
        ) as mock_logger:
            await repository.delete(pipeline.id)

            mock_logger.info.assert_called_once_with(
                "Deleted pipeline: %s",
                pipeline.id,
            )

    @pytest.mark.asyncio
    async def test_plugin_delete_logging(self) -> None:
        """Test plugin repository logs delete operations correctly."""
        from flext_api.infrastructure.repositories.plugin_repository import (
            InMemoryPluginRepository,
        )

        repository = InMemoryPluginRepository()
        plugin = Plugin(name="test-plugin")

        await repository.save(plugin)

        with patch(
            "flext_api.infrastructure.repositories.plugin_repository.logger",
        ) as mock_logger:
            await repository.delete(plugin.id)

            mock_logger.info.assert_called_once_with(
                "Plugin deleted successfully: %s",
                plugin.name,
            )
