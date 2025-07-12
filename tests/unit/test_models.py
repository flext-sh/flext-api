"""Unit tests for API models.

Modern unit tests with full type hints and async support.
"""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from flext_api.domain.entities import PipelineStatus
from flext_api.models.pipeline import PipelineCreateRequest
from flext_api.models.pipeline import PipelineResponse
from flext_api.models.pipeline import PipelineType
from flext_api.models.plugin import PluginInstallRequest


class TestPipelineModels:
    """Test pipeline-related models."""

    def test_pipeline_create_valid(self, sample_pipeline_data: dict) -> None:
        """Test valid pipeline creation."""
        # Adapt sample data to match PipelineCreateRequest fields
        pipeline_data = {
            "name": sample_pipeline_data["name"],
            "description": sample_pipeline_data["description"],
            "extractor": "tap-sample",
            "loader": "target-sample",
            "configuration": sample_pipeline_data.get("config", {}),
        }
        pipeline = PipelineCreateRequest(**pipeline_data)

        assert pipeline.name == sample_pipeline_data["name"]
        assert pipeline.description == sample_pipeline_data["description"]
        assert pipeline.configuration == sample_pipeline_data.get("config", {})

    def test_pipeline_create_missing_required(self) -> None:
        """Test pipeline creation with missing required fields."""
        with pytest.raises(ValidationError) as exc_info:
            PipelineCreateRequest(description="Missing name and required fields")

        errors = exc_info.value.errors()
        # Should fail on missing name, extractor, or loader
        required_fields = {"name", "extractor", "loader"}
        error_fields = {error["loc"][0] for error in errors if error["loc"]}
        assert required_fields.intersection(error_fields)

    def test_pipeline_response_serialization(self, sample_pipeline_data: dict) -> None:
        """Test pipeline response serialization."""
        response = PipelineResponse(
            pipeline_id=uuid4(),
            name=sample_pipeline_data["name"],
            description=sample_pipeline_data["description"],
            pipeline_type=PipelineType.ETL,
            status=PipelineStatus.ACTIVE,
            extractor="tap-sample",
            loader="target-sample",
            environment="dev",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            configuration=sample_pipeline_data.get("config", {}),
        )

        data = response.model_dump()
        assert data["pipeline_id"] is not None
        assert data["name"] == sample_pipeline_data["name"]
        assert data["status"] == "active"
        assert "created_at" in data
        assert "updated_at" in data

    @pytest.mark.parametrize(
        "status",
        [
            PipelineStatus.ACTIVE,
            PipelineStatus.INACTIVE,
            PipelineStatus.FAILED,
            PipelineStatus.RUNNING,
        ],
    )
    def test_pipeline_status_enum(self, status: PipelineStatus) -> None:
        """Test pipeline status enum values."""
        assert status.value in {"active", "inactive", "failed", "running"}


class TestPluginModels:
    """Test plugin-related models."""

    def test_plugin_config_validation(self, sample_plugin_data: dict) -> None:
        """Test plugin install validation."""
        # Adapt sample data to match PluginInstallRequest fields with flext-core standards
        plugin_data = {
            "name": sample_plugin_data["name"],
            "plugin_type": "tap",  # Map to flext-core standard
            "version": sample_plugin_data.get("version"),
        }
        plugin = PluginInstallRequest(**plugin_data)

        assert plugin.name == sample_plugin_data["name"]
        assert plugin.plugin_type == "tap"  # Verify flext-core standard
        assert plugin.version == sample_plugin_data.get("version")

    def test_plugin_config_invalid_type(self, sample_plugin_data: dict) -> None:
        """Test plugin install with invalid type."""
        plugin_data = {
            "name": sample_plugin_data["name"],
            "plugin_type": "invalid-type",
            "version": sample_plugin_data.get("version"),
        }

        with pytest.raises(ValidationError) as exc_info:
            PluginInstallRequest(**plugin_data)

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("plugin_type",) for error in errors)

    def test_plugin_config_optional_fields(self) -> None:
        """Test plugin install with optional fields."""
        plugin = PluginInstallRequest(
            name="minimal-plugin",
            plugin_type="tap",  # Using flext-core standard values
            version="1.0.0",
        )

        assert plugin.configuration == {}  # Default empty dict
        assert plugin.force_reinstall is False  # Default not force
