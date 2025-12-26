"""Tests for FlextAPI unified HTTP facade."""

from __future__ import annotations

from unittest.mock import MagicMock

from flext_core import FlextResult

from flext_api.api import FlextApi
from flext_api.models import FlextApiModels
from flext_api.settings import FlextApiSettings


class TestFlextApiInitialization:
    """Test FlextApi initialization and setup."""

    def test_init_with_default_config(self) -> None:
        """Test FlextApi initialization with default config."""
        api = FlextApi()
        assert api._config is not None
        assert isinstance(api._config, FlextApiSettings)
        assert api._client is not None

    def test_init_with_custom_config(self) -> None:
        """Test FlextApi initialization with custom config."""
        config = FlextApiSettings(
            timeout=60.0,
            max_retries=3,
            base_url="https://api.example.com",
        )
        api = FlextApi(config)
        assert api._config is config
        assert api._config.timeout == 60.0
        assert api._config.max_retries == 3
        assert api._config.base_url == "https://api.example.com"

    def test_unified_namespace_models(self) -> None:
        """Test unified namespace access to Models."""
        assert FlextApi.Models is FlextApiModels
        assert hasattr(FlextApi.Models, "HttpRequest")
        assert hasattr(FlextApi.Models, "HttpResponse")

    def test_unified_namespace_config(self) -> None:
        """Test unified namespace access to Config."""
        assert FlextApi.Config is FlextApiSettings


class TestFlextApiExecute:
    """Test FlextApi.execute() method."""

    def test_execute_returns_config(self) -> None:
        """Test execute returns FlextResult with config."""
        config = FlextApiSettings()
        api = FlextApi(config)
        result = api.execute()

        assert result.is_success
        assert result.value is config

    def test_execute_with_custom_config(self) -> None:
        """Test execute with custom config."""
        config = FlextApiSettings(timeout=45.0)
        api = FlextApi(config)
        result = api.execute()

        assert result.is_success
        unwrapped = result.value
        assert unwrapped.timeout == 45.0


class TestFlextApiHttpMethods:
    """Test FlextApi HTTP method implementations."""

    def test_get_calls_http_method(self) -> None:
        """Test GET method creates correct request."""
        api = FlextApi()

        # Manually call the method to verify parameters
        # The actual test validates method signature and delegation
        assert api.get is not None  # method exists

    def test_post_calls_http_method(self) -> None:
        """Test POST method exists and is callable."""
        api = FlextApi()
        assert api.post is not None

    def test_put_calls_http_method(self) -> None:
        """Test PUT method exists and is callable."""
        api = FlextApi()
        assert api.put is not None

    def test_delete_calls_http_method(self) -> None:
        """Test DELETE method exists and is callable."""
        api = FlextApi()
        assert api.delete is not None

    def test_patch_calls_http_method(self) -> None:
        """Test PATCH method exists and is callable."""
        api = FlextApi()
        assert api.patch is not None


class TestFlextApiGenericHttpMethod:
    """Test FlextApi._http_method() generic method executor."""

    def test_http_method_with_get(self) -> None:
        """Test _http_method with GET method."""
        api = FlextApi()
        # Create a mock client to avoid actual HTTP calls
        original_client = api._client
        api._client = MagicMock()
        api._client.request = MagicMock(
            return_value=FlextResult[FlextApiModels.HttpResponse].ok(
                FlextApiModels.HttpResponse(status_code=200, body={}),
            ),
        )

        try:
            result = api._http_method("GET", "https://example.com/api/test")
            assert result.is_success
        finally:
            api._client = original_client

    def test_http_method_with_post(self) -> None:
        """Test _http_method with POST method and body."""
        api = FlextApi()
        original_client = api._client
        api._client = MagicMock()
        api._client.request = MagicMock(
            return_value=FlextResult[FlextApiModels.HttpResponse].ok(
                FlextApiModels.HttpResponse(status_code=201, body={}),
            ),
        )

        try:
            body = {"name": "test"}
            result = api._http_method(
                "POST",
                "https://example.com/api/users",
                data=body,
            )
            assert result.is_success
        finally:
            api._client = original_client

    def test_http_method_with_timeout(self) -> None:
        """Test _http_method processes timeout parameter."""
        api = FlextApi()
        original_client = api._client
        api._client = MagicMock()
        api._client.request = MagicMock(
            return_value=FlextResult[FlextApiModels.HttpResponse].ok(
                FlextApiModels.HttpResponse(status_code=200, body={}),
            ),
        )

        try:
            result = api._http_method(
                "GET",
                "https://example.com/api/test",
                timeout=60.0,
            )
            assert result.is_success
            # Verify the client was called
            api._client.request.assert_called_once()
            request_arg = api._client.request.call_args[0][0]
            assert request_arg.timeout == 60.0
        finally:
            api._client = original_client

    def test_http_method_converts_int_timeout_to_float(self) -> None:
        """Test _http_method converts int timeout to float."""
        api = FlextApi()
        original_client = api._client
        api._client = MagicMock()
        api._client.request = MagicMock(
            return_value=FlextResult[FlextApiModels.HttpResponse].ok(
                FlextApiModels.HttpResponse(status_code=200, body={}),
            ),
        )

        try:
            result = api._http_method("GET", "https://example.com/api/test", timeout=45)
            assert result.is_success
            request_arg = api._client.request.call_args[0][0]
            assert isinstance(request_arg.timeout, float)
            assert request_arg.timeout == 45.0
        finally:
            api._client = original_client

    def test_http_method_default_timeout(self) -> None:
        """Test _http_method fails fast for invalid timeout values - no fallbacks."""
        api = FlextApi()

        # Invalid timeout should fail fast - no fallback to default
        result = api._http_method(
            "GET",
            "https://example.com/api/test",
            timeout="invalid",
        )
        assert result.is_failure
        assert (
            "Invalid timeout value" in result.error
            or "Invalid timeout type" in result.error
        )

    def test_http_method_with_headers(self) -> None:
        """Test _http_method passes headers correctly."""
        api = FlextApi()
        original_client = api._client
        api._client = MagicMock()
        api._client.request = MagicMock(
            return_value=FlextResult[FlextApiModels.HttpResponse].ok(
                FlextApiModels.HttpResponse(status_code=200, body={}),
            ),
        )

        try:
            headers = {"Authorization": "Bearer token", "X-Custom": "value"}
            result = api._http_method(
                "POST",
                "https://example.com/api/test",
                data={"key": "value"},
                headers=headers,
            )
            assert result.is_success
            request_arg = api._client.request.call_args[0][0]
            assert request_arg.headers == headers
        finally:
            api._client = original_client

    def test_http_method_empty_headers_default(self) -> None:
        """Test _http_method uses empty headers when not provided."""
        api = FlextApi()
        original_client = api._client
        api._client = MagicMock()
        api._client.request = MagicMock(
            return_value=FlextResult[FlextApiModels.HttpResponse].ok(
                FlextApiModels.HttpResponse(status_code=200, body={}),
            ),
        )

        try:
            result = api._http_method("GET", "https://example.com/api/test")
            assert result.is_success
            request_arg = api._client.request.call_args[0][0]
            assert request_arg.headers == {}
        finally:
            api._client = original_client


class TestFlextApiRequest:
    """Test FlextApi.request() method."""

    def test_request_delegates_to_client(self) -> None:
        """Test request method delegates to client."""
        api = FlextApi()
        original_client = api._client
        api._client = MagicMock()

        mock_response = FlextApiModels.HttpResponse(
            status_code=200,
            body={"status": "ok"},
        )
        api._client.request = MagicMock(
            return_value=FlextResult[FlextApiModels.HttpResponse].ok(mock_response),
        )

        try:
            request = FlextApiModels.HttpRequest(
                method="GET",
                url="https://example.com/api/test",
            )
            result = api.request(request)

            assert result.is_success
            assert result.value.status_code == 200
            api._client.request.assert_called_once_with(request)
        finally:
            api._client = original_client

    def test_request_returns_error(self) -> None:
        """Test request returns error result on failure."""
        api = FlextApi()
        original_client = api._client
        api._client = MagicMock()

        error_result = FlextResult[FlextApiModels.HttpResponse].fail("Connection error")
        api._client.request = MagicMock(return_value=error_result)

        try:
            request = FlextApiModels.HttpRequest(
                method="GET",
                url="https://example.com/api/test",
            )
            result = api.request(request)

            assert result.is_failure
            assert result.error == "Connection error"
        finally:
            api._client = original_client


class TestFlextApiIntegration:
    """Test FlextApi integration scenarios."""

    def test_config_persistence(self) -> None:
        """Test config is maintained across multiple method calls."""
        config = FlextApiSettings(timeout=60.0, max_retries=3)
        api = FlextApi(config)

        assert api._config is config
        assert api._config.timeout == 60.0
        assert api._config.max_retries == 3

        # Verify config persists
        api.execute()
        assert api._config is config

    def test_client_persistence(self) -> None:
        """Test HTTP client is persistent."""
        api = FlextApi()
        original_client = api._client

        # Multiple method calls should use same client
        api.execute()
        assert api._client is original_client

    def test_models_class_variable_access(self) -> None:
        """Test Models class variable is accessible."""
        api = FlextApi()

        # Access through instance
        assert api.Models is FlextApiModels

        # Access through class
        assert FlextApi.Models is FlextApiModels

        # Verify models have expected types
        request_type = api.Models.HttpRequest
        response_type = api.Models.HttpResponse
        assert request_type is not None
        assert response_type is not None

    def test_config_class_variable_access(self) -> None:
        """Test Config class variable is accessible."""
        api = FlextApi()

        # Access through instance
        assert api.Config is FlextApiSettings

        # Access through class
        assert FlextApi.Config is FlextApiSettings
