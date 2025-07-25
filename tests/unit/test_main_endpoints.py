"""Tests for main application endpoints exposed directly in main.py."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from flext_api.main import app


@pytest.fixture
def client() -> TestClient:
    """Create test client for main app endpoints."""
    return TestClient(app)


# Health endpoints tests
def test_health_check_endpoint(client: TestClient) -> None:
    """Test health check endpoint."""
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "healthy"
    assert "timestamp" in data
    # Verify timestamp format (ISO format)
    assert "T" in data["timestamp"]
    # Accept both Z and +00:00 timezone formats
    assert data["timestamp"].endswith("Z") or data["timestamp"].endswith("+00:00")


def test_readiness_check_endpoint(client: TestClient) -> None:
    """Test Kubernetes readiness probe endpoint."""
    response = client.get("/health/ready")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ready"
    assert "timestamp" in data
    # Verify timestamp format (ISO format)
    assert "T" in data["timestamp"]
    # Accept both Z and +00:00 timezone formats
    assert data["timestamp"].endswith("Z") or data["timestamp"].endswith("+00:00")


# Pipeline endpoints tests
def test_list_pipelines_endpoint_empty(client: TestClient) -> None:
    """Test list pipelines endpoint when no pipelines exist."""
    response = client.get("/api/v1/pipelines")

    assert response.status_code == 200
    data = response.json()

    assert "pipelines" in data
    assert "total_count" in data
    assert isinstance(data["pipelines"], list)
    assert data["total_count"] == len(data["pipelines"])


def test_create_pipeline_endpoint(client: TestClient) -> None:
    """Test create pipeline endpoint."""
    # Use JSON body as the endpoint expects
    response = client.post(
        "/api/v1/pipelines",
        json={
            "name": "test-pipeline",
            "extractor": "tap-postgresql",
            "loader": "target-jsonl",
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert "pipeline_id" in data
    assert data["name"] == "test-pipeline"
    assert data["extractor"] == "tap-postgresql"
    assert data["loader"] == "target-jsonl"
    assert (
        data["pipeline_status"] == "active"
    )  # FlextAPIPipeline default status is ACTIVE
    assert "created_at" in data
    assert "configuration" in data
    # Pipeline response includes execution tracking fields


def test_create_pipeline_with_special_characters(client: TestClient) -> None:
    """Test create pipeline with special characters in name."""
    response = client.post(
        "/api/v1/pipelines",
        json={
            "name": "test-pipeline_v2-final",
            "extractor": "tap-mysql",
            "loader": "target-postgres",
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["name"] == "test-pipeline_v2-final"
    assert data["extractor"] == "tap-mysql"
    assert data["loader"] == "target-postgres"


def test_list_pipelines_after_creation(client: TestClient) -> None:
    """Test list pipelines after creating some."""
    # Create a pipeline first
    create_response = client.post(
        "/api/v1/pipelines",
        json={
            "name": "listed-pipeline",
            "extractor": "tap-csv",
            "loader": "target-sqlite",
        },
    )
    assert create_response.status_code == 200

    # Now list pipelines
    list_response = client.get("/api/v1/pipelines")

    assert list_response.status_code == 200
    data = list_response.json()

    assert data["total_count"] >= 1
    assert len(data["pipelines"]) >= 1

    # Find our created pipeline
    pipeline_names = [p["name"] for p in data["pipelines"]]
    assert "listed-pipeline" in pipeline_names


def test_get_pipeline_endpoint(client: TestClient) -> None:
    """Test get specific pipeline endpoint."""
    # First create a pipeline
    create_response = client.post(
        "/api/v1/pipelines",
        json={
            "name": "get-test-pipeline",
            "extractor": "tap-oracle",
            "loader": "target-oracle",
        },
    )
    assert create_response.status_code == 200
    created_pipeline = create_response.json()
    pipeline_id = created_pipeline["pipeline_id"]

    # Now get the pipeline
    response = client.get(f"/api/v1/pipelines/{pipeline_id}")

    assert response.status_code == 200
    data = response.json()

    assert data["pipeline_id"] == pipeline_id
    assert data["name"] == "get-test-pipeline"
    assert data["extractor"] == "tap-oracle"
    assert data["loader"] == "target-oracle"
    assert data["status"] == "active"


def test_get_pipeline_not_found(client: TestClient) -> None:
    """Test get non-existent pipeline."""
    # Use a valid UUID format that doesn't exist
    non_existent_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/api/v1/pipelines/{non_existent_id}")

    assert response.status_code == 404
    data = response.json()
    assert f"Pipeline {non_existent_id} not found" in data["detail"]


def test_execute_pipeline_endpoint(client: TestClient) -> None:
    """Test execute pipeline endpoint."""
    # First create a pipeline
    create_response = client.post(
        "/api/v1/pipelines",
        json={
            "name": "execute-test-pipeline",
            "extractor": "tap-ldap",
            "loader": "target-ldap",
        },
    )
    assert create_response.status_code == 200
    created_pipeline = create_response.json()
    pipeline_id = created_pipeline["pipeline_id"]

    # Now execute the pipeline
    response = client.post(f"/api/v1/pipelines/{pipeline_id}/execute")

    assert response.status_code == 200
    data = response.json()

    assert "execution_id" in data
    assert data["pipeline_id"] == pipeline_id
    assert data["status"] == "running"
    assert "started_at" in data


def test_execute_pipeline_not_found(client: TestClient) -> None:
    """Test execute non-existent pipeline."""
    from uuid import uuid4

    non_existent_id = str(uuid4())  # Use valid UUID format
    response = client.post(f"/api/v1/pipelines/{non_existent_id}/execute")

    assert response.status_code == 500  # Internal server error from storage
    data = response.json()
    assert f"Pipeline {non_existent_id} not found" in data["detail"]


# Complex pipeline workflow test
def test_complete_pipeline_workflow(client: TestClient) -> None:
    """Test complete pipeline lifecycle: create, list, get, execute."""
    workflow_pipeline_name = "workflow-test-pipeline"

    # Step 1: Create pipeline
    create_response = client.post(
        "/api/v1/pipelines",
        json={
            "name": workflow_pipeline_name,
            "extractor": "tap-oracle-oic",
            "loader": "target-postgres",
        },
    )
    assert create_response.status_code == 200
    created_data = create_response.json()
    pipeline_id = created_data["pipeline_id"]

    # Step 2: Verify it appears in list
    list_response = client.get("/api/v1/pipelines")
    assert list_response.status_code == 200
    list_data = list_response.json()
    pipeline_names = [p["name"] for p in list_data["pipelines"]]
    assert workflow_pipeline_name in pipeline_names

    # Step 3: Get pipeline details
    get_response = client.get(f"/api/v1/pipelines/{pipeline_id}")
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert get_data["name"] == workflow_pipeline_name
    assert get_data["status"] == "active"

    # Step 4: Execute pipeline
    execute_response = client.post(f"/api/v1/pipelines/{pipeline_id}/execute")
    assert execute_response.status_code == 200
    execute_data = execute_response.json()
    assert execute_data["pipeline_id"] == pipeline_id
    assert execute_data["status"] == "running"

    # Step 5: Verify pipeline status changed after execution
    get_after_execute_response = client.get(f"/api/v1/pipelines/{pipeline_id}")
    assert get_after_execute_response.status_code == 200
    final_data = get_after_execute_response.json()
    assert final_data["status"] == "running"
    assert "last_execution_id" in final_data


def test_create_pipeline_missing_parameters(client: TestClient) -> None:
    """Test create pipeline with missing required parameters."""
    # Missing loader parameter
    response = client.post(
        "/api/v1/pipelines",
        json={
            "name": "incomplete-pipeline",
            "extractor": "tap-csv",
            # Missing loader parameter
        },
    )

    assert response.status_code == 422  # Validation error


def test_create_multiple_pipelines_different_names(client: TestClient) -> None:
    """Test creating multiple pipelines with different names."""
    pipelines_to_create = [
        {"name": "pipeline-1", "extractor": "tap-mysql", "loader": "target-postgres"},
        {"name": "pipeline-2", "extractor": "tap-postgresql", "loader": "target-mysql"},
        {"name": "pipeline-3", "extractor": "tap-csv", "loader": "target-jsonl"},
    ]

    created_ids = []

    for pipeline_config in pipelines_to_create:
        response = client.post("/api/v1/pipelines", json=pipeline_config)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == pipeline_config["name"]
        created_ids.append(data["pipeline_id"])

    # Verify all pipelines exist
    list_response = client.get("/api/v1/pipelines")
    assert list_response.status_code == 200
    list_data = list_response.json()

    # Should have at least the 3 we created
    assert list_data["total_count"] >= 3

    # All our pipeline names should be present
    existing_names = [p["name"] for p in list_data["pipelines"]]
    for pipeline_config in pipelines_to_create:
        assert pipeline_config["name"] in existing_names


def test_pipeline_id_format(client: TestClient) -> None:
    """Test that pipeline IDs are properly formatted UUIDs."""
    response = client.post(
        "/api/v1/pipelines",
        json={
            "name": "uuid-test-pipeline",
            "extractor": "tap-test",
            "loader": "target-test",
        },
    )

    assert response.status_code == 200
    data = response.json()

    pipeline_id = data["pipeline_id"]
    # UUID should be 36 characters with 4 hyphens
    assert len(pipeline_id) == 36
    assert pipeline_id.count("-") == 4
    # Should be lowercase hex with hyphens
    cleaned_id = pipeline_id.replace("-", "")
    assert all(c in "0123456789abcdef" for c in cleaned_id)


def test_pipeline_timestamps_format(client: TestClient) -> None:
    """Test that pipeline timestamps are properly formatted."""
    response = client.post(
        "/api/v1/pipelines",
        json={
            "name": "timestamp-test-pipeline",
            "extractor": "tap-timestamp",
            "loader": "target-timestamp",
        },
    )

    assert response.status_code == 200
    data = response.json()

    # created_at should be ISO format
    assert "created_at" in data
    created_at = data["created_at"]
    assert "T" in created_at
    # Accept multiple timezone formats
    assert created_at.endswith(("Z", "+00:00")) or "+00:00" in created_at


def test_pipeline_configuration_structure(client: TestClient) -> None:
    """Test that pipeline configuration has proper structure."""
    response = client.post(
        "/api/v1/pipelines",
        json={
            "name": "config-test-pipeline",
            "extractor": "tap-config",
            "loader": "target-config",
        },
    )

    assert response.status_code == 200
    data = response.json()

    # Verify required fields exist
    required_fields = [
        "pipeline_id",
        "name",
        "extractor",
        "loader",
        "status",
        "created_at",
        "configuration",
    ]
    for field in required_fields:
        assert field in data, f"Required field '{field}' missing from pipeline response"

    # Verify configuration is a dict
    assert isinstance(data["configuration"], dict)

    # Verify execution tracking fields exist
    assert "execution_count" in data
    assert data["execution_count"] == 0  # Initial count should be 0


def test_execute_pipeline_updates_pipeline_state(client: TestClient) -> None:
    """Test that executing a pipeline properly updates the pipeline state."""
    # Create pipeline
    create_response = client.post(
        "/api/v1/pipelines",
        json={
            "name": "state-test-pipeline",
            "extractor": "tap-state",
            "loader": "target-state",
        },
    )
    assert create_response.status_code == 200
    pipeline_data = create_response.json()
    pipeline_id = pipeline_data["pipeline_id"]

    # Verify initial state
    assert pipeline_data["status"] == "active"

    # Execute pipeline
    execute_response = client.post(f"/api/v1/pipelines/{pipeline_id}/execute")
    assert execute_response.status_code == 200
    execute_response.json()

    # Get pipeline after execution
    get_response = client.get(f"/api/v1/pipelines/{pipeline_id}")
    assert get_response.status_code == 200
    updated_pipeline = get_response.json()

    # Verify state changes
    assert updated_pipeline["status"] == "running"
    # The last_execution_id field exists but is None (not implemented)
    assert "last_execution_id" in updated_pipeline
    assert updated_pipeline["last_execution_id"] is None
