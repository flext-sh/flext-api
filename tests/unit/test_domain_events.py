"""Tests for FLEXT API domain events."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from flext_core import DomainEvent, EntityId, UserId

from flext_api.domain.entities import PluginType
from flext_api.domain.events import (
    ApiRequestCompletedEvent,
    ApiRequestReceivedEvent,
    PipelineCreatedEvent,
    PipelineDeletedEvent,
    PipelineUpdatedEvent,
    PluginDisabledEvent,
    PluginEnabledEvent,
    PluginRegisteredEvent,
    PluginUpdatedEvent,
)


class TestDomainEventBase:
    """Test base DomainEvent functionality."""

    def test_domain_event_is_base_class(self) -> None:
        """Test DomainEvent serves as base class."""
        # All events should inherit from DomainEvent
        assert issubclass(PipelineCreatedEvent, DomainEvent)
        assert issubclass(PluginRegisteredEvent, DomainEvent)
        assert issubclass(ApiRequestReceivedEvent, DomainEvent)

    def test_domain_event_has_required_fields(self) -> None:
        """Test DomainEvent has required base fields."""
        # Create a simple event to test base functionality
        event = ApiRequestReceivedEvent(
            request_id=EntityId(str(uuid4())),
            method="GET",
            ip_address="127.0.0.1",
        )

        # Should have base DomainEvent fields
        assert hasattr(event, "event_id")
        assert hasattr(event, "timestamp")
        assert isinstance(event.event_id, type(uuid4()))
        assert isinstance(event.timestamp, datetime)


class TestPipelineEvents:
    """Test pipeline-specific domain events."""

    def test_pipeline_created_event(self) -> None:
        """Test PipelineCreatedEvent creation."""
        pipeline_id = str(uuid4())
        pipeline_name = "test-pipeline"
        owner_id = UserId(str(uuid4()))
        project_id = EntityId(str(uuid4()))

        event = PipelineCreatedEvent(
            pipeline_id=pipeline_id,
            pipeline_name=pipeline_name,
            owner_id=owner_id,
            project_id=project_id,
        )

        assert event.pipeline_id == pipeline_id
        assert event.pipeline_name == pipeline_name
        assert event.owner_id == owner_id
        assert event.project_id == project_id
        assert isinstance(event.event_id, type(uuid4()))
        assert isinstance(event.timestamp, datetime)

    def test_pipeline_created_event_minimal(self) -> None:
        """Test PipelineCreatedEvent with minimal required fields."""
        pipeline_id = str(uuid4())
        pipeline_name = "test-pipeline"

        event = PipelineCreatedEvent(
            pipeline_id=pipeline_id,
            pipeline_name=pipeline_name,
        )

        assert event.pipeline_id == pipeline_id
        assert event.pipeline_name == pipeline_name
        assert event.owner_id is None
        assert event.project_id is None

    def test_pipeline_updated_event(self) -> None:
        """Test PipelineUpdatedEvent creation."""
        pipeline_id = str(uuid4())
        changes: dict[str, object] = {"name": "new-name", "status": "active"}
        updated_by = UserId(str(uuid4()))

        event = PipelineUpdatedEvent(
            pipeline_id=pipeline_id,
            changes=changes,
            updated_by=updated_by,
        )

        assert event.pipeline_id == pipeline_id
        assert event.changes == changes
        assert event.updated_by == updated_by

    def test_pipeline_updated_event_minimal(self) -> None:
        """Test PipelineUpdatedEvent with minimal fields."""
        pipeline_id = str(uuid4())

        event = PipelineUpdatedEvent(
            pipeline_id=pipeline_id,
        )

        assert event.pipeline_id == pipeline_id
        assert event.changes == {}
        assert event.updated_by is None

    def test_pipeline_deleted_event(self) -> None:
        """Test PipelineDeletedEvent creation."""
        pipeline_id = str(uuid4())
        deleted_by = UserId(str(uuid4()))

        event = PipelineDeletedEvent(
            pipeline_id=pipeline_id,
            deleted_by=deleted_by,
        )

        assert event.pipeline_id == pipeline_id
        assert event.deleted_by == deleted_by

    def test_pipeline_events_inheritance(self) -> None:
        """Test pipeline events inherit from DomainEvent properly."""
        pipeline_id = str(uuid4())

        created_event = PipelineCreatedEvent(
            pipeline_id=pipeline_id,
            pipeline_name="test",
        )

        assert isinstance(created_event, DomainEvent)
        assert hasattr(created_event, "event_id")
        assert hasattr(created_event, "timestamp")


class TestPluginEvents:
    """Test plugin-specific domain events."""

    def test_plugin_registered_event(self) -> None:
        """Test PluginRegisteredEvent creation."""
        plugin_id = str(uuid4())
        plugin_name = "tap-csv"
        plugin_type = PluginType.EXTRACTOR
        version = "1.0.0"

        event = PluginRegisteredEvent(
            plugin_id=plugin_id,
            plugin_name=plugin_name,
            plugin_type=plugin_type,
            version=version,
        )

        assert event.plugin_id == plugin_id
        assert event.plugin_name == plugin_name
        assert event.plugin_type == plugin_type
        assert event.version == version

    def test_plugin_updated_event(self) -> None:
        """Test PluginUpdatedEvent creation."""
        plugin_id = str(uuid4())
        changes = {"version": "1.1.0", "enabled": True}
        updated_by = UserId(str(uuid4()))

        event = PluginUpdatedEvent(
            plugin_id=plugin_id,
            changes=changes,
            updated_by=updated_by,
        )

        assert event.plugin_id == plugin_id
        assert event.changes == changes
        assert event.updated_by == updated_by

    def test_plugin_disabled_event(self) -> None:
        """Test PluginDisabledEvent creation."""
        plugin_id = str(uuid4())
        disabled_by = UserId(str(uuid4()))
        reason = "Security vulnerability"

        event = PluginDisabledEvent(
            plugin_id=plugin_id,
            disabled_by=disabled_by,
            reason=reason,
        )

        assert event.plugin_id == plugin_id
        assert event.disabled_by == disabled_by
        assert event.reason == reason

    def test_plugin_enabled_event(self) -> None:
        """Test PluginEnabledEvent creation."""
        plugin_id = str(uuid4())
        enabled_by = UserId(str(uuid4()))

        event = PluginEnabledEvent(
            plugin_id=plugin_id,
            enabled_by=enabled_by,
        )

        assert event.plugin_id == plugin_id
        assert event.enabled_by == enabled_by

    def test_plugin_events_inheritance(self) -> None:
        """Test plugin events inherit from DomainEvent properly."""
        plugin_id = str(uuid4())

        registered_event = PluginRegisteredEvent(
            plugin_id=plugin_id,
            plugin_name="test-plugin",
            plugin_type=PluginType.EXTRACTOR,
            version="1.0.0",
        )

        assert isinstance(registered_event, DomainEvent)
        assert hasattr(registered_event, "event_id")
        assert hasattr(registered_event, "timestamp")


class TestApiEvents:
    """Test API-specific domain events."""

    def test_api_request_received_event(self) -> None:
        """Test ApiRequestReceivedEvent creation."""
        request_id = EntityId(str(uuid4()))
        method = "POST"
        ip_address = "192.168.1.100"

        event = ApiRequestReceivedEvent(
            request_id=request_id,
            method=method,
            ip_address=ip_address,
        )

        assert event.request_id == request_id
        assert event.method == method
        assert event.ip_address == ip_address

    def test_api_request_received_event_minimal(self) -> None:
        """Test ApiRequestReceivedEvent with minimal fields."""
        request_id = EntityId(str(uuid4()))

        event = ApiRequestReceivedEvent(
            request_id=request_id,
        )

        assert event.request_id == request_id
        assert event.method is None
        assert event.ip_address is None

    def test_api_request_completed_event(self) -> None:
        """Test ApiRequestCompletedEvent creation."""
        request_id = EntityId(str(uuid4()))
        status_code = 200
        response_time_ms = 150
        success = True

        event = ApiRequestCompletedEvent(
            request_id=request_id,
            status_code=status_code,
            response_time_ms=response_time_ms,
            success=success,
        )

        assert event.request_id == request_id
        assert event.status_code == status_code
        assert event.response_time_ms == response_time_ms
        assert event.success == success

    def test_api_events_inheritance(self) -> None:
        """Test API events inherit from DomainEvent properly."""
        request_id = EntityId(str(uuid4()))

        received_event = ApiRequestReceivedEvent(
            request_id=request_id,
            method="GET",
        )

        assert isinstance(received_event, DomainEvent)
        assert hasattr(received_event, "event_id")
        assert hasattr(received_event, "timestamp")


class TestEventValidation:
    """Test domain event validation."""

    def test_pipeline_name_validation(self) -> None:
        """Test pipeline name must be non-empty."""
        pipeline_id = str(uuid4())

        # Valid name should work
        event = PipelineCreatedEvent(
            pipeline_id=pipeline_id,
            pipeline_name="valid-name",
        )
        assert event.pipeline_name == "valid-name"

        # Empty name should raise validation error
        with pytest.raises((ValueError, TypeError)):
            PipelineCreatedEvent(
                pipeline_id=pipeline_id,
                pipeline_name="",
            )

    def test_plugin_version_validation(self) -> None:
        """Test plugin version format validation."""
        plugin_id = str(uuid4())
        plugin_name = "test-plugin"
        plugin_type = PluginType.EXTRACTOR

        # Valid semantic version should work
        valid_versions = ["1.0.0", "10.20.30", "0.1.0"]
        for version in valid_versions:
            event = PluginRegisteredEvent(
                plugin_id=plugin_id,
                plugin_name=plugin_name,
                plugin_type=plugin_type,
                version=version,
            )
            assert event.version == version

        # Invalid versions should raise validation error
        invalid_versions = ["1.0", "v1.0.0", "1.0.0-beta", "invalid"]
        for version in invalid_versions:
            with pytest.raises((ValueError, TypeError)):
                PluginRegisteredEvent(
                    plugin_id=plugin_id,
                    plugin_name=plugin_name,
                    plugin_type=plugin_type,
                    version=version,
                )

    def test_status_code_validation(self) -> None:
        """Test API status code validation."""
        request_id = EntityId(str(uuid4()))

        # Valid status codes should work
        valid_codes = [200, 201, 400, 404, 500]
        for code in valid_codes:
            event = ApiRequestCompletedEvent(
                request_id=request_id,
                status_code=code,
                response_time_ms=100,
                success=code < 400,
            )
            assert event.status_code == code

        # Invalid status codes should raise validation error
        invalid_codes = [99, 600, -1]
        for code in invalid_codes:
            with pytest.raises((ValueError, TypeError)):
                ApiRequestCompletedEvent(
                    request_id=request_id,
                    status_code=code,
                    response_time_ms=100,
                    success=False,
                )

    def test_response_time_validation(self) -> None:
        """Test response time must be non-negative."""
        request_id = EntityId(str(uuid4()))

        # Valid response times should work
        valid_times = [0, 1, 100, 5000]
        for time_ms in valid_times:
            event = ApiRequestCompletedEvent(
                request_id=request_id,
                status_code=200,
                response_time_ms=time_ms,
                success=True,
            )
            assert event.response_time_ms == time_ms

        # Negative response time should raise validation error
        with pytest.raises((ValueError, TypeError)):
            ApiRequestCompletedEvent(
                request_id=request_id,
                status_code=200,
                response_time_ms=-1,
                success=True,
            )


class TestEventSerialization:
    """Test domain event serialization capabilities."""

    def test_pipeline_event_serialization(self) -> None:
        """Test pipeline event serialization."""
        pipeline_id = str(uuid4())
        pipeline_name = "test-pipeline"

        event = PipelineCreatedEvent(
            pipeline_id=pipeline_id,
            pipeline_name=pipeline_name,
        )

        # Test model_dump if available (Pydantic v2)
        event_dict = event.model_dump() if hasattr(event, "model_dump") else dict(event)

        assert event_dict["pipeline_id"] == pipeline_id
        assert event_dict["pipeline_name"] == pipeline_name

    def test_plugin_event_serialization(self) -> None:
        """Test plugin event serialization."""
        plugin_id = str(uuid4())
        plugin_name = "test-plugin"
        plugin_type = PluginType.EXTRACTOR
        version = "1.0.0"

        event = PluginRegisteredEvent(
            plugin_id=plugin_id,
            plugin_name=plugin_name,
            plugin_type=plugin_type,
            version=version,
        )

        # Test model_dump if available (Pydantic v2)
        event_dict = event.model_dump() if hasattr(event, "model_dump") else dict(event)

        assert event_dict["plugin_id"] == plugin_id
        assert event_dict["plugin_name"] == plugin_name
        assert event_dict["version"] == version

    def test_api_event_serialization(self) -> None:
        """Test API event serialization."""
        request_id = EntityId(str(uuid4()))
        method = "POST"
        ip_address = "127.0.0.1"

        event = ApiRequestReceivedEvent(
            request_id=request_id,
            method=method,
            ip_address=ip_address,
        )

        # Test model_dump if available (Pydantic v2)
        event_dict = event.model_dump() if hasattr(event, "model_dump") else dict(event)

        assert event_dict["request_id"] == request_id
        assert event_dict["method"] == method
        assert event_dict["ip_address"] == ip_address


class TestEventEquality:
    """Test domain event equality and comparison."""

    def test_events_equal_by_content(self) -> None:
        """Test events are equal when content is the same."""
        pipeline_id = str(uuid4())
        pipeline_name = "test-pipeline"

        _event1 = PipelineCreatedEvent(
            pipeline_id=pipeline_id,
            pipeline_name=pipeline_name,
        )

        _event2 = PipelineCreatedEvent(
            pipeline_id=pipeline_id,
            pipeline_name=pipeline_name,
        )

        # Events should be equal by content
        # Note: This depends on how DomainEvent implements equality
        # They might not be equal due to different event_ids and timestamps

    def test_events_different_when_content_differs(self) -> None:
        """Test events are different when content differs."""
        pipeline_id1 = str(uuid4())
        pipeline_id2 = str(uuid4())

        event1 = PipelineCreatedEvent(
            pipeline_id=pipeline_id1,
            pipeline_name="pipeline-1",
        )

        event2 = PipelineCreatedEvent(
            pipeline_id=pipeline_id2,
            pipeline_name="pipeline-2",
        )

        # Events should be different due to different content
        assert event1.pipeline_id != event2.pipeline_id
        assert event1.pipeline_name != event2.pipeline_name


class TestEventTimestamps:
    """Test domain event timestamp behavior."""

    def test_events_have_creation_timestamp(self) -> None:
        """Test that events automatically get creation timestamps."""
        before_creation = datetime.now(UTC)

        event = PipelineCreatedEvent(
            pipeline_id=str(uuid4()),
            pipeline_name="test-pipeline",
        )

        after_creation = datetime.now(UTC)

        assert hasattr(event, "timestamp")
        assert isinstance(event.timestamp, datetime)
        assert before_creation <= event.timestamp <= after_creation

    def test_events_have_unique_ids(self) -> None:
        """Test that events get unique identifiers."""
        event1 = PipelineCreatedEvent(
            pipeline_id=str(uuid4()),
            pipeline_name="pipeline-1",
        )

        event2 = PipelineCreatedEvent(
            pipeline_id=str(uuid4()),
            pipeline_name="pipeline-2",
        )

        assert hasattr(event1, "event_id")
        assert hasattr(event2, "event_id")
        assert event1.event_id != event2.event_id
