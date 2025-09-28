"""Tests for FlextApiClient HTTP methods to improve coverage."""

from unittest.mock import patch

import pytest
from flext_core.result import FlextResult

from flext_api import FlextApiClient


class TestFlextApiClientHttpMethods:
    """Tests for FlextApiClient HTTP methods to improve coverage."""

    @pytest.mark.asyncio
    async def test_client_get_method(self) -> None:
        """Test client GET method."""
        client = FlextApiClient()

        with patch.object(client, "_request") as mock_request:
            mock_response = FlextResult[object].ok({"status": "success"})
            mock_request.return_value = mock_response

            result = await client.get("/test")

            assert result.is_success
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert call_args[0][0] == "GET"  # method
            assert call_args[0][1] == "/test"  # url

    @pytest.mark.asyncio
    async def test_client_get_method_with_params(self) -> None:
        """Test client GET method with parameters."""
        client = FlextApiClient()

        with patch.object(client, "_request") as mock_request:
            mock_response = FlextResult[object].ok({"status": "success"})
            mock_request.return_value = mock_response

            result = await client.get("/test", params={"key": "value"})

            assert result.is_success
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert call_args[1]["params"] == {"key": "value"}

    @pytest.mark.asyncio
    async def test_client_post_method(self) -> None:
        """Test client POST method."""
        client = FlextApiClient()

        with patch.object(client, "_request") as mock_request:
            mock_response = FlextResult[object].ok({"status": "success"})
            mock_request.return_value = mock_response

            result = await client.post("/test")

            assert result.is_success
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert call_args[0][0] == "POST"  # method
            assert call_args[0][1] == "/test"  # url

    @pytest.mark.asyncio
    async def test_client_post_method_with_json(self) -> None:
        """Test client POST method with JSON data."""
        client = FlextApiClient()

        with patch.object(client, "_request") as mock_request:
            mock_response = FlextResult[object].ok({"status": "success"})
            mock_request.return_value = mock_response

            json_data = {"name": "test", "value": 123}
            result = await client.post("/test", json=json_data)

            assert result.is_success
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert call_args[1]["json"] == json_data

    @pytest.mark.asyncio
    async def test_client_put_method(self) -> None:
        """Test client PUT method."""
        client = FlextApiClient()

        with patch.object(client, "_request") as mock_request:
            mock_response = FlextResult[object].ok({"status": "success"})
            mock_request.return_value = mock_response

            result = await client.put("/test")

            assert result.is_success
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert call_args[0][0] == "PUT"  # method
            assert call_args[0][1] == "/test"  # url

    @pytest.mark.asyncio
    async def test_client_put_method_with_data(self) -> None:
        """Test client PUT method with data."""
        client = FlextApiClient()

        with patch.object(client, "_request") as mock_request:
            mock_response = FlextResult[object].ok({"status": "success"})
            mock_request.return_value = mock_response

            data = {"field": "value"}
            result = await client.put("/test", data=data)

            assert result.is_success
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert call_args[1]["data"] == data

    @pytest.mark.asyncio
    async def test_client_delete_method(self) -> None:
        """Test client DELETE method."""
        client = FlextApiClient()

        with patch.object(client, "_request") as mock_request:
            mock_response = FlextResult[object].ok({"status": "success"})
            mock_request.return_value = mock_response

            result = await client.delete("/test")

            assert result.is_success
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert call_args[0][0] == "DELETE"  # method
            assert call_args[0][1] == "/test"  # url

    @pytest.mark.asyncio
    async def test_client_delete_method_with_headers(self) -> None:
        """Test client DELETE method with headers."""
        client = FlextApiClient()

        with patch.object(client, "_request") as mock_request:
            mock_response = FlextResult[object].ok({"status": "success"})
            mock_request.return_value = mock_response

            headers = {"Authorization": "Bearer token"}
            result = await client.delete("/test", headers=headers)

            assert result.is_success
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert call_args[1]["headers"] == headers

    @pytest.mark.asyncio
    async def test_client_patch_method(self) -> None:
        """Test client PATCH method."""
        client = FlextApiClient()

        with patch.object(client, "_request") as mock_request:
            mock_response = FlextResult[object].ok({"status": "success"})
            mock_request.return_value = mock_response

            result = await client.patch("/test")

            assert result.is_success
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert call_args[0][0] == "PATCH"  # method
            assert call_args[0][1] == "/test"  # url

    @pytest.mark.asyncio
    async def test_client_patch_method_with_timeout(self) -> None:
        """Test client PATCH method with timeout."""
        client = FlextApiClient()

        with patch.object(client, "_request") as mock_request:
            mock_response = FlextResult[object].ok({"status": "success"})
            mock_request.return_value = mock_response

            result = await client.patch("/test", request_timeout=30)

            assert result.is_success
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert call_args[1]["request_timeout"] == 30

    @pytest.mark.asyncio
    async def test_client_http_methods_with_complex_params(self) -> None:
        """Test client HTTP methods with complex parameters."""
        client = FlextApiClient()

        with patch.object(client, "_request") as mock_request:
            mock_response = FlextResult[object].ok({"status": "success"})
            mock_request.return_value = mock_response

            # Test with multiple parameters
            result = await client.post(
                "/test",
                params={"page": 1, "limit": 10},
                json={"name": "test"},
                headers={"Content-Type": "application/json"},
                request_timeout=60,
            )

            assert result.is_success
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert call_args[1]["params"] == {"page": 1, "limit": 10}
            assert call_args[1]["json"] == {"name": "test"}
            assert call_args[1]["headers"] == {"Content-Type": "application/json"}
            assert call_args[1]["request_timeout"] == 60

    @pytest.mark.asyncio
    async def test_client_http_methods_error_handling(self) -> None:
        """Test client HTTP methods error handling."""
        client = FlextApiClient()

        with patch.object(client, "_request") as mock_request:
            mock_response = FlextResult[object].fail("Request failed")
            mock_request.return_value = mock_response

            result = await client.get("/test")

            assert result.is_failure
            assert result.error == "Request failed"

    @pytest.mark.asyncio
    async def test_client_extract_kwargs_method(self) -> None:
        """Test client _extract_kwargs method."""
        client = FlextApiClient()

        kwargs = {
            "params": {"key": "value"},
            "data": {"field": "data"},
            "json": {"json_field": "json_value"},
            "headers": {"Authorization": "Bearer token"},
            "request_timeout": 30,
            "unknown_param": "should_be_ignored",
        }

        extracted = client._extract_kwargs(kwargs)

        assert isinstance(extracted, dict)
        assert "params" in extracted
        assert "data" in extracted
        assert "json" in extracted
        assert "headers" in extracted
        assert "request_timeout" in extracted
        assert extracted["params"] == {"key": "value"}
        assert extracted["data"] == {"field": "data"}
        assert extracted["json"] == {"json_field": "json_value"}
        assert extracted["headers"] == {"Authorization": "Bearer token"}
        assert extracted["request_timeout"] == 30

    @pytest.mark.asyncio
    async def test_client_extract_kwargs_empty(self) -> None:
        """Test client _extract_kwargs with empty kwargs."""
        client = FlextApiClient()

        extracted = client._extract_kwargs({})

        assert isinstance(extracted, dict)
        # _extract_kwargs returns dict with None values for all expected keys
        assert (
            len(extracted) == 6
        )  # params, data, json, headers, request_timeout, timeout

    @pytest.mark.asyncio
    async def test_client_extract_kwargs_invalid_input(self) -> None:
        """Test client _extract_kwargs with invalid input."""
        client = FlextApiClient()

        # Test with non-dict input - this should cause an AttributeError
        with pytest.raises(AttributeError):
            client._extract_kwargs("not_a_dict")

    def test_client_http_methods_exist(self) -> None:
        """Test that client has expected HTTP methods."""
        client = FlextApiClient()

        expected_methods = ["get", "post", "put", "delete", "patch", "_extract_kwargs"]

        for method in expected_methods:
            assert hasattr(client, method), f"Client missing method: {method}"
            assert callable(getattr(client, method)), (
                f"Client method {method} is not callable"
            )

    @pytest.mark.asyncio
    async def test_client_http_methods_with_none_values(self) -> None:
        """Test client HTTP methods with None values in kwargs."""
        client = FlextApiClient()

        with patch.object(client, "_request") as mock_request:
            mock_response = FlextResult[object].ok({"status": "success"})
            mock_request.return_value = mock_response

            result = await client.post(
                "/test", params=None, json=None, headers=None, request_timeout=None
            )

            assert result.is_success
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert call_args[1]["params"] is None
            assert call_args[1]["json"] is None
            assert call_args[1]["headers"] is None
            assert call_args[1]["request_timeout"] is None
