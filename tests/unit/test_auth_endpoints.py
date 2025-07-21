"""Tests for authentication endpoints."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from flext_api.main import app


@pytest.fixture
def client() -> TestClient:
    """Create test client for authentication endpoints."""
    return TestClient(app)


def test_login_endpoint(client: TestClient) -> None:
    """Test login endpoint with valid credentials."""
    login_data = {
        "username": "test_user",
        "password": "test_password",
    }

    response = client.post("/api/v1/auth/login", json=login_data)

    assert response.status_code == 200
    data = response.json()

    assert "access_token" in data
    assert data["access_token"] == "placeholder_token"
    assert data["token_type"] == "bearer"
    assert data["expires_in"] == 3600
    assert "user" in data
    assert data["user"]["username"] == "test_user"
    assert data["user"]["roles"] == ["user"]
    assert data["user"]["is_active"] is True
    assert data["user"]["is_admin"] is False


def test_login_endpoint_with_email(client: TestClient) -> None:
    """Test login endpoint with email instead of username."""
    login_data = {
        "username": "test@example.com",  # Using email as username
        "password": "test_password",
    }

    response = client.post("/api/v1/auth/login", json=login_data)

    assert response.status_code == 200
    data = response.json()

    assert data["user"]["username"] == "test@example.com"


def test_register_endpoint(client: TestClient) -> None:
    """Test register endpoint with valid data."""
    register_data = {
        "username": "new_user",
        "email": "new_user@example.com",
        "password": "secure_password",
        "roles": ["user"],
    }

    response = client.post("/api/v1/auth/register", json=register_data)

    assert response.status_code == 200
    data = response.json()

    assert data["message"] == "User registered successfully"
    assert data["created"] is True
    assert "user" in data
    assert data["user"]["username"] == "new_user"
    assert data["user"]["roles"] == ["user"]
    assert data["user"]["is_active"] is True
    assert data["user"]["is_admin"] is False


def test_register_endpoint_without_roles(client: TestClient) -> None:
    """Test register endpoint without specifying roles."""
    register_data = {
        "username": "new_user2",
        "email": "new_user2@example.com",
        "password": "secure_password",
    }

    response = client.post("/api/v1/auth/register", json=register_data)

    assert response.status_code == 200
    data = response.json()

    assert data["user"]["roles"] == ["user"]  # Default role


def test_register_endpoint_with_admin_role(client: TestClient) -> None:
    """Test register endpoint with admin role."""
    register_data = {
        "username": "admin_user",
        "email": "admin@example.com",
        "password": "admin_password",
        "roles": ["admin", "user"],
    }

    response = client.post("/api/v1/auth/register", json=register_data)

    assert response.status_code == 200
    data = response.json()

    assert data["user"]["roles"] == ["admin", "user"]


def test_logout_endpoint(client: TestClient) -> None:
    """Test logout endpoint."""
    response = client.post("/api/v1/auth/logout")

    assert response.status_code == 200
    data = response.json()

    assert data["message"] == "Logged out successfully"
    assert data["success"] is True
    assert "timestamp" in data


def test_get_profile_endpoint(client: TestClient) -> None:
    """Test get profile endpoint."""
    response = client.get("/api/v1/auth/profile")

    assert response.status_code == 200
    data = response.json()

    assert data["username"] == "current_user"
    assert data["roles"] == ["user"]
    assert data["is_active"] is True
    assert data["is_admin"] is False


def test_login_endpoint_invalid_data(client: TestClient) -> None:
    """Test login endpoint with invalid data structure."""
    invalid_data = {
        "wrong_field": "test_user",
    }

    response = client.post("/api/v1/auth/login", json=invalid_data)

    assert response.status_code == 422  # Validation error


def test_register_endpoint_invalid_data(client: TestClient) -> None:
    """Test register endpoint with invalid data structure."""
    invalid_data = {
        "username": "test_user",
        # Missing required fields like email and password
    }

    response = client.post("/api/v1/auth/register", json=invalid_data)

    assert response.status_code == 422  # Validation error


def test_login_endpoint_missing_username(client: TestClient) -> None:
    """Test login endpoint with missing username."""
    login_data = {
        "password": "test_password",
    }

    response = client.post("/api/v1/auth/login", json=login_data)

    assert response.status_code == 422


def test_login_endpoint_missing_password(client: TestClient) -> None:
    """Test login endpoint with missing password."""
    login_data = {
        "username": "test_user",
    }

    response = client.post("/api/v1/auth/login", json=login_data)

    assert response.status_code == 422


def test_register_endpoint_missing_email(client: TestClient) -> None:
    """Test register endpoint with missing email."""
    register_data = {
        "username": "test_user",
        "password": "test_password",
    }

    response = client.post("/api/v1/auth/register", json=register_data)

    assert response.status_code == 422


def test_auth_endpoints_with_empty_strings(client: TestClient) -> None:
    """Test auth endpoints with empty string values."""
    login_data = {
        "username": "",
        "password": "",
    }

    response = client.post("/api/v1/auth/login", json=login_data)

    # Should either accept empty strings (200) or reject them (422)
    # Based on the current implementation, it should accept them
    assert response.status_code in {200, 422}


def test_register_endpoint_with_empty_roles_list(client: TestClient) -> None:
    """Test register endpoint with empty roles list."""
    register_data = {
        "username": "test_user",
        "email": "test@example.com",
        "password": "test_password",
        "roles": [],
    }

    response = client.post("/api/v1/auth/register", json=register_data)

    assert response.status_code == 200
    data = response.json()

    # Should default to ["user"] when empty list provided
    assert data["user"]["roles"] == ["user"]
