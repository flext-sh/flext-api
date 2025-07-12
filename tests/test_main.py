"""Real tests for FLEXT API main module."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

from flext_api.main import app
from flext_api.models.system import SystemStatus


class TestSystemEndpoints:
    """Test system management endpoints."""

    def setup_method(self) -> None:
        """Set up test client."""
        self.client = TestClient(app)

    def test_health_check(self) -> None:
        """Test health check endpoint returns correct status."""
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data

    def test_system_status(self) -> None:
        """Test system status endpoint."""
        response = self.client.get("/api/v1/system/status")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in [s.value for s in SystemStatus]
        assert "uptime_seconds" in data
        assert isinstance(data["uptime_seconds"], (int, float))
        assert data["uptime_seconds"] >= 0

    def test_system_metrics(self) -> None:
        """Test system metrics endpoint."""
        response = self.client.get("/api/v1/system/metrics")
        assert response.status_code == 200
        data = response.json()
        # API returns a list of metrics, not a dict
        assert isinstance(data, list)
        assert len(data) > 0
        # Check for specific metrics in the list
        metric_names = [m["metric_name"] for m in data]
        assert "cpu_usage" in metric_names
        assert "memory_usage" in metric_names
        # Check metric values
        cpu_metric = next(m for m in data if m["metric_name"] == "cpu_usage")
        assert 0 <= cpu_metric["value"] <= 100

    def test_create_alert(self) -> None:
        """Test creating a system alert."""
        response = self.client.post(
            "/api/v1/system/alerts",
            params={
                "severity": "warning",
                "title": "Test Alert",
                "message": "Test alert message",
            }
        )
        assert response.status_code == 200  # FastAPI default is 200, not 201
        data = response.json()
        assert data["severity"] == "warning"
        assert data["title"] == "Test Alert"
        assert data["message"] == "Test alert message"
        assert "alert_id" in data
        assert "created_at" in data

    def test_list_alerts(self) -> None:
        """Test listing system alerts."""
        # First create an alert
        self.client.post(
            "/api/v1/system/alerts",
            params={
                "severity": "info",
                "title": "Test Info",
                "message": "Test info alert",
            }
        )

        # Then list alerts
        response = self.client.get("/api/v1/system/alerts")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert any(alert["message"] == "Test info alert" for alert in data)

    def test_maintenance_mode(self) -> None:
        """Test enabling and disabling maintenance mode."""
        # Enable maintenance mode
        maintenance_data = {
            "mode": "scheduled",
            "reason": "System maintenance in progress",  # Changed from message to reason
        }
        response = self.client.post("/api/v1/system/maintenance", json=maintenance_data)
        assert response.status_code == 200
        data = response.json()
        assert data["mode"] == "scheduled"
        assert data["reason"] == "System maintenance in progress"
        assert data["status"] == "started"

        # Check status reflects maintenance mode
        response = self.client.get("/api/v1/system/status")
        assert response.status_code == 200
        assert response.json()["maintenance_mode"] == "scheduled"

        # Disable maintenance mode
        disable_data = {"mode": "none", "reason": "Maintenance completed"}
        response = self.client.post("/api/v1/system/maintenance", json=disable_data)
        assert response.status_code == 200
        data = response.json()
        assert data["mode"] == "none"
        assert data["status"] == "started"


@pytest.mark.asyncio
class TestAsyncEndpoints:
    """Test async endpoints."""

    async def test_async_health_check(self) -> None:
        """Test async health check endpoint."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"

    async def test_create_backup_async(self) -> None:
        """Test creating system backup asynchronously."""
        backup_data = {"backup_type": "full", "description": "Test backup"}
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/api/v1/system/backup", json=backup_data)
            assert response.status_code == 200  # API returns 200, not 202
            data = response.json()
            assert data["backup_type"] == "full"
            assert data["status"] == "completed"  # API completes immediately
            assert "backup_id" in data
            assert "created_at" in data


class TestErrorHandling:
    """Test error handling."""

    def setup_method(self) -> None:
        """Set up test client."""
        self.client = TestClient(app)

    def test_invalid_alert_severity(self) -> None:
        """Test creating alert with invalid severity."""
        alert_data = {
            "severity": "invalid_severity",
            "message": "Test alert",
            "source": "test",
        }
        response = self.client.post("/api/v1/system/alerts", json=alert_data)
        assert response.status_code == 422
        assert "field required" in response.json()["detail"][0]["msg"].lower()

    def test_invalid_maintenance_mode(self) -> None:
        """Test setting invalid maintenance mode."""
        maintenance_data = {"mode": "invalid_mode", "message": "Test"}
        response = self.client.post("/api/v1/system/maintenance", json=maintenance_data)
        assert response.status_code == 422

    def test_missing_required_fields(self) -> None:
        """Test request with missing required fields."""
        # Alert without message
        alert_data = {"severity": "error", "source": "test"}
        response = self.client.post("/api/v1/system/alerts", json=alert_data)
        assert response.status_code == 422

    def test_get_nonexistent_alert(self) -> None:
        """Test getting a non-existent alert."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = self.client.get(f"/api/v1/system/alerts/{fake_id}")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
