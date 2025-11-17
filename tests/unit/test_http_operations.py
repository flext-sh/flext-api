"""Tests for FlextAPI HTTP operations using real API.

Tests use FlextApi directly instead of removed FlextApiOperations stub.
"""

from __future__ import annotations

from unittest.mock import MagicMock

from flext_core import FlextResult

from flext_api import FlextApi, FlextApiModels


class TestFlextApiHttpOperations:
    """Test HTTP operations using FlextApi directly."""

    def test_get_request_using_api(self) -> None:
        """Test GET request using FlextApi directly."""
        api = FlextApi()
        original_client = api._client
        api._client = MagicMock()
        api._client.request = MagicMock(
            return_value=FlextResult[FlextApiModels.HttpResponse].ok(
                FlextApiModels.HttpResponse(status_code=200, body={"data": "test"})
            )
        )

        try:
            result = api.get("https://api.example.com/users")
            assert result.is_success
            response = result.unwrap()
            assert response.status_code == 200
        finally:
            api._client = original_client

    def test_post_request_using_api(self) -> None:
        """Test POST request using FlextApi directly."""
        api = FlextApi()
        original_client = api._client
        api._client = MagicMock()
        api._client.request = MagicMock(
            return_value=FlextResult[FlextApiModels.HttpResponse].ok(
                FlextApiModels.HttpResponse(status_code=201, body={"id": "123"})
            )
        )

        try:
            result = api.post(
                "https://api.example.com/users",
                data={"name": "John", "email": "john@example.com"},
            )
            assert result.is_success
            response = result.unwrap()
            assert response.status_code == 201
        finally:
            api._client = original_client

    def test_put_request_using_api(self) -> None:
        """Test PUT request using FlextApi directly."""
        api = FlextApi()
        original_client = api._client
        api._client = MagicMock()
        api._client.request = MagicMock(
            return_value=FlextResult[FlextApiModels.HttpResponse].ok(
                FlextApiModels.HttpResponse(status_code=200, body={"updated": True})
            )
        )

        try:
            result = api.put(
                "https://api.example.com/users/1",
                data={"name": "Jane", "email": "jane@example.com"},
            )
            assert result.is_success
            response = result.unwrap()
            assert response.status_code == 200
        finally:
            api._client = original_client

    def test_delete_request_using_api(self) -> None:
        """Test DELETE request using FlextApi directly."""
        api = FlextApi()
        original_client = api._client
        api._client = MagicMock()
        api._client.request = MagicMock(
            return_value=FlextResult[FlextApiModels.HttpResponse].ok(
                FlextApiModels.HttpResponse(status_code=204, body=None)
            )
        )

        try:
            result = api.delete("https://api.example.com/users/1")
            assert result.is_success
            response = result.unwrap()
            assert response.status_code == 204
        finally:
            api._client = original_client
