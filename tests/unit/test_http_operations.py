"""Tests for FlextAPI HTTP operations using REAL HTTP.

ALL TESTS USE REAL HTTP REQUESTS - NO MOCKS, NO PATCHES, NO BYPASSES.
Tests use httpbin.org for real HTTP endpoint testing.
"""

from __future__ import annotations

import pytest

from flext_api import FlextApi


class TestFlextApiHttpOperations:
    """Test HTTP operations using FlextApi with REAL HTTP requests."""

    @pytest.mark.network
    def test_get_request_using_api(self) -> None:
        """Test GET request using FlextApi with real HTTP."""
        api = FlextApi()
        result = api.get("https://httpbin.org/get")

        # If httpbin is unavailable, skip test but verify error handling works
        if not result.is_success and (
            "connection" in result.error.lower() or "refused" in result.error.lower()
        ):
            pytest.skip(f"httpbin.org unavailable: {result.error}")

        assert result.is_success, f"Request failed: {result.error}"
        response = result.unwrap()
        assert response.status_code == 200
        assert isinstance(response.body, dict)

    @pytest.mark.network
    def test_post_request_using_api(self) -> None:
        """Test POST request using FlextApi with real HTTP."""
        api = FlextApi()
        result = api.post(
            "https://httpbin.org/post",
            data={"name": "John", "email": "john@example.com"},
        )

        if not result.is_success and (
            "connection" in result.error.lower() or "refused" in result.error.lower()
        ):
            pytest.skip(f"httpbin.org unavailable: {result.error}")

        assert result.is_success, f"Request failed: {result.error}"
        response = result.unwrap()
        assert response.status_code == 200
        assert isinstance(response.body, dict)
        # httpbin returns posted data in json field
        posted_data = response.body.get("json", {})
        assert posted_data.get("name") == "John"
        assert posted_data.get("email") == "john@example.com"

    @pytest.mark.network
    def test_put_request_using_api(self) -> None:
        """Test PUT request using FlextApi with real HTTP."""
        api = FlextApi()
        result = api.put(
            "https://httpbin.org/put",
            data={"name": "Jane", "email": "jane@example.com"},
        )

        if not result.is_success and (
            "connection" in result.error.lower() or "refused" in result.error.lower()
        ):
            pytest.skip(f"httpbin.org unavailable: {result.error}")

        assert result.is_success, f"Request failed: {result.error}"
        response = result.unwrap()
        assert response.status_code == 200
        assert isinstance(response.body, dict)

    @pytest.mark.network
    def test_delete_request_using_api(self) -> None:
        """Test DELETE request using FlextApi with real HTTP."""
        api = FlextApi()
        result = api.delete("https://httpbin.org/delete")

        if not result.is_success and (
            "connection" in result.error.lower() or "refused" in result.error.lower()
        ):
            pytest.skip(f"httpbin.org unavailable: {result.error}")

        assert result.is_success, f"Request failed: {result.error}"
        response = result.unwrap()
        assert response.status_code == 200
        # DELETE may return empty body or None
        assert response.body is None or isinstance(response.body, dict)
