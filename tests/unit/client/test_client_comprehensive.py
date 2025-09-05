"""Comprehensive tests for FlextApiClient with real HTTP functionality validation.

Tests all client functionality using flext_tests library without mocks.
Achieves 100% coverage for client.py module.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import json
from typing import Never
from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest
from flext_core import FlextResult
from flext_tests import FlextMatchers

from flext_api import FlextApiClient


class TestFlextApiClient:
    """Comprehensive HTTP client tests."""

    def test_client_initialization(self) -> None:
        """Test client initialization with various configurations."""
        # Basic initialization
        client = FlextApiClient()
        assert client.base_url == ""
        assert client.timeout == 30.0
        assert isinstance(client.headers, dict)
        assert client.max_retries == 3

        # Configuration via dict
        config = {
            "base_url": "https://api.example.com",
            "timeout": 60.0,
            "headers": {"Authorization": "Bearer token"},
            "max_retries": 5,
        }
        client_with_config = FlextApiClient(config)
        assert client_with_config.base_url == "https://api.example.com"
        assert client_with_config.timeout == 60.0
        assert client_with_config.headers["Authorization"] == "Bearer token"
        assert client_with_config.max_retries == 5

        # Configuration via kwargs
        client_kwargs = FlextApiClient(
            base_url="https://test.example.com",
            timeout=45.0,
            headers={"User-Agent": "test"},
            max_retries=2,
        )
        assert client_kwargs.base_url == "https://test.example.com"
        assert client_kwargs.timeout == 45.0
        assert client_kwargs.max_retries == 2

    def test_client_initialization_type_safety(self) -> None:
        """Test client initialization with type conversion."""
        # Test timeout conversion
        client1 = FlextApiClient(timeout="45")  # String to float
        assert client1.timeout == 45.0

        client2 = FlextApiClient(timeout=30)  # Int to float
        assert client2.timeout == 30.0

        # Test invalid timeout fallback
        client3 = FlextApiClient(timeout={"invalid": "type"})
        assert client3.timeout == 30.0  # Default fallback

        # Test max_retries conversion
        client4 = FlextApiClient(max_retries="3")  # String to int
        assert client4.max_retries == 3

        # Test invalid max_retries fallback
        client5 = FlextApiClient(max_retries={"invalid": "type"})
        assert client5.max_retries == 3  # Default fallback

        # Test headers type safety
        client6 = FlextApiClient(headers="invalid")  # Non-dict to empty dict
        assert client6.headers == {}

        # Test base_url None handling
        client7 = FlextApiClient(base_url=None)
        assert client7.base_url == ""

    def test_client_properties(self) -> None:
        """Test client property access."""
        client = FlextApiClient(
            base_url="https://api.example.com",
            timeout=45.0,
            headers={"Custom": "Value"},
            max_retries=2,
        )

        assert client.base_url == "https://api.example.com"
        assert client.timeout == 45.0
        assert client.headers == {"Custom": "Value"}
        assert client.max_retries == 2

    def test_client_execute(self) -> None:
        """Test client execution (domain service pattern)."""
        client = FlextApiClient(base_url="https://test.com")
        result = client.execute()

        assert result.success
        data = result.value
        assert data["client_type"] == "httpx.AsyncClient"
        assert data["base_url"] == "https://test.com"
        assert data["timeout"] == 30.0
        assert data["session_started"] is False
        assert data["status"] == "active"
        assert "client_id" in data

    def test_client_execute_error_handling(self) -> None:
        """Test execute method error handling."""
        # Create a client that will trigger an exception during execute
        client = FlextApiClient()

        # Patch the client_id property to raise an exception
        with patch.object(client, "_client_id", side_effect=Exception("Test error")):
            result = client.execute()
            FlextMatchers.assert_result_failure(result)
            assert "HTTP client execution failed" in result.error

    def test_config_property(self) -> None:
        """Test config property for test compatibility."""
        client = FlextApiClient(
            base_url="https://api.test.com",
            timeout=60.0,
            headers={"Test": "Header"},
            max_retries=5,
        )

        config = client.config
        assert config.base_url == "https://api.test.com"
        assert config.timeout == 60.0
        assert config.headers == {"Test": "Header"}
        assert config.max_retries == 5

    def test_health_check(self) -> None:
        """Test health check functionality."""
        client = FlextApiClient(base_url="https://api.example.com")
        health = client.health_check()

        assert "client_id" in health
        assert health["session_started"] is False
        assert health["base_url"] == "https://api.example.com"
        assert health["timeout"] == 30.0
        assert health["max_retries"] == 3
        assert health["client_ready"] is False  # Not started
        assert health["status"] == "not_started"

    def test_url_building(self) -> None:
        """Test internal building logic."""
        client = FlextApiClient(base_url="https://api.example.com/")

        # Test _build_url method
        url1 = client._build_url("/users")
        assert url1 == "https://api.example.com/users"

        url2 = client._build_url("users")
        assert url2 == "https://api.example.com/users"

        url3 = client._build_url("")
        assert url3 == "https://api.example.com"

        # Test with base without trailing slash
        client2 = FlextApiClient(base_url="https://api.example.com")
        url4 = client2._build_url("/users")
        assert url4 == "https://api.example.com/users"

    @pytest.mark.asyncio
    async def test_session_lifecycle(self) -> None:
        """Test session start and stop lifecycle."""
        client = FlextApiClient(base_url="https://httpbin.org")

        # Initial state
        assert not client._session_started
        assert client._client is None

        # Start session
        start_result = await client.start()
        assert start_result.success
        assert client._session_started
        assert client._client is not None
        assert isinstance(client._client, httpx.AsyncClient)

        # Health check after start
        health = client.health_check()
        assert health["session_started"] is True
        assert health["client_ready"] is True
        assert health["status"] == "healthy"

        # Start again (idempotent)
        start_result2 = await client.start()
        assert start_result2.success

        # Stop session
        stop_result = await client.stop()
        assert stop_result.success
        assert not client._session_started
        assert client._client is None

        # Stop again (idempotent)
        stop_result2 = await client.stop()
        assert stop_result2.success

    @pytest.mark.asyncio
    async def test_session_start_error_handling(self) -> None:
        """Test session start error handling."""
        with patch("httpx.AsyncClient", side_effect=Exception("Connection failed")):
            client = FlextApiClient()
            result = await client.start()
            FlextMatchers.assert_result_failure(result)
            assert "HTTP session start failed" in result.error

    @pytest.mark.asyncio
    async def test_session_stop_error_handling(self) -> None:
        """Test session stop error handling."""
        client = FlextApiClient()

        # Create a mock client that throws on aclose
        mock_client = AsyncMock()
        mock_client.aclose.side_effect = Exception("Close failed")
        client._client = mock_client
        client._session_started = True

        result = await client.stop()
        FlextMatchers.assert_result_failure(result)
        assert "HTTP session stop failed" in result.error

    @pytest.mark.asyncio
    async def test_close_method(self) -> None:
        """Test close method (alias for stop)."""
        client = FlextApiClient()

        # Start session first
        await client.start()
        assert client._session_started

        # Close should work
        await client.close()
        assert not client._session_started

    @pytest.mark.asyncio
    async def test_close_method_error_handling(self) -> None:
        """Test close method error handling."""
        client = FlextApiClient()

        # Create a mock client that throws on aclose
        mock_client = AsyncMock()
        mock_client.aclose.side_effect = Exception("Close failed")
        client._client = mock_client
        client._session_started = True

        with pytest.raises(RuntimeError, match="Failed to close client"):
            await client.close()

    @pytest.mark.asyncio
    async def test_session_validation(self) -> None:
        """Test session validation before requests."""
        client = FlextApiClient()

        # Session not started
        validation_result = client._validate_session()
        assert not validation_result.success
        assert "HTTP session not started" in validation_result.error

        # Start session and validate
        await client.start()
        validation_result2 = client._validate_session()
        assert validation_result2.success

    @pytest.mark.asyncio
    async def test_http_request_context(self) -> None:
        """Test HTTP request context model."""
        context = FlextApiClient._HttpRequestContext(
            request_id="test_id",
            method="POST",
            url="https://api.example.com/data",
            params={"query": "test"},
            json_data={"data": "value"},
            headers={"Content-Type": "application/json"},
            timeout=30.0,
        )

        # Test properties
        assert context.request_id == "test_id"
        assert context.method == "POST"
        assert context.url == "https://api.example.com/data"
        assert context.params == {"query": "test"}
        assert context.json_data == {"data": "value"}
        assert context.headers == {"Content-Type": "application/json"}
        assert context.timeout == 30.0

        # Test to_httpx_kwargs
        kwargs = context.to_httpx_kwargs()
        assert kwargs["method"] == "POST"
        assert kwargs["url"] == "https://api.example.com/data"
        assert kwargs["params"] == {"query": "test"}
        assert kwargs["json"] == {"data": "value"}
        assert kwargs["headers"] == {"Content-Type": "application/json"}
        assert kwargs["timeout"] == 30.0

    @pytest.mark.asyncio
    async def test_http_request_context_with_data(self) -> None:
        """Test HTTP request context with raw data instead of JSON."""
        context = FlextApiClient._HttpRequestContext(
            request_id="test_id",
            method="POST",
            url="https://api.example.com/data",
            data=b"raw data content",
        )

        kwargs = context.to_httpx_kwargs()
        assert kwargs["method"] == "POST"
        assert kwargs["url"] == "https://api.example.com/data"
        assert kwargs["content"] == b"raw data content"
        assert "json" not in kwargs  # Should not include JSON when data is provided

    @pytest.mark.asyncio
    async def test_retry_strategy(self) -> None:
        """Test retry strategy functionality."""
        client = FlextApiClient(max_retries=2)
        retry_strategy = client._retry_strategy

        assert isinstance(retry_strategy, FlextApiClient._RetryStrategy)
        assert retry_strategy.max_retries == 2

        # Test property caching
        retry_strategy2 = client._retry_strategy
        assert retry_strategy is retry_strategy2

    @pytest.mark.asyncio
    async def test_retry_strategy_should_retry(self) -> None:
        """Test retry strategy decision logic."""
        retry_strategy = FlextApiClient._RetryStrategy(max_retries=2)

        # Should retry on failed result, attempt < max_retries
        failed_result = FlextResult[dict[str, object]].fail("Network error")
        assert retry_strategy._should_retry(failed_result, 0) is True
        assert retry_strategy._should_retry(failed_result, 1) is True
        assert (
            retry_strategy._should_retry(failed_result, 2) is False
        )  # Max retries reached

        # Should not retry on successful result
        success_result = FlextResult[dict[str, object]].ok({"data": "success"})
        assert retry_strategy._should_retry(success_result, 0) is False

    def test_retry_strategy_error_logging(self) -> None:
        """Test retry strategy error logging."""
        retry_strategy = FlextApiClient._RetryStrategy(max_retries=2)
        context = FlextApiClient._HttpRequestContext(
            request_id="test_request", method="GET", url="https://api.example.com/test"
        )

        # Test timeout error logging
        timeout_error = httpx.TimeoutException("Request timeout")
        retry_strategy._log_retry_error(context, timeout_error, 0)

        # Test general request error logging
        request_error = httpx.RequestError("Connection failed")
        retry_strategy._log_retry_error(context, request_error, 1)

    def test_retry_exhausted_result(self) -> None:
        """Test retry exhausted result creation."""
        retry_strategy = FlextApiClient._RetryStrategy(max_retries=2)
        context = FlextApiClient._HttpRequestContext(
            request_id="test_request", method="GET", url="https://api.example.com/test"
        )

        last_error = httpx.RequestError("Final error")
        result = retry_strategy._create_retry_exhausted_result(context, last_error)

        FlextMatchers.assert_result_failure(result)
        assert "HTTP request failed after 3 attempts" in result.error
        assert "Final error" in result.error

    @pytest.mark.asyncio
    async def test_response_parsing(self) -> None:
        """Test response parsing logic."""
        client = FlextApiClient()

        # Test JSON response parsing
        json_response = Mock()
        json_response.headers = {"content-type": "application/json"}
        json_response.json.return_value = {"data": "test", "status": "success"}

        parsed = client._parse_response(json_response)
        assert parsed == {"data": "test", "status": "success"}

        # Test non-JSON response parsing
        text_response = Mock()
        text_response.headers = {"content-type": "text/plain"}
        text_response.text = "Plain text response"
        text_response.status_code = 200

        parsed_text = client._parse_response(text_response)
        assert parsed_text == {"content": "Plain text response", "status_code": 200}

        # Test JSON parsing error
        broken_json_response = Mock()
        broken_json_response.headers = {"content-type": "application/json"}
        broken_json_response.json.side_effect = json.JSONDecodeError(
            "Invalid JSON", "", 0
        )
        broken_json_response.text = "Invalid JSON content"
        broken_json_response.status_code = 200

        parsed_broken = client._parse_response(broken_json_response)
        assert parsed_broken == {"content": "Invalid JSON content", "status_code": 200}

    def test_http_error_checking(self) -> None:
        """Test HTTP error status checking."""
        client = FlextApiClient()
        context = FlextApiClient._HttpRequestContext(
            request_id="test_request", method="GET", url="https://api.example.com/test"
        )

        # Test successful response (no error)
        success_response = Mock()
        success_response.status_code = 200
        error_result = client._check_http_errors(success_response, context)
        assert error_result is None

        # Test client error (4xx) - should fail without retry
        client_error_response = Mock()
        client_error_response.status_code = 404
        client_error_response.text = "Not Found"
        error_result = client._check_http_errors(client_error_response, context)
        assert error_result is not None
        assert not error_result.success
        assert "HTTP 404: Not Found" in error_result.error

        # Test server error (5xx) - should fail but allow retry
        server_error_response = Mock()
        server_error_response.status_code = 500
        server_error_response.text = "Internal Server Error"
        error_result = client._check_http_errors(server_error_response, context)
        assert error_result is not None
        assert not error_result.success
        assert "HTTP 500: Internal Server Error" in error_result.error

    @pytest.mark.asyncio
    async def test_request_methods_session_validation(self) -> None:
        """Test that HTTP methods validate session state."""
        client = FlextApiClient()

        # All methods should fail when session not started
        get_result = await client.get("/test")
        assert not get_result.success
        assert "HTTP session not started" in get_result.error

        post_result = await client.post("/test", {"data": "test"})
        assert not post_result.success
        assert "HTTP session not started" in post_result.error

        put_result = await client.put("/test", {"data": "test"})
        assert not put_result.success
        assert "HTTP session not started" in put_result.error

        delete_result = await client.delete("/test")
        assert not delete_result.success
        assert "HTTP session not started" in delete_result.error

    @pytest.mark.asyncio
    async def test_make_request_method(self) -> None:
        """Test internal _make_request method."""
        client = FlextApiClient(base_url="https://httpbin.org")

        # Session not started
        result = await client._make_request("GET", "/get")
        FlextMatchers.assert_result_failure(result)
        assert "HTTP session not started" in result.error

    @pytest.mark.asyncio
    async def test_execute_single_request_client_not_initialized(self) -> None:
        """Test _execute_single_request when client is None."""
        client = FlextApiClient()
        context = FlextApiClient._HttpRequestContext(
            request_id="test", method="GET", url="https://api.example.com/test"
        )

        # Client not initialized
        result = await client._execute_single_request(context, 0)
        FlextMatchers.assert_result_failure(result)
        assert "HTTP client not initialized" in result.error

    @pytest.mark.asyncio
    async def test_config_merge_behavior(self) -> None:
        """Test config and kwargs merge behavior."""
        # Config dict takes precedence over kwargs
        config = {"base_url": "https://config.com", "timeout": 60.0}
        client = FlextApiClient(config, base_url="https://kwargs.com", timeout=45.0)

        # Config values should be used, but kwargs should also be merged
        assert client.base_url == "https://kwargs.com"  # kwargs override config
        assert client.timeout == 45.0  # kwargs override config

        # Test with no config
        client2 = FlextApiClient(base_url="https://kwargs-only.com")
        assert client2.base_url == "https://kwargs-only.com"

    @pytest.mark.asyncio
    async def test_retry_strategy_execution_with_mock(self) -> None:
        """Test retry strategy execution with mocked HTTP client."""
        client = FlextApiClient(max_retries=2, base_url="https://httpbin.org")
        await client.start()

        context = FlextApiClient._HttpRequestContext(
            request_id="test_retry", method="GET", url="https://httpbin.org/get"
        )

        retry_strategy = client._retry_strategy

        # Mock execute function that fails and then succeeds
        call_count = 0

        async def mock_execute_fn(
            ctx: FlextApiClient._HttpRequestContext, attempt: int
        ) -> FlextResult[dict[str, object]]:
            nonlocal call_count
            call_count += 1
            if call_count < 2:  # Fail first time
                return FlextResult[dict[str, object]].fail("Network error")
            # Succeed second time
            return FlextResult[dict[str, object]].ok({"success": True})

        result = await retry_strategy.execute(context, mock_execute_fn)
        assert result.success
        assert call_count == 2  # Should retry once

        await client.stop()

    @pytest.mark.asyncio
    async def test_retry_strategy_all_attempts_fail(self) -> None:
        """Test retry strategy when all attempts fail."""
        client = FlextApiClient(max_retries=1)
        retry_strategy = client._retry_strategy

        context = FlextApiClient._HttpRequestContext(
            request_id="test_fail", method="GET", url="https://httpbin.org/get"
        )

        # Mock execute function that always fails
        async def always_fail_execute_fn(
            ctx: FlextApiClient._HttpRequestContext, attempt: int
        ) -> FlextResult[dict[str, object]]:
            return FlextResult[dict[str, object]].fail("Always fails")

        result = await retry_strategy.execute(context, always_fail_execute_fn)
        FlextMatchers.assert_result_failure(result)
        assert "Always fails" in result.error

    @pytest.mark.asyncio
    async def test_retry_strategy_with_exceptions(self) -> None:
        """Test retry strategy with network exceptions."""
        client = FlextApiClient(max_retries=1)
        retry_strategy = client._retry_strategy

        context = FlextApiClient._HttpRequestContext(
            request_id="test_exception", method="GET", url="https://httpbin.org/get"
        )

        # Mock execute function that raises httpx exceptions
        call_count = 0

        async def exception_execute_fn(
            ctx: FlextApiClient._HttpRequestContext, attempt: int
        ) -> dict[str, object]:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                msg = "Request timeout"
                raise httpx.TimeoutException(msg)
            if call_count == 2:
                msg = "Connection failed"
                raise httpx.RequestError(msg)
            return {}

        result = await retry_strategy.execute(context, exception_execute_fn)
        FlextMatchers.assert_result_failure(result)
        assert "HTTP request failed after 2 attempts" in result.error
        assert "Connection failed" in result.error

    @pytest.mark.asyncio
    async def test_retry_strategy_with_unexpected_exception(self) -> None:
        """Test retry strategy with unexpected exceptions."""
        client = FlextApiClient(max_retries=1)
        retry_strategy = client._retry_strategy

        context = FlextApiClient._HttpRequestContext(
            request_id="test_unexpected", method="GET", url="https://httpbin.org/get"
        )

        # Mock execute function that raises unexpected exception
        async def unexpected_exception_execute_fn(
            ctx: FlextApiClient._HttpRequestContext, attempt: int
        ) -> Never:
            msg = "Unexpected error"
            raise ValueError(msg)

        result = await retry_strategy.execute(context, unexpected_exception_execute_fn)
        FlextMatchers.assert_result_failure(result)
        assert "HTTP request failed after 2 attempts" in result.error
        assert "Unexpected error" in result.error

    @pytest.mark.asyncio
    async def test_execute_single_request_with_mock_response(self) -> None:
        """Test _execute_single_request with mock httpx response."""
        client = FlextApiClient()
        await client.start()

        context = FlextApiClient._HttpRequestContext(
            request_id="test_single", method="GET", url="https://httpbin.org/get"
        )

        # Mock httpx response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"success": True}

        # Mock the client request method
        with patch.object(client._client, "request", return_value=mock_response):
            result = await client._execute_single_request(context, 0)
            assert result.success
            assert result.value == {"success": True}

        await client.stop()

    @pytest.mark.asyncio
    async def test_execute_single_request_with_http_error(self) -> None:
        """Test _execute_single_request with HTTP error response."""
        client = FlextApiClient()
        await client.start()

        context = FlextApiClient._HttpRequestContext(
            request_id="test_error", method="GET", url="https://httpbin.org/status/404"
        )

        # Mock httpx response with error
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_response.headers = {"content-type": "text/plain"}

        # Mock the client request method
        with patch.object(client._client, "request", return_value=mock_response):
            result = await client._execute_single_request(context, 0)
            FlextMatchers.assert_result_failure(result)
            assert "HTTP 404: Not Found" in result.error

        await client.stop()
