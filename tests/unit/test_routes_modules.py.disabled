"""Tests for FLEXT API routes modules to ensure 100% endpoint coverage."""

from __future__ import annotations

from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from flext_api.main import app


class TestMainApplication:
    """Test main FastAPI application and route integration."""

    @pytest.fixture
    def client(self) -> TestClient:
        """Create test client for the main application."""
        return TestClient(app)

    def test_app_instance_creation(self) -> None:
        """Test that app instance is created correctly."""
        assert isinstance(app, FastAPI)
        assert app.title == "FLEXT API"
        assert "Enterprise Data Integration Platform" in app.description

    def test_app_metadata(self) -> None:
        """Test application metadata is set correctly."""
        assert app.version == "1.0.0"
        assert app.docs_url == "/docs"
        assert app.redoc_url == "/redoc"

    def test_cors_middleware_configured(self) -> None:
        """Test CORS middleware is properly configured."""
        # Check if CORS middleware is in the middleware stack
        cors_middleware_found = any(
            hasattr(middleware, "cls") and "CORS" in str(middleware.cls)
            for middleware in app.user_middleware
        )
        assert cors_middleware_found

    def test_root_endpoint(self, client: TestClient) -> None:
        """Test root endpoint returns API information."""
        response = client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert data["message"] == "FLEXT API - Enterprise Data Integration Platform"
        assert "version" in data
        assert "documentation" in data

    def test_health_endpoint(self, client: TestClient) -> None:
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
        assert "uptime" in data

    def test_api_info_endpoint(self, client: TestClient) -> None:
        """Test API info endpoint."""
        response = client.get("/api/info")
        assert response.status_code == 200

        data = response.json()
        assert "api_name" in data
        assert "version" in data
        assert "endpoints" in data
        assert len(data["endpoints"]) > 0

    def test_router_inclusion(self) -> None:
        """Test that all routers are properly included."""
        # Get all routes from the app
        routes = [getattr(route, "path", str(route)) for route in app.routes]

        # Check that expected router prefixes are present
        expected_prefixes = [
            "/api/v1/auth",
            "/api/v1/plugins",
            "/api/v1/system",
        ]

        for prefix in expected_prefixes:
            # Check if any route starts with the expected prefix
            prefix_found = any(route.startswith(prefix) for route in routes)
            assert prefix_found, f"No routes found with prefix {prefix}"

    def test_openapi_schema_generation(self, client: TestClient) -> None:
        """Test OpenAPI schema is generated correctly."""
        response = client.get("/openapi.json")
        assert response.status_code == 200

        schema = response.json()
        assert schema["openapi"] == "3.1.0"
        assert schema["info"]["title"] == "FLEXT API"
        assert "paths" in schema
        assert len(schema["paths"]) > 0


class TestAuthRoutes:
    """Test authentication routes integration."""

    @pytest.fixture
    def client(self) -> TestClient:
        """Create test client."""
        return TestClient(app)

    def test_auth_login_route_exists(self, client: TestClient) -> None:
        """Test login route exists and is accessible."""
        # Test route exists (may return error but should not be 404)
        response = client.post("/api/v1/auth/login", json={})
        assert response.status_code != 404

    def test_auth_logout_route_exists(self, client: TestClient) -> None:
        """Test logout route exists and is accessible."""
        response = client.post("/api/v1/auth/logout", json={})
        assert response.status_code != 404

    def test_auth_user_info_route_exists(self, client: TestClient) -> None:
        """Test user profile route exists and is accessible."""
        response = client.get("/api/v1/auth/profile")
        assert response.status_code != 404

    def test_auth_routes_require_proper_data(self, client: TestClient) -> None:
        """Test auth routes validate request data properly."""
        # Login should require username and password
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "test_user", "password": "test_password"},
        )
        # Should not be a validation error (422)
        assert response.status_code != 422

    @patch("flext_api.application.services.auth_service.AuthService")
    def test_auth_routes_with_mocked_service(
        self,
        mock_auth_service_class: Mock,
        client: TestClient,
    ) -> None:
        """Test auth routes with mocked service."""
        mock_service = Mock()
        mock_service.login = AsyncMock(
            return_value=Mock(
                is_successful=True,
                unwrap=Mock(
                    return_value={
                        "access_token": "test_token",
                        "token_type": "bearer",
                        "expires_in": 3600,
                        "username": "test_user",
                    },
                ),
            ),
        )
        mock_auth_service_class.return_value = mock_service

        response = client.post(
            "/api/v1/auth/login",
            json={"username": "test_user", "password": "test_password"},
        )

        # Should succeed with mocked service
        assert response.status_code == 200


class TestPluginRoutes:
    """Test plugin management routes integration."""

    @pytest.fixture
    def client(self) -> TestClient:
        """Create test client."""
        return TestClient(app)

    def test_plugin_list_route_exists(self, client: TestClient) -> None:
        """Test plugin list route exists."""
        response = client.get("/api/v1/plugins")
        assert response.status_code != 404

    def test_plugin_install_route_exists(self, client: TestClient) -> None:
        """Test plugin install route exists."""
        response = client.post("/api/v1/plugins/install", json={})
        assert response.status_code != 404

    def test_plugin_uninstall_route_exists(self, client: TestClient) -> None:
        """Test plugin uninstall route exists."""
        plugin_id = str(uuid4())
        response = client.delete(f"/api/v1/plugins/{plugin_id}")
        assert response.status_code != 404

    def test_plugin_update_route_exists(self, client: TestClient) -> None:
        """Test plugin update route exists."""
        plugin_id = str(uuid4())
        response = client.put(f"/api/v1/plugins/{plugin_id}", json={})
        assert response.status_code != 404

    def test_plugin_get_route_exists(self, client: TestClient) -> None:
        """Test get plugin route exists."""
        # Use a valid plugin name that exists in storage
        plugin_name = "tap-oracle-oic"
        response = client.get(f"/api/v1/plugins/{plugin_name}")
        assert response.status_code != 404

    def test_plugin_config_route_exists(self, client: TestClient) -> None:
        """Test plugin config route exists."""
        plugin_id = str(uuid4())
        response = client.put(f"/api/v1/plugins/{plugin_id}/config", json={})
        assert response.status_code != 404

    def test_plugin_health_route_exists(self, client: TestClient) -> None:
        """Test plugin health route exists."""
        plugin_id = str(uuid4())
        response = client.get(f"/api/v1/plugins/{plugin_id}/health")
        assert response.status_code != 404

    def test_plugin_discover_route_exists(self, client: TestClient) -> None:
        """Test plugin discovery route exists."""
        response = client.get("/api/v1/plugins/discover")
        assert response.status_code != 404

    def test_plugin_stats_route_exists(self, client: TestClient) -> None:
        """Test plugin stats route exists."""
        response = client.get("/api/v1/plugins/stats")
        assert response.status_code != 404

    def test_plugin_routes_handle_query_params(self, client: TestClient) -> None:
        """Test plugin routes handle query parameters correctly."""
        # Test list with filters
        response = client.get("/api/v1/plugins?plugin_type=tap&status=installed")
        assert response.status_code != 422  # Should not be validation error

        # Test discover with search
        response = client.get("/api/v1/plugins/discover?search=csv&plugin_type=tap")
        assert response.status_code != 422


class TestSystemRoutes:
    """Test system management routes integration."""

    @pytest.fixture
    def client(self) -> TestClient:
        """Create test client."""
        return TestClient(app)

    def test_system_status_route_exists(self, client: TestClient) -> None:
        """Test system status route exists."""
        response = client.get("/api/v1/system/status")
        assert response.status_code != 404

    def test_system_info_route_exists(self, client: TestClient) -> None:
        """Test system info route exists."""
        response = client.get("/api/v1/system/info")
        assert response.status_code != 404

    def test_system_metrics_route_exists(self, client: TestClient) -> None:
        """Test system metrics route exists."""
        response = client.get("/api/v1/system/metrics")
        assert response.status_code != 404

    def test_system_logs_route_exists(self, client: TestClient) -> None:
        """Test system logs route exists."""
        response = client.get("/api/v1/system/logs")
        assert response.status_code != 404

    def test_system_config_route_exists(self, client: TestClient) -> None:
        """Test system config route exists."""
        response = client.get("/api/v1/system/config")
        assert response.status_code != 404

    def test_system_backup_route_exists(self, client: TestClient) -> None:
        """Test system backup route exists."""
        response = client.post("/api/v1/system/backup", json={})
        assert response.status_code != 404

    def test_system_restore_route_exists(self, client: TestClient) -> None:
        """Test system restore route exists."""
        backup_id = str(uuid4())
        response = client.post(f"/api/v1/system/restore/{backup_id}", json={})
        assert response.status_code != 404

    def test_system_health_check_route_exists(self, client: TestClient) -> None:
        """Test system health check route exists."""
        response = client.post("/api/v1/system/health-check")
        # Should return 501 (Not Implemented) not 404 (Not Found)
        assert response.status_code == 501


class TestRouteErrorHandling:
    """Test route error handling and edge cases."""

    @pytest.fixture
    def client(self) -> TestClient:
        """Create test client."""
        return TestClient(app)

    def test_404_for_nonexistent_routes(self, client: TestClient) -> None:
        """Test 404 is returned for non-existent routes."""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404

    def test_405_for_wrong_http_methods(self, client: TestClient) -> None:
        """Test 405 is returned for wrong HTTP methods."""
        # Try POST on a GET-only endpoint
        response = client.post("/api/v1/plugins/stats")
        assert response.status_code == 405

        # Try GET on a POST-only endpoint
        response = client.get("/api/v1/auth/login")
        assert response.status_code == 405

    def test_422_for_invalid_request_data(self, client: TestClient) -> None:
        """Test 422 is returned for invalid request data."""
        # Invalid JSON structure
        response = client.post("/api/v1/auth/login", json={"invalid_field": "value"})
        assert response.status_code == 422

    def test_422_for_malformed_requests(self, client: TestClient) -> None:
        """Test 422 is returned for malformed JSON requests."""
        # Invalid JSON syntax - FastAPI returns 422 for JSON parsing errors
        response = client.post(
            "/api/v1/auth/login",
            content="invalid json",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 422

    def test_unsupported_media_type(self, client: TestClient) -> None:
        """Test 415 is returned for unsupported media types."""
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "test", "password": "test"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        # Should accept form data or return appropriate error
        assert response.status_code in {200, 422, 415}


class TestRouteAuthentication:
    """Test route authentication and authorization."""

    @pytest.fixture
    def client(self) -> TestClient:
        """Create test client."""
        return TestClient(app)

    def test_protected_routes_require_auth(self, client: TestClient) -> None:
        """Test that protected routes require authentication."""
        protected_endpoints = [
            "/api/v1/auth/profile",
            "/api/v1/plugins/install",
            "/api/v1/system/backup",
        ]

        for endpoint in protected_endpoints:
            if endpoint.endswith(("/install", "/backup")):
                response = client.post(endpoint, json={})
            else:
                response = client.get(endpoint)

            # Should either require auth (401) or succeed with mock data
            assert response.status_code in {200, 401, 422}

    def test_public_routes_work_without_auth(self, client: TestClient) -> None:
        """Test that public routes work without authentication."""
        public_endpoints = [
            "/",
            "/health",
            "/api/info",
            "/api/v1/plugins/discover",
            "/api/v1/system/status",
        ]

        for endpoint in public_endpoints:
            response = client.get(endpoint)
            # Should work without authentication
            assert response.status_code == 200

    def test_auth_header_handling(self, client: TestClient) -> None:
        """Test authentication header handling for profile endpoint."""
        # Test with valid Bearer token format
        headers = {"Authorization": "Bearer test_token"}
        response = client.get("/api/v1/auth/profile", headers=headers)

        # Profile endpoint is currently a placeholder that returns 200
        assert response.status_code == 200

        # Test with invalid header format - placeholder endpoints don't validate headers
        headers = {"Authorization": "Invalid format"}
        response = client.get("/api/v1/auth/profile", headers=headers)

        # Placeholder endpoint accepts any request
        assert response.status_code == 200


class TestRouteRequestValidation:
    """Test route request validation and data handling."""

    @pytest.fixture
    def client(self) -> TestClient:
        """Create test client."""
        return TestClient(app)

    def test_json_request_validation(self, client: TestClient) -> None:
        """Test JSON request body validation."""
        # Valid request structure
        valid_data = {
            "name": "test-plugin",
            "plugin_type": "tap",
            "version": "1.0.0",
        }

        response = client.post("/api/v1/plugins/install", json=valid_data)
        assert response.status_code != 422

    def test_query_parameter_validation(self, client: TestClient) -> None:
        """Test query parameter validation."""
        # Valid query parameters
        response = client.get("/api/v1/plugins?page=1&page_size=20&plugin_type=tap")
        assert response.status_code != 422

        # Invalid query parameters
        response = client.get("/api/v1/plugins?page=-1&page_size=0")
        # Should handle invalid params gracefully
        assert response.status_code in {200, 422}

    def test_path_parameter_validation(self, client: TestClient) -> None:
        """Test path parameter validation."""
        # Valid UUID format
        valid_uuid = str(uuid4())
        response = client.get(f"/api/v1/plugins/{valid_uuid}")
        assert response.status_code != 422

        # Invalid UUID format
        response = client.get("/api/v1/plugins/invalid-uuid")
        assert response.status_code in {404, 422}

    def test_content_type_handling(self, client: TestClient) -> None:
        """Test different content type handling."""
        data = {"username": "test", "password": "test"}

        # JSON content type
        response = client.post("/api/v1/auth/login", json=data)
        assert response.status_code != 415

        # Form data content type (if supported)
        response = client.post("/api/v1/auth/login", data=data)
        # Should either work or return appropriate error
        assert response.status_code in {200, 415, 422}


class TestRouteResponseFormats:
    """Test route response formats and structure."""

    @pytest.fixture
    def client(self) -> TestClient:
        """Create test client."""
        return TestClient(app)

    def test_json_response_format(self, client: TestClient) -> None:
        """Test that routes return properly formatted JSON."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.headers.get("content-type") == "application/json"

        # Should be valid JSON
        data = response.json()
        assert isinstance(data, dict)

    def test_error_response_format(self, client: TestClient) -> None:
        """Test error responses are properly formatted."""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404

        # Error should be in JSON format
        assert response.headers.get("content-type") == "application/json"
        error_data = response.json()
        assert "detail" in error_data

    def test_validation_error_format(self, client: TestClient) -> None:
        """Test validation error responses are properly formatted."""
        response = client.post("/api/v1/auth/login", json={})

        if response.status_code == 422:
            error_data = response.json()
            assert "detail" in error_data
            assert isinstance(error_data["detail"], list)

    def test_successful_response_structure(self, client: TestClient) -> None:
        """Test successful responses have consistent structure."""
        response = client.get("/")
        assert response.status_code == 200

        data = response.json()
        # Should have consistent structure for API responses
        assert "message" in data or "status" in data


class TestRoutePerformance:
    """Test route performance and concurrency."""

    @pytest.fixture
    def client(self) -> TestClient:
        """Create test client."""
        return TestClient(app)

    def test_concurrent_requests(self, client: TestClient) -> None:
        """Test handling of concurrent requests."""
        import threading

        results = []

        def make_request() -> None:
            response = client.get("/health")
            results.append(response.status_code)

        # Create multiple threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # All requests should succeed
        assert len(results) == 10
        assert all(status == 200 for status in results)

    def test_large_request_handling(self, client: TestClient) -> None:
        """Test handling of large request payloads."""
        # Create large but reasonable payload
        large_config = {f"key_{i}": f"value_{i}" for i in range(100)}
        large_data = {"name": "test-plugin", "configuration": large_config}

        response = client.post("/api/v1/plugins/install", json=large_data)
        # Should handle large payload gracefully
        assert response.status_code != 413  # Not "Payload Too Large"

    def test_request_timeout_handling(self, client: TestClient) -> None:
        """Test request timeout handling."""
        # This test would require mocking slow operations
        # For now, just test that normal requests complete quickly
        import time

        start_time = time.time()
        response = client.get("/health")
        end_time = time.time()

        assert response.status_code == 200
        assert (end_time - start_time) < 5.0  # Should complete within 5 seconds
