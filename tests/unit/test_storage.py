"""Tests for FLEXT API storage functionality."""

from __future__ import annotations

import pytest

from flext_api.models.system import AlertSeverity, SystemBackupRequest
from flext_api.storage import FlextAPIStorage


@pytest.fixture
def storage() -> FlextAPIStorage:
    """Create storage instance for testing."""
    return FlextAPIStorage()


def test_storage_initialization(storage: FlextAPIStorage) -> None:
    """Test storage initializes correctly."""
    assert storage.system_status == "healthy"
    assert len(storage.services) == 4
    assert len(storage.plugins) == 3


def test_get_system_status(storage: FlextAPIStorage) -> None:
    """Test getting system status."""
    result = storage.get_system_status()

    # Debug info if test fails
    if not result.is_success:
        # Use pytest to show the error instead of print
        pytest.fail(f"Error: {result.error}")

    assert result.is_success

    status = result.unwrap()
    # SystemStatus enum values should be string
    assert str(status.status) == "healthy"
    assert status.version == "1.0.0"
    assert status.plugin_count == 3


def test_create_alert(storage: FlextAPIStorage) -> None:
    """Test creating system alert."""
    result = storage.create_alert(
        AlertSeverity.INFO,
        "Test Alert",
        "This is a test alert",
    )

    # Debug info if test fails
    if not result.is_success:
        # Use pytest to show the error instead of print
        pytest.fail(f"Error: {result.error}")

    assert result.is_success

    alert = result.unwrap()
    assert alert.title == "Test Alert"
    assert alert.message == "This is a test alert"
    assert alert.severity == AlertSeverity.INFO

    # Alert should be stored
    assert len(storage.alerts) == 1


def test_get_metrics(storage: FlextAPIStorage) -> None:
    """Test getting system metrics."""
    result = storage.get_metrics()

    # Debug info if test fails
    if not result.is_success:
        # Use pytest to show the error instead of print
        pytest.fail(f"Error: {result.error}")

    assert result.is_success

    metrics = result.unwrap()
    assert len(metrics) == 3  # CPU, memory, request count

    metric_names = [m.metric_name for m in metrics]
    assert "cpu_usage" in metric_names
    assert "memory_usage" in metric_names
    assert "request_count" in metric_names


def test_create_backup(storage: FlextAPIStorage) -> None:
    """Test creating system backup."""
    backup_request = SystemBackupRequest(
        backup_type="full",
        description="Test backup",
        encryption=True,
        compression=True,
        metadata={"test": "value"},
    )

    result = storage.create_backup(backup_request)

    # Debug info if test fails
    if not result.is_success:
        # Use pytest to show the error instead of print
        pytest.fail(f"Error: {result.error}")

    assert result.is_success

    backup = result.unwrap()
    assert backup.backup_type == "full"
    assert backup.description == "Test backup"
    assert backup.encrypted is True
    assert backup.status == "completed"

    # Backup should be stored
    assert len(storage.backups) == 1


def test_create_pipeline(storage: FlextAPIStorage) -> None:
    """Test creating pipeline."""
    result = storage.create_pipeline("test-pipeline", "tap-oracle-oic", "target-ldap")
    assert result.is_success

    pipeline = result.unwrap()
    assert pipeline["name"] == "test-pipeline"
    assert pipeline["extractor"] == "tap-oracle-oic"
    assert pipeline["loader"] == "target-ldap"
    assert pipeline["status"] == "created"

    # Pipeline should be stored
    assert len(storage.pipelines) == 1


def test_get_pipeline(storage: FlextAPIStorage) -> None:
    """Test getting pipeline by ID."""
    # First create a pipeline
    create_result = storage.create_pipeline(
        "test-pipeline",
        "tap-oracle-oic",
        "target-ldap",
    )
    pipeline_id = create_result.unwrap()["id"]

    # Now get it
    result = storage.get_pipeline(pipeline_id)
    assert result.is_success

    pipeline = result.unwrap()
    assert pipeline["id"] == pipeline_id
    assert pipeline["name"] == "test-pipeline"


def test_execute_pipeline(storage: FlextAPIStorage) -> None:
    """Test executing pipeline."""
    # First create a pipeline
    create_result = storage.create_pipeline(
        "test-pipeline",
        "tap-oracle-oic",
        "target-ldap",
    )
    pipeline_id = create_result.unwrap()["id"]

    # Now execute it
    result = storage.execute_pipeline(pipeline_id)
    assert result.is_success

    execution = result.unwrap()
    assert execution["pipeline_id"] == pipeline_id
    assert execution["status"] == "running"
    assert "execution_id" in execution

    # Pipeline status should be updated
    pipeline = storage.pipelines[pipeline_id]
    assert pipeline["status"] == "running"

    # Execution should be stored
    assert len(storage.executions) == 1


def test_get_nonexistent_pipeline(storage: FlextAPIStorage) -> None:
    """Test getting nonexistent pipeline."""
    result = storage.get_pipeline("nonexistent-id")
    assert not result.is_success
    assert result.error is not None
    assert "not found" in str(result.error)


def test_execute_nonexistent_pipeline(storage: FlextAPIStorage) -> None:
    """Test executing nonexistent pipeline."""
    result = storage.execute_pipeline("nonexistent-id")
    assert not result.is_success
    assert result.error is not None
    assert "not found" in str(result.error)
