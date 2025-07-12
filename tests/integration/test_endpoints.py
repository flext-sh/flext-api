"""Integration tests for API endpoints.

Modern async integration tests for FastAPI endpoints.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from typing import Any

    from httpx import AsyncClient


@pytest.mark.integration
class TestPipelineEndpoints:
    """Test pipeline API endpoints."""

    @pytest.mark.asyncio
    async def test_create_pipeline(
        self,
        async_client: AsyncClient,
        sample_pipeline_data: dict[str, Any],
        auth_headers: dict[str, str],
    ) -> None:
        """Test pipeline creation."""
        response = await async_client.post(
            "/api/v1/pipelines",
            json=sample_pipeline_data,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_pipeline_data["name"]
        assert "id" in data
        assert data["status"] == "active"

    @pytest.mark.asyncio
    async def test_get_pipeline(
        self,
        async_client: AsyncClient,
        auth_headers: dict[str, str],
    ) -> None:
        """Test getting a single pipeline."""
        # First create a pipeline
        create_response = await async_client.post(
            "/api/v1/pipelines",
            json={
                "name": "test-get-pipeline",
                "description": "Pipeline for GET test",
                "config": {},
            },
            headers=auth_headers,
        )
        pipeline_id = create_response.json()["id"]

        # Then retrieve it
        response = await async_client.get(
            f"/api/v1/pipelines/{pipeline_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == pipeline_id
        assert data["name"] == "test-get-pipeline"

    @pytest.mark.asyncio
    async def test_list_pipelines(
        self,
        async_client: AsyncClient,
        auth_headers: dict[str, str],
    ) -> None:
        """Test listing pipelines with pagination."""
        # Create multiple pipelines
        for i in range(3):
            await async_client.post(
                "/api/v1/pipelines",
                json={
                    "name": f"test-list-pipeline-{i}",
                    "description": f"Pipeline {i}",
                    "config": {},
                },
                headers=auth_headers,
            )

        # List with pagination
        response = await async_client.get(
            "/api/v1/pipelines?limit=2&offset=0",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) <= 2
        assert "total" in data
        assert "has_more" in data

    @pytest.mark.asyncio
    async def test_update_pipeline(
        self,
        async_client: AsyncClient,
        auth_headers: dict[str, str],
    ) -> None:
        """Test updating a pipeline."""
        # Create pipeline
        create_response = await async_client.post(
            "/api/v1/pipelines",
            json={
                "name": "test-update-pipeline",
                "description": "Original description",
                "config": {},
            },
            headers=auth_headers,
        )
        pipeline_id = create_response.json()["id"]

        # Update it
        response = await async_client.patch(
            f"/api/v1/pipelines/{pipeline_id}",
            json={
                "description": "Updated description",
                "config": {"new_field": "new_value"},
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated description"
        assert data["config"]["new_field"] == "new_value"

    @pytest.mark.asyncio
    async def test_delete_pipeline(
        self,
        async_client: AsyncClient,
        auth_headers: dict[str, str],
    ) -> None:
        """Test deleting a pipeline."""
        # Create pipeline
        create_response = await async_client.post(
            "/api/v1/pipelines",
            json={
                "name": "test-delete-pipeline",
                "description": "To be deleted",
                "config": {},
            },
            headers=auth_headers,
        )
        pipeline_id = create_response.json()["id"]

        # Delete it
        response = await async_client.delete(
            f"/api/v1/pipelines/{pipeline_id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

        # Verify it's gone
        get_response = await async_client.get(
            f"/api/v1/pipelines/{pipeline_id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 404


@pytest.mark.integration
class TestAuthEndpoints:
    """Test authentication endpoints."""

    @pytest.mark.asyncio
    async def test_login_valid_credentials(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test login with valid credentials."""
        response = await async_client.post(
            "/api/v1/auth/login",
            json={
                "username": "testuser",
                "password": "testpass123",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test login with invalid credentials."""
        response = await async_client.post(
            "/api/v1/auth/login",
            json={
                "username": "invaliduser",
                "password": "wrongpass",
            },
        )

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_protected_endpoint_without_auth(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test accessing protected endpoint without authentication."""
        response = await async_client.get("/api/v1/pipelines")

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "Not authenticated" in data["detail"]
