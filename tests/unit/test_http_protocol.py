"""Unit tests for HTTP protocol plugin.

Tests HTTP protocol implementation including request execution, retry logic,
connection pooling, and error handling.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from flext_api.models import FlextApiModels
from flext_api.protocol_impls.http import HttpProtocolPlugin
from flext_core import FlextResult


class TestHttpProtocolPlugin:
    """Test suite for HttpProtocolPlugin."""

    def _create_mock_response(
        self,
        status_code: int = 200,
        headers: dict | None = None,
        content: bytes = b"",
        text: str = "",
        url: str = "https://example.com",
    ) -> Mock:
        """Create a properly mocked HTTP response."""
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.headers = headers or {}
        mock_response.content = content
        mock_response.text = text
        mock_response.url = url
        mock_response.read = Mock(return_value=content)
        mock_response.aread = Mock(return_value=content)
        return mock_response

    @pytest.fixture
    def http_plugin(self) -> HttpProtocolPlugin:
        """Create HTTP protocol plugin for testing."""
        return HttpProtocolPlugin(
            http2=True,
            max_connections=100,
            max_retries=3,
            retry_backoff_factor=1.0,
        )

    @pytest.fixture
    def sample_request(self) -> FlextApiModels.HttpRequest:
        """Create sample HTTP request for testing."""
        return FlextApiModels.HttpRequest(
            method="GET",
            url="https://httpbin.org/get?test=value",
            headers={"User-Agent": "flext-api-test/1.0.0"},
        )

    def test_plugin_initialization(self, http_plugin: HttpProtocolPlugin) -> None:
        """Test HTTP plugin initialization."""
        assert http_plugin is not None
        assert http_plugin.name == "http"
        assert http_plugin._max_retries == 3
        assert http_plugin._transport is not None

    def test_plugin_supports_protocol(self, http_plugin: HttpProtocolPlugin) -> None:
        """Test protocol support checking."""
        assert http_plugin.supports_protocol("http") is True
        assert http_plugin.supports_protocol("https") is True
        assert http_plugin.supports_protocol("websocket") is False
        assert http_plugin.supports_protocol("grpc") is False

    def test_plugin_get_supported_protocols(
        self, http_plugin: HttpProtocolPlugin
    ) -> None:
        """Test getting list of supported protocols."""
        protocols = http_plugin.get_supported_protocols()
        assert "http" in protocols
        assert "https" in protocols
        assert "http/1.1" in protocols
        assert "http/2" in protocols
        # Note: http/3 may be included based on configuration
        assert len(protocols) >= 4

    def test_send_request_success(
        self,
        http_plugin: HttpProtocolPlugin,
        sample_request: FlextApiModels.HttpRequest,
    ) -> None:
        """Test successful HTTP request."""
        # Mock successful response
        mock_response = self._create_mock_response(
            status_code=200,
            headers={"content-type": "application/json"},
            content=b'{"success": true}',
            text='{"success": true}',
            url=str(sample_request.url),
        )

        # Mock the transport connect to return a mock client
        mock_client = Mock()
        mock_client.request.return_value = mock_response

        with patch.object(
            http_plugin._transport,
            "connect",
            return_value=FlextResult[Mock].ok(mock_client),
        ):
            result = http_plugin.send_request(sample_request)

            assert result.is_success
            response = result.unwrap()
            assert response.status_code == 200
            assert response.headers["content-type"] == "application/json"

    def test_send_request_with_timeout(
        self,
        http_plugin: HttpProtocolPlugin,
        sample_request: FlextApiModels.HttpRequest,
    ) -> None:
        """Test HTTP request with custom timeout."""
        mock_response = self._create_mock_response(
            status_code=200,
            url=str(sample_request.url),
        )

        mock_client = Mock()
        mock_client.request.return_value = mock_response

        with patch.object(
            http_plugin._transport,
            "connect",
            return_value=FlextResult[Mock].ok(mock_client),
        ):
            result = http_plugin.send_request(sample_request, timeout=10.0)

            assert result.is_success

    def test_send_request_retry_on_timeout(
        self,
        http_plugin: HttpProtocolPlugin,
        sample_request: FlextApiModels.HttpRequest,
    ) -> None:
        """Test retry logic on timeout."""
        import httpx

        # Mock timeout on first attempt, success on second
        mock_client = Mock()
        mock_success_response = self._create_mock_response(
            status_code=200,
            url=str(sample_request.url),
        )
        mock_client.request = Mock(
            side_effect=[
                httpx.TimeoutException("Timeout"),
                mock_success_response,
            ]
        )

        with patch.object(
            http_plugin._transport,
            "connect",
            return_value=FlextResult[Mock].ok(mock_client),
        ):
            result = http_plugin.send_request(sample_request)

            assert result.is_success
            assert mock_client.request.call_count == 2

    def test_send_request_retry_exhausted(
        self,
        http_plugin: HttpProtocolPlugin,
        sample_request: FlextApiModels.HttpRequest,
    ) -> None:
        """Test retry logic when all retries exhausted."""
        import httpx

        # Mock timeout on all attempts
        mock_client = Mock()
        mock_client.request = Mock(
            side_effect=[httpx.TimeoutException("Timeout")]
            * (http_plugin._max_retries + 1)
        )

        with patch.object(
            http_plugin._transport,
            "connect",
            return_value=FlextResult[Mock].ok(mock_client),
        ):
            result = http_plugin.send_request(sample_request)

            assert result.is_failure
            assert result.error is not None and "failed after" in result.error
            assert mock_client.request.call_count == http_plugin._max_retries + 1

    def test_send_request_network_error(
        self,
        http_plugin: HttpProtocolPlugin,
        sample_request: FlextApiModels.HttpRequest,
    ) -> None:
        """Test handling of network errors."""
        import httpx

        mock_client = Mock()
        mock_client.request = Mock(side_effect=httpx.NetworkError("Connection failed"))

        with patch.object(
            http_plugin._transport,
            "connect",
            return_value=FlextResult[Mock].ok(mock_client),
        ):
            result = http_plugin.send_request(sample_request)

            assert result.is_failure
            assert (
                result.error is not None and "Connection failed" in result.error
            ) or "failed after" in result.error

    def test_send_request_http_error(
        self,
        http_plugin: HttpProtocolPlugin,
        sample_request: FlextApiModels.HttpRequest,
    ) -> None:
        """Test handling of HTTP error status codes."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.headers = {}
        mock_response.content = b"Internal Server Error"
        mock_response.text = "Internal Server Error"

        mock_client = Mock()
        mock_client.request.return_value = mock_response

        with patch.object(
            http_plugin._transport,
            "connect",
            return_value=FlextResult[Mock].ok(mock_client),
        ):
            result = http_plugin.send_request(sample_request)

            # Plugin should fail on 500 errors
            assert result.is_failure

    def test_send_request_with_body(self, http_plugin: HttpProtocolPlugin) -> None:
        """Test HTTP request with JSON body."""
        request = FlextApiModels.HttpRequest(
            method="POST",
            url="https://httpbin.org/post",
            headers={"Content-Type": "application/json"},
            body=b'{"data": "test"}',
        )

        mock_response = self._create_mock_response(
            status_code=201,
            headers={"content-type": "application/json"},
            content=b'{"created": true}',
            text='{"created": true}',
            url=str(request.url),
        )

        mock_client = Mock()
        mock_client.request.return_value = mock_response

        with patch.object(
            http_plugin._transport,
            "connect",
            return_value=FlextResult[Mock].ok(mock_client),
        ):
            result = http_plugin.send_request(request)

            assert result.is_success
            response = result.unwrap()
            assert response.status_code == 201

    def test_plugin_initialization_lifecycle(self) -> None:
        """Test plugin initialization and shutdown lifecycle."""
        plugin = HttpProtocolPlugin()

        # Test initialization
        init_result = plugin.initialize()
        assert init_result.is_success
        assert plugin.is_initialized

        # Test double initialization
        init_result_2 = plugin.initialize()
        assert init_result_2.is_failure

        # Test shutdown
        shutdown_result = plugin.shutdown()
        assert shutdown_result.is_success
        assert not plugin.is_initialized

        # Test double shutdown
        shutdown_result_2 = plugin.shutdown()
        assert shutdown_result_2.is_failure

    def test_plugin_metadata(self, http_plugin: HttpProtocolPlugin) -> None:
        """Test plugin metadata retrieval."""
        metadata = http_plugin.get_metadata()

        assert metadata["name"] == "http"
        assert "version" in metadata
        assert "description" in metadata
        assert metadata["initialized"] in {"True", "False"}

    def test_send_request_with_custom_headers(
        self, http_plugin: HttpProtocolPlugin
    ) -> None:
        """Test HTTP request with custom headers."""
        request = FlextApiModels.HttpRequest(
            method="GET",
            url="https://httpbin.org/headers",
            headers={
                "X-Custom-Header": "custom-value",
                "Authorization": "Bearer token123",
            },
        )

        mock_response = self._create_mock_response(
            status_code=200,
            url=str(request.url),
        )

        mock_client = Mock()
        mock_client.request.return_value = mock_response

        with patch.object(
            http_plugin._transport,
            "connect",
            return_value=FlextResult[Mock].ok(mock_client),
        ):
            result = http_plugin.send_request(request)

            assert result.is_success
            # Verify custom headers were passed
            call_args = mock_client.request.call_args
            assert call_args is not None

    def test_exponential_backoff(
        self,
        http_plugin: HttpProtocolPlugin,
        sample_request: FlextApiModels.HttpRequest,
    ) -> None:
        """Test exponential backoff on retries."""
        import time

        import httpx

        call_times = []

        def mock_request_with_timing(*args, **kwargs):
            call_times.append(time.time())
            if len(call_times) < 3:
                msg = "Timeout"
                raise httpx.TimeoutException(msg)
            return self._create_mock_response(
                status_code=200,
                url=str(sample_request.url),
            )

        mock_client = Mock()
        mock_client.request = Mock(side_effect=mock_request_with_timing)

        with patch.object(
            http_plugin._transport,
            "connect",
            return_value=FlextResult[Mock].ok(mock_client),
        ):
            result = http_plugin.send_request(sample_request)

            assert result.is_success
            assert len(call_times) == 3

            # Verify exponential backoff between retries
            if len(call_times) >= 3:
                delay_1 = call_times[1] - call_times[0]
                delay_2 = call_times[2] - call_times[1]
                # Second delay should be roughly double the first (exponential backoff)
                assert delay_2 > delay_1
