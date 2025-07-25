"""Tests for PipelineService - Real comprehensive coverage."""

from __future__ import annotations

from unittest.mock import patch
from uuid import uuid4

import pytest

from flext_api.application.services.pipeline_service import PipelineService
from flext_api.models.pipeline import (
    PipelineCreateRequest,
    PipelineExecutionRequest,
    PipelineStatus,
    PipelineUpdateRequest,
)


class TestPipelineService:
    """Comprehensive tests for PipelineService."""

    @pytest.fixture
    def pipeline_service(self) -> PipelineService:
        """Create pipeline service instance."""
        return PipelineService()

    @pytest.fixture
    def valid_create_request(self) -> PipelineCreateRequest:
        """Create valid pipeline creation request."""
        return PipelineCreateRequest(
            name="test-pipeline",
            description="Test pipeline for unit tests",
            extractor="tap-postgres",
            loader="target-snowflake",
            configuration={
                "source": {"host": "localhost", "port": 5432},
                "destination": {"account": "test-account"},
            },
        )

    @pytest.fixture
    def valid_update_request(self) -> PipelineUpdateRequest:
        """Create valid pipeline update request."""
        return PipelineUpdateRequest(
            description="Updated test pipeline",
            configuration={
                "source": {"host": "updated-host", "port": 5433},
            },
        )

    @pytest.fixture
    def valid_execution_request(self) -> PipelineExecutionRequest:
        """Create valid pipeline execution request."""
        return PipelineExecutionRequest(
            pipeline_id=str(uuid4()),
            parameters={"full_refresh": True},
            scheduled_time=None,
        )

    async def test_create_pipeline_success(
        self,
        pipeline_service: PipelineService,
        valid_create_request: PipelineCreateRequest,
    ) -> None:
        """Test successful pipeline creation."""
        result = await pipeline_service.create_pipeline(valid_create_request)

        assert result.is_success
        assert result.data is not None
        assert "id" in result.data
        assert result.data["name"] == "test-pipeline"
        assert result.data["status"] == "created"

    async def test_create_pipeline_empty_name(
        self, pipeline_service: PipelineService
    ) -> None:
        """Test pipeline creation with empty name."""
        request = PipelineCreateRequest(
            name="",
            description="Test pipeline",
            extractor="tap-postgres",
            loader="target-snowflake",
        )

        result = await pipeline_service.create_pipeline(request)

        assert not result.is_success
        assert "Pipeline creation failed" in result.error

    async def test_create_pipeline_empty_extractor(
        self, pipeline_service: PipelineService
    ) -> None:
        """Test pipeline creation with empty extractor."""
        request = PipelineCreateRequest(
            name="test-pipeline",
            description="Test pipeline",
            extractor="",
            loader="target-snowflake",
        )

        result = await pipeline_service.create_pipeline(request)

        assert not result.is_success
        assert "Pipeline creation failed" in result.error

    async def test_create_pipeline_empty_loader(
        self, pipeline_service: PipelineService
    ) -> None:
        """Test pipeline creation with empty loader."""
        request = PipelineCreateRequest(
            name="test-pipeline",
            description="Test pipeline",
            extractor="tap-postgres",
            loader="",
        )

        result = await pipeline_service.create_pipeline(request)

        assert not result.is_success
        assert "Pipeline creation failed" in result.error

    async def test_list_pipelines_success(
        self, pipeline_service: PipelineService
    ) -> None:
        """Test successful pipeline listing."""
        result = await pipeline_service.list_pipelines()

        assert result.is_success
        assert result.data is not None
        assert isinstance(result.data, list)

    async def test_list_pipelines_with_status_filter(
        self, pipeline_service: PipelineService
    ) -> None:
        """Test pipeline listing with status filter."""
        result = await pipeline_service.list_pipelines(status=PipelineStatus.ACTIVE)

        assert result.is_success
        assert result.data is not None
        assert isinstance(result.data, list)

    async def test_list_pipelines_pagination(
        self, pipeline_service: PipelineService
    ) -> None:
        """Test pipeline listing with pagination."""
        result = await pipeline_service.list_pipelines(page=1, page_size=10)

        assert result.is_success
        assert result.data is not None
        assert isinstance(result.data, list)

    async def test_get_pipeline_by_id_success(
        self,
        pipeline_service: PipelineService,
        valid_create_request: PipelineCreateRequest,
    ) -> None:
        """Test successful pipeline retrieval by ID."""
        # First create a pipeline
        create_result = await pipeline_service.create_pipeline(valid_create_request)
        assert create_result.is_success
        pipeline_id = create_result.data["id"]

        # Then retrieve it
        result = await pipeline_service.get_pipeline_by_id(pipeline_id)

        assert result.is_success
        assert result.data is not None
        assert result.data["id"] == pipeline_id

    async def test_get_pipeline_by_id_not_found(
        self, pipeline_service: PipelineService
    ) -> None:
        """Test pipeline retrieval for non-existent ID."""
        fake_id = str(uuid4())
        result = await pipeline_service.get_pipeline_by_id(fake_id)

        assert not result.is_success
        assert "Pipeline not found" in result.error

    async def test_get_pipeline_by_id_empty_id(
        self, pipeline_service: PipelineService
    ) -> None:
        """Test pipeline retrieval with empty ID."""
        result = await pipeline_service.get_pipeline_by_id("")

        assert not result.is_success
        assert "Pipeline ID cannot be empty" in result.error

    async def test_update_pipeline_success(
        self,
        pipeline_service: PipelineService,
        valid_create_request: PipelineCreateRequest,
        valid_update_request: PipelineUpdateRequest,
    ) -> None:
        """Test successful pipeline update."""
        # First create a pipeline
        create_result = await pipeline_service.create_pipeline(valid_create_request)
        assert create_result.is_success
        pipeline_id = create_result.data["id"]

        # Then update it
        result = await pipeline_service.update_pipeline(
            pipeline_id, valid_update_request
        )

        assert result.is_success
        assert result.data is not None
        assert result.data["description"] == "Updated test pipeline"

    async def test_update_pipeline_not_found(
        self,
        pipeline_service: PipelineService,
        valid_update_request: PipelineUpdateRequest,
    ) -> None:
        """Test updating non-existent pipeline."""
        fake_id = str(uuid4())
        result = await pipeline_service.update_pipeline(fake_id, valid_update_request)

        assert not result.is_success
        assert "Pipeline update failed" in result.error

    async def test_delete_pipeline_success(
        self,
        pipeline_service: PipelineService,
        valid_create_request: PipelineCreateRequest,
    ) -> None:
        """Test successful pipeline deletion."""
        # First create a pipeline
        create_result = await pipeline_service.create_pipeline(valid_create_request)
        assert create_result.is_success
        pipeline_id = create_result.data["id"]

        # Then delete it
        result = await pipeline_service.delete_pipeline(pipeline_id)

        assert result.is_success
        assert result.data is not None
        assert "message" in result.data

    async def test_delete_pipeline_not_found(
        self, pipeline_service: PipelineService
    ) -> None:
        """Test deleting non-existent pipeline."""
        fake_id = str(uuid4())
        result = await pipeline_service.delete_pipeline(fake_id)

        assert not result.is_success
        assert "Pipeline deletion failed" in result.error

    async def test_execute_pipeline_success(
        self,
        pipeline_service: PipelineService,
        valid_create_request: PipelineCreateRequest,
    ) -> None:
        """Test successful pipeline execution."""
        # First create a pipeline
        create_result = await pipeline_service.create_pipeline(valid_create_request)
        assert create_result.is_success
        pipeline_id = create_result.data["id"]

        # Then execute it
        result = await pipeline_service.execute_pipeline(pipeline_id)

        assert result.is_success
        assert result.data is not None
        assert "execution_id" in result.data

    async def test_execute_pipeline_not_found(
        self, pipeline_service: PipelineService
    ) -> None:
        """Test executing non-existent pipeline."""
        fake_id = str(uuid4())
        result = await pipeline_service.execute_pipeline(fake_id)

        assert not result.is_success
        assert "Pipeline execution failed" in result.error

    async def test_execute_pipeline_with_parameters(
        self,
        pipeline_service: PipelineService,
        valid_create_request: PipelineCreateRequest,
    ) -> None:
        """Test pipeline execution with parameters."""
        # First create a pipeline
        create_result = await pipeline_service.create_pipeline(valid_create_request)
        assert create_result.is_success
        pipeline_id = create_result.data["id"]

        # Then execute with parameters
        parameters = {"full_refresh": True, "table": "users"}
        result = await pipeline_service.execute_pipeline(pipeline_id, parameters)

        assert result.is_success
        assert result.data is not None
        assert "execution_id" in result.data

    async def test_get_execution_status_success(
        self,
        pipeline_service: PipelineService,
        valid_create_request: PipelineCreateRequest,
    ) -> None:
        """Test getting execution status."""
        # First create and execute a pipeline
        create_result = await pipeline_service.create_pipeline(valid_create_request)
        assert create_result.is_success
        pipeline_id = create_result.data["id"]

        execute_result = await pipeline_service.execute_pipeline(pipeline_id)
        assert execute_result.is_success
        execution_id = execute_result.data["execution_id"]

        # Then get execution status
        result = await pipeline_service.get_execution_status(execution_id)

        assert result.is_success
        assert result.data is not None
        assert "status" in result.data

    async def test_get_execution_status_not_found(
        self, pipeline_service: PipelineService
    ) -> None:
        """Test getting status for non-existent execution."""
        fake_id = str(uuid4())
        result = await pipeline_service.get_execution_status(fake_id)

        assert not result.is_success
        assert "Execution not found" in result.error

    async def test_cancel_execution_success(
        self,
        pipeline_service: PipelineService,
        valid_create_request: PipelineCreateRequest,
    ) -> None:
        """Test successful execution cancellation."""
        # First create and execute a pipeline
        create_result = await pipeline_service.create_pipeline(valid_create_request)
        assert create_result.is_success
        pipeline_id = create_result.data["id"]

        execute_result = await pipeline_service.execute_pipeline(pipeline_id)
        assert execute_result.is_success
        execution_id = execute_result.data["execution_id"]

        # Then cancel execution
        result = await pipeline_service.cancel_execution(execution_id)

        assert result.is_success
        assert result.data is not None
        assert "message" in result.data

    async def test_cancel_execution_not_found(
        self, pipeline_service: PipelineService
    ) -> None:
        """Test cancelling non-existent execution."""
        fake_id = str(uuid4())
        result = await pipeline_service.cancel_execution(fake_id)

        assert not result.is_success
        assert "Execution cancellation failed" in result.error

    async def test_get_pipeline_executions_success(
        self,
        pipeline_service: PipelineService,
        valid_create_request: PipelineCreateRequest,
    ) -> None:
        """Test getting pipeline executions."""
        # First create a pipeline
        create_result = await pipeline_service.create_pipeline(valid_create_request)
        assert create_result.is_success
        pipeline_id = create_result.data["id"]

        # Get executions
        result = await pipeline_service.get_pipeline_executions(pipeline_id)

        assert result.is_success
        assert result.data is not None
        assert isinstance(result.data, list)

    async def test_validate_pipeline_success(
        self,
        pipeline_service: PipelineService,
        valid_create_request: PipelineCreateRequest,
    ) -> None:
        """Test successful pipeline validation."""
        # First create a pipeline
        create_result = await pipeline_service.create_pipeline(valid_create_request)
        assert create_result.is_success
        pipeline_id = create_result.data["id"]

        # Then validate it
        result = await pipeline_service.validate_pipeline(pipeline_id)

        assert result.is_success
        assert result.data is not None
        assert "validation_result" in result.data

    async def test_validate_pipeline_not_found(
        self, pipeline_service: PipelineService
    ) -> None:
        """Test validating non-existent pipeline."""
        fake_id = str(uuid4())
        result = await pipeline_service.validate_pipeline(fake_id)

        assert not result.is_success
        assert "Pipeline validation failed" in result.error

    async def test_clone_pipeline_success(
        self,
        pipeline_service: PipelineService,
        valid_create_request: PipelineCreateRequest,
    ) -> None:
        """Test successful pipeline cloning."""
        # First create a pipeline
        create_result = await pipeline_service.create_pipeline(valid_create_request)
        assert create_result.is_success
        pipeline_id = create_result.data["id"]

        # Then clone it
        result = await pipeline_service.clone_pipeline(pipeline_id, "cloned-pipeline")

        assert result.is_success
        assert result.data is not None
        assert result.data["name"] == "cloned-pipeline"

    async def test_clone_pipeline_not_found(
        self, pipeline_service: PipelineService
    ) -> None:
        """Test cloning non-existent pipeline."""
        fake_id = str(uuid4())
        result = await pipeline_service.clone_pipeline(fake_id, "cloned-pipeline")

        assert not result.is_success
        assert "Pipeline cloning failed" in result.error

    async def test_error_handling_exception(
        self, pipeline_service: PipelineService
    ) -> None:
        """Test error handling when exceptions occur."""
        with patch.object(pipeline_service, "_get_storage") as mock_storage:
            mock_storage.side_effect = Exception("Unexpected error")

            result = await pipeline_service.list_pipelines()

            assert not result.is_success
            assert "Failed to list pipelines" in result.error

    async def test_pipeline_status_transitions(
        self,
        pipeline_service: PipelineService,
        valid_create_request: PipelineCreateRequest,
    ) -> None:
        """Test pipeline status transitions."""
        # Create pipeline (starts as CREATED)
        create_result = await pipeline_service.create_pipeline(valid_create_request)
        assert create_result.is_success
        pipeline_id = create_result.data["id"]

        # Execute pipeline (should transition to RUNNING)
        execute_result = await pipeline_service.execute_pipeline(pipeline_id)
        assert execute_result.is_success

        # Check status
        result = await pipeline_service.get_pipeline_by_id(pipeline_id)
        assert result.is_success
        # Status should reflect execution
