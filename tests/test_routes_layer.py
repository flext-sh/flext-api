"""Comprehensive tests for routes layer - 100% coverage target.

Tests all route endpoints with complete coverage:
- Auth routes: login, logout, token refresh, user profile
- Pipeline routes: CRUD operations, execution, monitoring
- Plugin routes: installation, listing, configuration
- System routes: health checks, metrics, configuration
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from flext_core import FlextResult

if TYPE_CHECKING:
    from collections.abc import Generator


@pytest.fixture
def client() -> Generator[TestClient]:
    """Create test client with mocked dependencies."""
    # Mock SQLite database for testing
    with (
        patch("flext_api.dependencies.create_async_engine") as mock_engine,
        patch("flext_api.dependencies.async_session_factory") as mock_session,
    ):
        # Configure mocks to avoid database connection
        mock_engine.return_value = AsyncMock()
        mock_session.return_value = AsyncMock()

        from flext_api.main import app

        with TestClient(app) as test_client:
            yield test_client


class TestAuthRoutes:
    """Complete test coverage for authentication routes - target 95%+."""

    def test_login_success(self, client: TestClient) -> None:
        """Test successful user login."""
        login_data = {
            "username": "REDACTED_LDAP_BIND_PASSWORD",
            "password": "REDACTED_LDAP_BIND_PASSWORD123",
        }

        with patch("flext_api.dependencies.get_flext_auth_service") as mock_auth:
            mock_service = AsyncMock()
            mock_service.login.return_value = FlextResult.ok(
                {
                    "access_token": "test_token",
                    "token_type": "bearer",
                }
            )
            mock_auth.return_value = mock_service

            response = client.post("/api/v1/auth/login", json=login_data)

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["access_token"] == "test_token"
            assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, client: TestClient) -> None:
        """Test login with invalid credentials."""
        login_data = {
            "username": "invalid",
            "password": "invalid",
        }

        with patch("flext_api.dependencies.get_flext_auth_service") as mock_auth:
            mock_service = AsyncMock()
            mock_service.login.return_value = FlextResult.fail("Invalid credentials")
            mock_auth.return_value = mock_service

            response = client.post("/api/v1/auth/login", json=login_data)

            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            data = response.json()
            assert "Invalid credentials" in data["detail"]

    def test_login_missing_fields(self, client: TestClient) -> None:
        """Test login with missing required fields."""
        login_data = {"username": "REDACTED_LDAP_BIND_PASSWORD"}  # Missing password

        response = client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_login_empty_payload(self, client: TestClient) -> None:
        """Test login with empty payload."""
        response = client.post("/api/v1/auth/login", json={})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_login_service_error(self, client: TestClient) -> None:
        """Test login with authentication service error."""
        login_data = {
            "username": "REDACTED_LDAP_BIND_PASSWORD",
            "password": "REDACTED_LDAP_BIND_PASSWORD123",
        }

        with patch("flext_api.dependencies.get_flext_auth_service") as mock_auth:
            mock_service = AsyncMock()
            mock_service.login.return_value = FlextResult.fail("Service unavailable")
            mock_auth.return_value = mock_service

            response = client.post("/api/v1/auth/login", json=login_data)

            assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user_success(self, client: TestClient) -> None:
        """Test successful current user retrieval."""
        mock_user = {
            "username": "testuser",
            "roles": ["user"],
            "is_REDACTED_LDAP_BIND_PASSWORD": False,
        }

        with patch(
            "flext_api.dependencies.get_flext_current_user", return_value=mock_user
        ):
            response = client.get(
                "/api/v1/auth/me", headers={"Authorization": "Bearer test_token"}
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["username"] == "testuser"
            assert data["roles"] == ["user"]

    def test_get_current_user_unauthorized(self, client: TestClient) -> None:
        """Test current user retrieval without token."""
        response = client.get("/api/v1/auth/me")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_current_user_invalid_token(self, client: TestClient) -> None:
        """Test current user retrieval with invalid token."""
        from fastapi import HTTPException

        with patch(
            "flext_api.dependencies.get_flext_current_user",
            side_effect=HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            ),
        ):
            response = client.get(
                "/api/v1/auth/me", headers={"Authorization": "Bearer invalid_token"}
            )

            assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_success(self, client: TestClient) -> None:
        """Test successful user logout."""
        with (
            patch("flext_api.dependencies.get_flext_auth_service") as mock_auth,
            patch(
                "flext_api.dependencies.get_flext_current_user",
                return_value={"username": "testuser"},
            ),
        ):
            mock_service = AsyncMock()
            mock_service.logout.return_value = FlextResult.ok(
                {"message": "Logged out successfully"}
            )
            mock_auth.return_value = mock_service

            response = client.post(
                "/api/v1/auth/logout", headers={"Authorization": "Bearer test_token"}
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "Logged out successfully" in data["message"]

    def test_refresh_token_success(self, client: TestClient) -> None:
        """Test successful token refresh."""
        with patch("flext_api.dependencies.get_flext_auth_service") as mock_auth:
            mock_service = AsyncMock()
            mock_service.refresh_token.return_value = FlextResult.ok(
                {
                    "access_token": "new_token",
                    "token_type": "bearer",
                }
            )
            mock_auth.return_value = mock_service

            response = client.post(
                "/api/v1/auth/refresh",
                headers={"Authorization": "Bearer refresh_token"},
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["access_token"] == "new_token"


class TestPipelineRoutes:
    """Complete test coverage for pipeline routes - target 95%+."""

    def test_list_pipelines_success(self, client: TestClient) -> None:
        """Test successful pipeline listing."""
        mock_pipelines = [
            {
                "id": "pipeline1",
                "name": "test-pipeline-1",
                "description": "Test pipeline 1",
                "status": "created",
                "created_at": "2024-01-01T00:00:00Z",
            },
            {
                "id": "pipeline2",
                "name": "test-pipeline-2",
                "description": "Test pipeline 2",
                "status": "running",
                "created_at": "2024-01-01T00:00:00Z",
            },
        ]

        with (
            patch("flext_api.dependencies.get_flext_pipeline_service") as mock_service,
            patch(
                "flext_api.dependencies.get_flext_current_user",
                return_value={"username": "testuser"},
            ),
        ):
            mock_service_instance = AsyncMock()
            mock_service_instance.list_pipelines.return_value = FlextResult.ok(
                mock_pipelines
            )
            mock_service.return_value = mock_service_instance

            response = client.get(
                "/api/v1/pipelines", headers={"Authorization": "Bearer test_token"}
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data) == 2
            assert data[0]["name"] == "test-pipeline-1"

    def test_list_pipelines_unauthorized(self, client: TestClient) -> None:
        """Test pipeline listing without authentication."""
        response = client.get("/api/v1/pipelines")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_pipeline_success(self, client: TestClient) -> None:
        """Test successful pipeline creation."""
        pipeline_data = {
            "name": "new-pipeline",
            "description": "New test pipeline",
            "config": {"tap": "tap-postgres", "target": "target-jsonl"},
        }

        mock_pipeline = {
            "id": "new-id",
            "name": "new-pipeline",
            "description": "New test pipeline",
            "status": "created",
            "config": {"tap": "tap-postgres", "target": "target-jsonl"},
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }

        with (
            patch("flext_api.dependencies.get_flext_pipeline_service") as mock_service,
            patch(
                "flext_api.dependencies.get_flext_current_user",
                return_value={"username": "testuser"},
            ),
        ):
            mock_service_instance = AsyncMock()
            mock_service_instance.create_pipeline.return_value = FlextResult.ok(
                mock_pipeline
            )
            mock_service.return_value = mock_service_instance

            response = client.post(
                "/api/v1/pipelines",
                json=pipeline_data,
                headers={"Authorization": "Bearer test_token"},
            )

            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["name"] == "new-pipeline"

    def test_create_pipeline_invalid_data(self, client: TestClient) -> None:
        """Test pipeline creation with invalid data."""
        pipeline_data = {"name": ""}  # Invalid empty name

        with patch(
            "flext_api.dependencies.get_flext_current_user",
            return_value={"username": "testuser"},
        ):
            response = client.post(
                "/api/v1/pipelines",
                json=pipeline_data,
                headers={"Authorization": "Bearer test_token"},
            )

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_pipeline_success(self, client: TestClient) -> None:
        """Test successful pipeline retrieval."""
        pipeline_id = "test-pipeline-id"
        mock_pipeline = {
            "id": pipeline_id,
            "name": "test-pipeline",
            "description": "Test pipeline",
            "status": "created",
            "config": {},
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }

        with (
            patch("flext_api.dependencies.get_flext_pipeline_service") as mock_service,
            patch(
                "flext_api.dependencies.get_flext_current_user",
                return_value={"username": "testuser"},
            ),
        ):
            mock_service_instance = AsyncMock()
            mock_service_instance.get_pipeline.return_value = FlextResult.ok(
                mock_pipeline
            )
            mock_service.return_value = mock_service_instance

            response = client.get(
                f"/api/v1/pipelines/{pipeline_id}",
                headers={"Authorization": "Bearer test_token"},
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["id"] == pipeline_id

    def test_get_pipeline_not_found(self, client: TestClient) -> None:
        """Test pipeline retrieval for non-existent pipeline."""
        pipeline_id = "nonexistent-id"

        with (
            patch("flext_api.dependencies.get_flext_pipeline_service") as mock_service,
            patch(
                "flext_api.dependencies.get_flext_current_user",
                return_value={"username": "testuser"},
            ),
        ):
            mock_service_instance = AsyncMock()
            mock_service_instance.get_pipeline.return_value = FlextResult.fail(
                "Pipeline not found"
            )
            mock_service.return_value = mock_service_instance

            response = client.get(
                f"/api/v1/pipelines/{pipeline_id}",
                headers={"Authorization": "Bearer test_token"},
            )

            assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_pipeline_success(self, client: TestClient) -> None:
        """Test successful pipeline update."""
        pipeline_id = "test-pipeline-id"
        update_data = {"description": "Updated description"}

        mock_pipeline = {
            "id": pipeline_id,
            "name": "test-pipeline",
            "description": "Updated description",
            "status": "created",
            "config": {},
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }

        with (
            patch("flext_api.dependencies.get_flext_pipeline_service") as mock_service,
            patch(
                "flext_api.dependencies.get_flext_current_user",
                return_value={"username": "testuser"},
            ),
        ):
            mock_service_instance = AsyncMock()
            mock_service_instance.update_pipeline.return_value = FlextResult.ok(
                mock_pipeline
            )
            mock_service.return_value = mock_service_instance

            response = client.put(
                f"/api/v1/pipelines/{pipeline_id}",
                json=update_data,
                headers={"Authorization": "Bearer test_token"},
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["description"] == "Updated description"

    def test_delete_pipeline_success(self, client: TestClient) -> None:
        """Test successful pipeline deletion."""
        pipeline_id = "test-pipeline-id"

        with (
            patch("flext_api.dependencies.get_flext_pipeline_service") as mock_service,
            patch(
                "flext_api.dependencies.get_flext_current_user",
                return_value={"username": "testuser"},
            ),
        ):
            mock_service_instance = AsyncMock()
            mock_service_instance.delete_pipeline.return_value = FlextResult.ok(
                {"message": "Pipeline deleted"}
            )
            mock_service.return_value = mock_service_instance

            response = client.delete(
                f"/api/v1/pipelines/{pipeline_id}",
                headers={"Authorization": "Bearer test_token"},
            )

            assert response.status_code == status.HTTP_200_OK

    def test_execute_pipeline_success(self, client: TestClient) -> None:
        """Test successful pipeline execution."""
        pipeline_id = "test-pipeline-id"

        mock_execution = {
            "execution_id": "exec-123",
            "status": "running",
            "started_at": "2024-01-01T00:00:00Z",
        }

        with (
            patch("flext_api.dependencies.get_flext_pipeline_service") as mock_service,
            patch(
                "flext_api.dependencies.get_flext_current_user",
                return_value={"username": "testuser"},
            ),
        ):
            mock_service_instance = AsyncMock()
            mock_service_instance.execute_pipeline.return_value = FlextResult.ok(
                mock_execution
            )
            mock_service.return_value = mock_service_instance

            response = client.post(
                f"/api/v1/pipelines/{pipeline_id}/execute",
                headers={"Authorization": "Bearer test_token"},
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["status"] == "running"


class TestPluginRoutes:
    """Complete test coverage for plugin routes - target 95%+."""

    def test_list_plugins_success(self, client: TestClient) -> None:
        """Test successful plugin listing."""
        # Use the actual storage from main.py instead of mocking
        response = client.get("/api/v1/plugins")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "plugins" in data
        assert "total_count" in data

    def test_list_plugins_with_pagination(self, client: TestClient) -> None:
        """Test plugin listing with pagination."""
        response = client.get("/api/v1/plugins?page=1&page_size=10")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 10

    def test_list_plugins_with_filters(self, client: TestClient) -> None:
        """Test plugin listing with filters."""
        response = client.get("/api/v1/plugins?category=tap&status=installed")

        assert response.status_code == status.HTTP_200_OK

    def test_get_plugin_success(self, client: TestClient) -> None:
        """Test successful plugin retrieval."""
        plugin_name = "tap-oracle-oic"  # This exists in storage

        response = client.get(f"/api/v1/plugins/{plugin_name}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == plugin_name

    def test_get_plugin_not_found(self, client: TestClient) -> None:
        """Test plugin retrieval for non-existent plugin."""
        plugin_name = "nonexistent-plugin"

        response = client.get(f"/api/v1/plugins/{plugin_name}")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_install_plugin_success(self, client: TestClient) -> None:
        """Test successful plugin installation."""
        installation_data = {
            "name": "tap-postgres",
            "version": "1.0.0",
            "source": "hub",
        }

        with (
            patch("flext_api.dependencies.get_plugin_manager") as mock_manager,
            patch(
                "flext_api.dependencies.get_flext_current_user",
                return_value={"username": "testuser"},
            ),
        ):
            mock_manager_instance = AsyncMock()
            mock_manager_instance.install_plugin.return_value = {
                "name": "tap-postgres",
                "version": "1.0.0",
                "status": "installed",
                "path": "/opt/meltano/plugins/tap-postgres",
            }
            mock_manager.return_value = mock_manager_instance

            response = client.post(
                "/api/v1/plugins/install",
                json=installation_data,
                headers={"Authorization": "Bearer test_token"},
            )

            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["name"] == "tap-postgres"

    def test_install_plugin_unauthorized(self, client: TestClient) -> None:
        """Test plugin installation without authentication."""
        installation_data = {
            "name": "tap-postgres",
            "version": "1.0.0",
            "source": "hub",
        }

        response = client.post("/api/v1/plugins/install", json=installation_data)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_install_plugin_invalid_data(self, client: TestClient) -> None:
        """Test plugin installation with invalid data."""
        installation_data = {"name": ""}  # Invalid empty name

        with patch(
            "flext_api.dependencies.get_flext_current_user",
            return_value={"username": "testuser"},
        ):
            response = client.post(
                "/api/v1/plugins/install",
                json=installation_data,
                headers={"Authorization": "Bearer test_token"},
            )

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestSystemRoutes:
    """Complete test coverage for system routes - target 95%+."""

    def test_health_check_success(self, client: TestClient) -> None:
        """Test successful health check."""
        with patch("flext_api.dependencies.get_flext_system_service") as mock_service:
            mock_service_instance = AsyncMock()
            mock_service_instance.get_health.return_value = FlextResult.ok(
                {
                    "status": "healthy",
                    "timestamp": "2024-01-01T00:00:00Z",
                    "system": {
                        "cpu_usage": 50.0,
                        "memory_usage": 60.0,
                        "disk_usage": 70.0,
                    },
                }
            )
            mock_service.return_value = mock_service_instance

            response = client.get("/api/v1/system/health")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["status"] == "healthy"

    def test_health_check_failure(self, client: TestClient) -> None:
        """Test health check failure."""
        with patch("flext_api.dependencies.get_flext_system_service") as mock_service:
            mock_service_instance = AsyncMock()
            mock_service_instance.get_health.return_value = FlextResult.fail(
                "Health check failed"
            )
            mock_service.return_value = mock_service_instance

            response = client.get("/api/v1/system/health")

            assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE

    def test_get_metrics_success(self, client: TestClient) -> None:
        """Test successful metrics retrieval."""
        with patch("flext_api.dependencies.get_flext_system_service") as mock_service:
            mock_service_instance = AsyncMock()
            mock_service_instance.get_metrics.return_value = FlextResult.ok(
                {
                    "cpu_usage": 45.0,
                    "memory_usage": 55.0,
                    "disk_usage": 65.0,
                    "uptime": 3600,
                }
            )
            mock_service.return_value = mock_service_instance

            response = client.get("/api/v1/system/metrics")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "cpu_usage" in data

    def test_get_config_success(self, client: TestClient) -> None:
        """Test successful configuration retrieval."""
        with (
            patch("flext_api.dependencies.get_flext_system_service") as mock_service,
            patch(
                "flext_api.dependencies.get_flext_current_user",
                return_value={"username": "REDACTED_LDAP_BIND_PASSWORD", "is_REDACTED_LDAP_BIND_PASSWORD": True},
            ),
        ):
            mock_service_instance = AsyncMock()
            mock_service_instance.get_config.return_value = FlextResult.ok(
                {
                    "project_name": "FLEXT API",
                    "version": "0.7.0",
                    "debug": False,
                }
            )
            mock_service.return_value = mock_service_instance

            response = client.get(
                "/api/v1/system/config", headers={"Authorization": "Bearer test_token"}
            )

            assert response.status_code == status.HTTP_200_OK

    def test_get_config_unauthorized(self, client: TestClient) -> None:
        """Test configuration retrieval without authentication."""
        response = client.get("/api/v1/system/config")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_config_success(self, client: TestClient) -> None:
        """Test successful configuration update."""
        config_updates = {"log_level": "DEBUG"}

        with (
            patch("flext_api.dependencies.get_flext_system_service") as mock_service,
            patch(
                "flext_api.dependencies.get_flext_current_user",
                return_value={"username": "REDACTED_LDAP_BIND_PASSWORD", "is_REDACTED_LDAP_BIND_PASSWORD": True},
            ),
        ):
            mock_service_instance = AsyncMock()
            mock_service_instance.update_config.return_value = FlextResult.ok(
                {"message": "Config updated"}
            )
            mock_service.return_value = mock_service_instance

            response = client.put(
                "/api/v1/system/config",
                json=config_updates,
                headers={"Authorization": "Bearer test_token"},
            )

            assert response.status_code == status.HTTP_200_OK


class TestErrorHandling:
    """Test error handling across all routes - target 95%+."""

    def test_invalid_json_payload(self, client: TestClient) -> None:
        """Test handling of invalid JSON payload."""
        response = client.post(
            "/api/v1/auth/login",
            data="invalid json",
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_missing_content_type(self, client: TestClient) -> None:
        """Test handling of missing content type."""
        response = client.post("/api/v1/auth/login", data='{"username": "test"}')

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_method_not_allowed(self, client: TestClient) -> None:
        """Test handling of unsupported HTTP methods."""
        response = client.patch("/api/v1/auth/login")

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_not_found_endpoint(self, client: TestClient) -> None:
        """Test handling of non-existent endpoints."""
        response = client.get("/api/v1/nonexistent")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_internal_server_error(self, client: TestClient) -> None:
        """Test handling of internal server errors."""
        with patch(
            "flext_api.dependencies.get_flext_system_service",
            side_effect=RuntimeError("Internal error"),
        ):
            response = client.get("/api/v1/system/health")

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_service_unavailable(self, client: TestClient) -> None:
        """Test handling of service unavailable errors."""
        with patch("flext_api.dependencies.get_flext_system_service") as mock_service:
            mock_service_instance = AsyncMock()
            mock_service_instance.get_health.return_value = FlextResult.fail(
                "Service down"
            )
            mock_service.return_value = mock_service_instance

            response = client.get("/api/v1/system/health")

            assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
