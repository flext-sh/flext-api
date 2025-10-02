"""Unit tests for flext-api protocols.

Tests protocol compliance and interface contracts.
"""

from __future__ import annotations

from unittest.mock import Mock

from flext_api.protocols import FlextApiProtocols
from flext_core import FlextResult


class TestFlextApiProtocols:
    """Test protocol compliance and interface contracts."""

    def test_http_client_protocol_compliance(self) -> None:
        """Test HttpClientProtocol compliance with mock implementation."""
        # Create mock implementation
        mock_client = Mock(spec=FlextApiProtocols.HttpClientProtocol)

        # Mock return values
        mock_response = FlextResult(data={"status": "ok"})
        mock_client.request.return_value = mock_response
        mock_client.get.return_value = mock_response
        mock_client.post.return_value = mock_response
        mock_client.put.return_value = mock_response
        mock_client.delete.return_value = mock_response

        # Test request method (for )
        result = mock_client.request(
            method="GET",
            url="https://example.com/api?param=value",
            headers={"Content-Type": "application/json"},
            data={"key": "value"},
            timeout=30.0,
        )
        assert result.is_success is True
        mock_client.request.assert_called_once()

        # Test HTTP methods (for )
        mock_client.get("https://example.com/api")
        mock_client.post("https://example.com/api", data={"key": "value"})
        mock_client.put("https://example.com/api", data={"key": "value"})
        mock_client.delete("https://example.com/api")

        # Verify all methods were called
        assert mock_client.get.called
        assert mock_client.post.called
        assert mock_client.put.called
        assert mock_client.delete.called

    def test_storage_backend_protocol_compliance(self) -> None:
        """Test StorageBackendProtocol compliance with mock implementation."""
        mock_storage = Mock(spec=FlextApiProtocols.StorageBackendProtocol)

        # Mock return values
        mock_result = FlextResult(data=True)
        mock_get_result = FlextResult(data="test_value")
        mock_keys_result = FlextResult(data=["key1", "key2"])

        mock_storage.get.return_value = mock_get_result
        mock_storage.set.return_value = mock_result
        mock_storage.delete.return_value = mock_result
        mock_storage.exists.return_value = mock_result
        mock_storage.clear.return_value = mock_result
        mock_storage.keys.return_value = mock_keys_result

        # Test all methods
        result = mock_storage.get("test_key")
        assert result.is_success is True
        assert result.data == "test_value"

        mock_storage.set("test_key", "test_value", timeout=3600)
        mock_storage.delete("test_key")
        mock_storage.exists("test_key")
        mock_storage.clear()
        mock_storage.keys()

        # Verify all methods were called
        assert mock_storage.get.called
        assert mock_storage.set.called
        assert mock_storage.delete.called
        assert mock_storage.exists.called
        assert mock_storage.clear.called
        assert mock_storage.keys.called

    def test_retry_strategy_protocol_compliance(self) -> None:
        """Test RetryStrategyProtocol compliance with mock implementation."""
        mock_retry = Mock(spec=FlextApiProtocols.RetryStrategyProtocol)

        # Mock return values
        mock_retry.should_retry.return_value = True
        mock_retry.get_delay.return_value = 1.0
        mock_retry.get_max_attempts.return_value = 3

        # Test methods
        should_retry = mock_retry.should_retry(1, ValueError("test"), 500)
        assert should_retry is True

        delay = mock_retry.get_delay(1)
        assert delay == 1.0

        max_attempts = mock_retry.get_max_attempts()
        assert max_attempts == 3

        # Verify all methods were called
        assert mock_retry.should_retry.called
        assert mock_retry.get_delay.called
        assert mock_retry.get_max_attempts.called

    def test_connection_manager_protocol_compliance(self) -> None:
        """Test ConnectionManagerProtocol compliance with mock implementation."""
        mock_conn_mgr = Mock(spec=FlextApiProtocols.ConnectionManagerProtocol)

        # Mock return values
        mock_result = FlextResult(data=True)
        mock_conn_result = FlextResult(data=Mock())

        mock_conn_mgr.get_connection.return_value = mock_conn_result
        mock_conn_mgr.release_connection.return_value = mock_result
        mock_conn_mgr.close_all.return_value = mock_result
        mock_conn_mgr.is_healthy.return_value = mock_result

        # Test methods
        conn_result = mock_conn_mgr.get_connection()
        assert conn_result.is_success is True

        mock_conn_mgr.release_connection(Mock())
        mock_conn_mgr.close_all()
        mock_conn_mgr.is_healthy()

        # Verify all methods were called
        assert mock_conn_mgr.get_connection.called
        assert mock_conn_mgr.release_connection.called
        assert mock_conn_mgr.close_all.called
        assert mock_conn_mgr.is_healthy.called

    def test_cache_protocol_compliance(self) -> None:
        """Test CacheProtocol compliance with mock implementation."""
        mock_cache = Mock(spec=FlextApiProtocols.CacheProtocol)

        # Mock return values
        mock_result = FlextResult(data=True)
        mock_get_result = FlextResult(data="cached_value")

        mock_cache.get.return_value = mock_get_result
        mock_cache.set.return_value = mock_result
        mock_cache.invalidate.return_value = mock_result
        mock_cache.clear.return_value = mock_result

        # Test methods
        result = mock_cache.get("test_key")
        assert result.is_success is True
        assert result.data == "cached_value"

        mock_cache.set("test_key", "test_value", ttl=3600)
        mock_cache.invalidate("test_key")
        mock_cache.clear()

        # Verify all methods were called
        assert mock_cache.get.called
        assert mock_cache.set.called
        assert mock_cache.invalidate.called
        assert mock_cache.clear.called

    def test_request_validator_protocol_compliance(self) -> None:
        """Test RequestValidatorProtocol compliance with mock implementation."""
        mock_validator = Mock(spec=FlextApiProtocols.RequestValidatorProtocol)

        # Mock return values
        mock_request_data = {"key": "value"}
        mock_headers = {"Content-Type": "application/json"}
        mock_params = {"param": "value"}

        mock_validator.validate_request.return_value = FlextResult(
            data=mock_request_data
        )
        mock_validator.validate_headers.return_value = FlextResult(data=mock_headers)
        mock_validator.validate_params.return_value = FlextResult(data=mock_params)

        # Test methods
        result = mock_validator.validate_request(mock_request_data)
        assert result.is_success is True

        mock_validator.validate_headers(mock_headers)
        mock_validator.validate_params(mock_params)

        # Verify all methods were called
        assert mock_validator.validate_request.called
        assert mock_validator.validate_headers.called
        assert mock_validator.validate_params.called

    def test_response_processor_protocol_compliance(self) -> None:
        """Test ResponseProcessorProtocol compliance with mock implementation."""
        mock_processor = Mock(spec=FlextApiProtocols.ResponseProcessorProtocol)

        # Mock return values
        mock_response_data = {"status": "ok"}
        mock_error = ValueError("test error")

        mock_processor.process_response.return_value = FlextResult(
            data=mock_response_data
        )
        mock_processor.handle_error_response.return_value = FlextResult(
            error=str(mock_error)
        )

        # Test methods
        result = mock_processor.process_response(mock_response_data, 200)
        assert result.is_success is True

        error_result = mock_processor.handle_error_response(mock_response_data, 500)
        assert error_result.is_failure is True

        # Verify all methods were called
        assert mock_processor.process_response.called
        assert mock_processor.handle_error_response.called

    def test_authentication_provider_protocol_compliance(self) -> None:
        """Test AuthenticationProviderProtocol compliance with mock implementation."""
        mock_auth = Mock(spec=FlextApiProtocols.AuthenticationProviderProtocol)

        # Mock return values
        mock_headers = {"Authorization": "Bearer token"}
        mock_result = FlextResult(data=True)

        mock_auth.get_auth_headers.return_value = FlextResult(data=mock_headers)
        mock_auth.is_authenticated.return_value = mock_result
        mock_auth.refresh_auth.return_value = mock_result

        # Test methods
        result = mock_auth.get_auth_headers()
        assert result.is_success is True
        assert result.data == mock_headers

        mock_auth.is_authenticated()
        mock_auth.refresh_auth()

        # Verify all methods were called
        assert mock_auth.get_auth_headers.called
        assert mock_auth.is_authenticated.called
        assert mock_auth.refresh_auth.called

    def test_metrics_collector_protocol_compliance(self) -> None:
        """Test MetricsCollectorProtocol compliance with mock implementation."""
        mock_metrics = Mock(spec=FlextApiProtocols.MetricsCollectorProtocol)

        # Mock return values
        mock_result = FlextResult(data=True)
        mock_metrics_data = {"requests": 100, "errors": 5}

        mock_metrics.record_request.return_value = mock_result
        mock_metrics.record_error.return_value = mock_result
        mock_metrics.get_metrics.return_value = FlextResult(data=mock_metrics_data)

        # Test methods
        result = mock_metrics.record_request("GET", "https://example.com", 200, 150.0)
        assert result.is_success is True

        mock_metrics.record_error(ValueError("test"), {"context": "test"})

        metrics_result = mock_metrics.get_metrics()
        assert metrics_result.is_success is True
        assert metrics_result.data == mock_metrics_data

        # Verify all methods were called
        assert mock_metrics.record_request.called
        assert mock_metrics.record_error.called
        assert mock_metrics.get_metrics.called

    def test_middleware_protocol_compliance(self) -> None:
        """Test MiddlewareProtocol compliance with mock implementation."""
        mock_middleware = Mock(spec=FlextApiProtocols.MiddlewareProtocol)

        # Mock return values
        mock_request_data = {"key": "value"}
        mock_response_data = {"status": "ok"}

        mock_middleware.process_request.return_value = FlextResult(
            data=mock_request_data
        )
        mock_middleware.process_response.return_value = FlextResult(
            data=mock_response_data
        )

        # Test methods
        result = mock_middleware.process_request(mock_request_data)
        assert result.is_success is True

        response_result = mock_middleware.process_response(mock_response_data)
        assert response_result.is_success is True

        # Verify all methods were called
        assert mock_middleware.process_request.called
        assert mock_middleware.process_response.called

    def test_plugin_protocol_compliance(self) -> None:
        """Test PluginProtocol compliance with mock implementation."""
        mock_plugin = Mock(spec=FlextApiProtocols.PluginProtocol)

        # Mock return values
        mock_result = FlextResult(data=True)
        mock_config = {"setting": "value"}

        mock_plugin.initialize.return_value = mock_result
        mock_plugin.is_enabled.return_value = True
        mock_plugin.get_name.return_value = "test_plugin"
        mock_plugin.get_version.return_value = "1.0.0"

        # Test methods
        result = mock_plugin.initialize(mock_config)
        assert result.is_success is True

        assert mock_plugin.is_enabled() is True
        assert mock_plugin.get_name() == "test_plugin"
        assert mock_plugin.get_version() == "1.0.0"

        # Verify all methods were called
        assert mock_plugin.initialize.called
        assert mock_plugin.is_enabled.called
        assert mock_plugin.get_name.called
        assert mock_plugin.get_version.called

    def test_configuration_provider_protocol_compliance(self) -> None:
        """Test ConfigurationProviderProtocol compliance with mock implementation."""
        mock_config_provider = Mock(
            spec=FlextApiProtocols.ConfigurationProviderProtocol
        )

        # Mock return values
        mock_result = FlextResult(data=True)
        mock_config_result = FlextResult(data="config_value")

        mock_config_provider.get_config.return_value = mock_config_result
        mock_config_provider.set_config.return_value = mock_result
        mock_config_provider.reload_config.return_value = mock_result

        # Test methods
        result = mock_config_provider.get_config("test_key")
        assert result.is_success is True
        assert result.data == "config_value"

        mock_config_provider.set_config("test_key", "test_value")
        mock_config_provider.reload_config()

        # Verify all methods were called
        assert mock_config_provider.get_config.called
        assert mock_config_provider.set_config.called
        assert mock_config_provider.reload_config.called

    def test_logger_protocol_compliance(self) -> None:
        """Test LoggerProtocol compliance with mock implementation."""
        mock_logger = Mock(spec=FlextApiProtocols.LoggerProtocol)

        # Test methods
        mock_logger.info("test info message", extra={"key": "value"})
        mock_logger.error("test error message", extra={"key": "value"})
        mock_logger.debug("test debug message", extra={"key": "value"})
        mock_logger.warning("test warning message", extra={"key": "value"})

        # Verify all methods were called
        assert mock_logger.info.called
        assert mock_logger.error.called
        assert mock_logger.debug.called
        assert mock_logger.warning.called

    def test_protocol_runtime_checkable(self) -> None:
        """Test that protocols are runtime checkable."""
        # Create mock implementations
        mock_http_client = Mock(spec=FlextApiProtocols.HttpClientProtocol)
        mock_storage = Mock(spec=FlextApiProtocols.StorageBackendProtocol)

        # Test runtime checking
        assert isinstance(mock_http_client, FlextApiProtocols.HttpClientProtocol)
        assert isinstance(mock_storage, FlextApiProtocols.StorageBackendProtocol)

        # Test that non-compliant objects are not considered instances
        non_compliant = Mock()
        assert not isinstance(non_compliant, FlextApiProtocols.HttpClientProtocol)
        assert not isinstance(non_compliant, FlextApiProtocols.StorageBackendProtocol)
