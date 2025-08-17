"""Tests for client core functionality.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import pytest

from flext_api import (
    FlextApiClient,
    FlextApiClientConfig,
    FlextApiClientMethod,
    FlextApiClientRequest,
    FlextApiClientResponse,
    FlextApiClientStatus,
    FlextApiPlugin,
    create_client,
    create_client_with_plugins,
)

# Constants
HTTP_OK = 200
EXPECTED_BULK_SIZE = 2
EXPECTED_DATA_COUNT = 3


class TestFlextApiClientConfig:
    """Test FlextApiClientConfig dataclass."""

    def test_config_creation(self) -> None:
      """Test creating client config."""
      config = FlextApiClientConfig()
      if config.base_url != "":
          msg = f"Expected empty string, got {config.base_url}"
          raise AssertionError(msg)
      assert config.timeout == 30.0
      if config.headers != {}:
          msg = f"Expected empty dict, got {config.headers}"
          raise AssertionError(msg)
      assert config.max_retries == EXPECTED_DATA_COUNT

    def test_config_with_values(self) -> None:
      """Test config with custom values."""
      headers = {"Authorization": "Bearer token"}
      config = FlextApiClientConfig(
          base_url="https://api.example.com",
          timeout=60.0,
          headers=headers,
          max_retries=5,
      )

      if config.base_url != "https://api.example.com":
          msg = f"Expected https://api.example.com, got {config.base_url}"
          raise AssertionError(
              msg,
          )
      assert config.timeout == 60.0
      if config.headers != headers:
          msg = f"Expected {headers}, got {config.headers}"
          raise AssertionError(msg)
      assert config.max_retries == 5

    def test_config_invalid_url(self) -> None:
      """Test config with invalid URL format."""
      with pytest.raises(ValueError, match="Invalid URL format"):
          FlextApiClientConfig(base_url="invalid-url")

      with pytest.raises(ValueError, match="Invalid URL format"):
          FlextApiClientConfig(base_url="ftp://example.com")


class TestFlextApiClientRequest:
    """Test FlextApiClientRequest dataclass."""

    def test_request_creation(self) -> None:
      """Test creating client request."""
      request = FlextApiClientRequest(
          method=FlextApiClientMethod.GET,
          url="/api/test",
      )

      if request.method != FlextApiClientMethod.GET:
          msg = f"Expected {FlextApiClientMethod.GET}, got {request.method}"
          raise AssertionError(
              msg,
          )
      assert request.url == "/api/test"
      if request.headers != {}:
          msg = f"Expected empty dict, got {request.headers}"
          raise AssertionError(msg)
      assert request.params == {}

    def test_request_with_string_method(self) -> None:
      """Test request with string method gets converted."""
      request = FlextApiClientRequest(method="POST", url="/api/test")
      if request.method != FlextApiClientMethod.POST:
          msg = f"Expected {FlextApiClientMethod.POST}, got {request.method}"
          raise AssertionError(
              msg,
          )

    def test_request_validation_empty_url(self) -> None:
      """Test request creation with empty URL."""
      # Empty URL is allowed at dataclass level, validation happens later
      request = FlextApiClientRequest(method=FlextApiClientMethod.GET, url="")
      if request.url != "":
          msg = f"Expected empty string, got {request.url}"
          raise AssertionError(msg)


class TestFlextApiClientResponse:
    """Test FlextApiClientResponse dataclass."""

    def test_response_creation(self) -> None:
      """Test creating client response."""
      response = FlextApiClientResponse(status_code=200)
      if response.status_code != HTTP_OK:
          msg = f"Expected 200, got {response.status_code}"
          raise AssertionError(msg)
      assert response.headers == {}
      assert response.data is None
      if response.elapsed_time != 0.0:
          msg = f"Expected 0.0, got {response.elapsed_time}"
          raise AssertionError(msg)

    def test_response_with_data(self) -> None:
      """Test response with data."""
      data = {"key": "value"}
      response = FlextApiClientResponse(
          status_code=200,
          data=data,
          headers={"Content-Type": "application/json"},
      )

      assert response.status_code == 200
      assert response.data == data
      assert response.headers is not None
      assert response.headers["Content-Type"] == "application/json"

    def test_response_json_method(self) -> None:
      """Test response json method."""
      data = {"key": "value"}
      response = FlextApiClientResponse(status_code=200, data=data)
      assert response.json() == data

    def test_response_text_method(self) -> None:
      """Test response text method."""
      data = "Hello, World!"
      response = FlextApiClientResponse(status_code=200, data=data)
      assert response.text() == data


class TestFlextApiPlugin:
    """Test FlextApiPlugin."""

    def test_plugin_creation(self) -> None:
      """Test plugin creation."""
      plugin = FlextApiPlugin()
      assert isinstance(plugin, FlextApiPlugin)

    def test_plugin_with_name(self) -> None:
      """Test plugin with custom name."""
      plugin = FlextApiPlugin(name="test-plugin")
      assert plugin.name == "test-plugin"

    @pytest.mark.asyncio
    async def test_plugin_before_request(self) -> None:
      """Test plugin before_request hook."""
      plugin = FlextApiPlugin()
      request = FlextApiClientRequest(method=FlextApiClientMethod.GET, url="/test")

      # Should not modify request by default
      modified_request = await plugin.before_request(request)
      assert modified_request == request

    @pytest.mark.asyncio
    async def test_plugin_after_request(self) -> None:
      """Test plugin after_request hook."""
      plugin = FlextApiPlugin()
      request = FlextApiClientRequest(method="GET", url="/test")
      response = FlextApiClientResponse(status_code=200)

      # Should not modify response by default
      modified_response = await plugin.after_request(request, response)
      assert modified_response == response

    @pytest.mark.asyncio
    async def test_plugin_on_error(self) -> None:
      """Test plugin on_error hook."""
      plugin = FlextApiPlugin()
      request = FlextApiClientRequest(method="GET", url="/test")
      error = Exception("Test error")

      # Should not modify error by default
      modified_error = await plugin.on_error(request, error)
      assert modified_error == error


class TestFlextApiClient:
    """Test FlextApiClient."""

    def test_client_creation(self) -> None:
      """Test client creation."""
      client = FlextApiClient()
      assert isinstance(client, FlextApiClient)
      assert client.config is not None

    def test_client_with_config(self) -> None:
      """Test client with custom config."""
      config = FlextApiClientConfig(base_url="https://api.example.com")
      client = FlextApiClient(config=config)
      assert client.config.base_url == "https://api.example.com"

    def test_client_with_plugins(self) -> None:
      """Test client with plugins."""
      plugin = FlextApiPlugin(name="test-plugin")
      client = FlextApiClient(plugins=[plugin])
      assert len(client.plugins) == 1
      assert client.plugins[0].name == "test-plugin"

    def test_health_check(self) -> None:
      """Test client health check."""
      client = FlextApiClient()
      health = client.health_check()

      assert isinstance(health, dict)
      assert "status" in health
      assert "timestamp" in health

    @pytest.mark.asyncio
    async def test_start_service(self) -> None:
      """Test client service start."""
      client = FlextApiClient()
      result = await client.start()

      assert result.success
      assert client.status == FlextApiClientStatus.RUNNING

    @pytest.mark.asyncio
    async def test_stop_service(self) -> None:
      """Test client service stop."""
      client = FlextApiClient()
      await client.start()
      result = await client.stop()

      assert result.success
      assert client.status == FlextApiClientStatus.STOPPED

    @pytest.mark.asyncio
    async def test_close_method(self) -> None:
      """Test client close method."""
      client = FlextApiClient()
      await client.start()
      await client.close()

      assert client.status == FlextApiClientStatus.CLOSED

    @pytest.mark.asyncio
    async def test_context_manager(self) -> None:
      """Test client as context manager."""
      client = FlextApiClient()
      async with client:
          assert client.status == FlextApiClientStatus.RUNNING

      # After context manager exit, status should be STOPPED
      # Check that status changed from RUNNING to STOPPED
      assert str(client.status) == "stopped"

    def test_create_client(self) -> None:
      """Test create_client factory function."""
      client = create_client()
      assert isinstance(client, FlextApiClient)

    def test_create_client_with_config(self) -> None:
      """Test create_client_with_config factory function."""
      config = FlextApiClientConfig(base_url="https://api.example.com")
      client = create_client_with_plugins(config=config)
      assert isinstance(client, FlextApiClient)
      assert client.config.base_url == "https://api.example.com"
