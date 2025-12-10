"""Comprehensive tests for BaseProtocolImplementation.

Tests validate base protocol functionality using real implementation.
No mocks - uses actual BaseProtocolImplementation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_api.protocol_impls.base import BaseProtocolImplementation


class TestBaseProtocolImplementation:
    """Test base protocol implementation."""

    def test_initialization(self) -> None:
        """Test protocol implementation can be initialized."""
        protocol = BaseProtocolImplementation(name="test_protocol")
        assert protocol is not None
        assert protocol.name == "test_protocol"
        assert protocol.version == "1.0.0"
        assert protocol.description == ""
        assert not protocol.is_initialized

    def test_initialization_with_params(self) -> None:
        """Test protocol initialization with custom parameters."""
        protocol = BaseProtocolImplementation(
            name="custom_protocol",
            version="2.0.0",
            description="Custom protocol description",
        )
        assert protocol.name == "custom_protocol"
        assert protocol.version == "2.0.0"
        assert protocol.description == "Custom protocol description"

    def test_execute_before_initialization(self) -> None:
        """Test execute method before initialization."""
        protocol = BaseProtocolImplementation(name="test")
        result = protocol.execute()
        assert result.is_failure
        assert "not initialized" in result.error

    def test_initialize_success(self) -> None:
        """Test successful initialization."""
        protocol = BaseProtocolImplementation(name="test")
        result = protocol.initialize()
        assert result.is_success
        assert protocol.is_initialized

    def test_initialize_already_initialized(self) -> None:
        """Test initialization when already initialized."""
        protocol = BaseProtocolImplementation(name="test")
        protocol.initialize()
        result = protocol.initialize()
        assert result.is_failure
        assert "already initialized" in result.error

    def test_execute_after_initialization(self) -> None:
        """Test execute method after initialization."""
        protocol = BaseProtocolImplementation(name="test")
        protocol.initialize()
        result = protocol.execute()
        assert result.is_success
        assert result.value is True

    def test_shutdown_success(self) -> None:
        """Test successful shutdown."""
        protocol = BaseProtocolImplementation(name="test")
        protocol.initialize()
        result = protocol.shutdown()
        assert result.is_success
        assert not protocol.is_initialized

    def test_shutdown_not_initialized(self) -> None:
        """Test shutdown when not initialized."""
        protocol = BaseProtocolImplementation(name="test")
        result = protocol.shutdown()
        assert result.is_failure
        assert "not initialized" in result.error

    def test_send_request_not_implemented(self) -> None:
        """Test send_request method is not implemented in base class."""
        protocol = BaseProtocolImplementation(name="test")
        result = protocol.send_request({})
        assert result.is_failure
        assert "must be implemented" in result.error

    def test_supports_protocol_default(self) -> None:
        """Test supports_protocol default implementation."""
        protocol = BaseProtocolImplementation(name="test")
        assert not protocol.supports_protocol("http")
        assert not protocol.supports_protocol("websocket")

    def test_get_supported_protocols_default(self) -> None:
        """Test get_supported_protocols default implementation."""
        protocol = BaseProtocolImplementation(name="test")
        protocols = protocol.get_supported_protocols()
        assert isinstance(protocols, list)
        assert len(protocols) == 0

    def test_get_protocol_info(self) -> None:
        """Test get_protocol_info method."""
        protocol = BaseProtocolImplementation(
            name="test_protocol",
            version="1.0.0",
            description="Test protocol",
        )
        info = protocol.get_protocol_info()
        assert isinstance(info, dict)
        assert info["name"] == "test_protocol"
        assert info["version"] == "1.0.0"
        assert info["description"] == "Test protocol"
        assert info["initialized"] is False
        assert isinstance(info["supported_protocols"], list)

    def test_get_protocol_info_after_initialization(self) -> None:
        """Test get_protocol_info after initialization."""
        protocol = BaseProtocolImplementation(name="test")
        protocol.initialize()
        info = protocol.get_protocol_info()
        assert info["initialized"] is True

    def test_validate_request_valid(self) -> None:
        """Test _validate_request with valid request."""
        protocol = BaseProtocolImplementation(name="test")
        result = protocol._validate_request({"method": "GET", "url": "/test"})
        assert result.is_success
        assert result.value == {"method": "GET", "url": "/test"}

    def test_validate_request_not_dict(self) -> None:
        """Test _validate_request with non-dict request."""
        protocol = BaseProtocolImplementation(name="test")
        result = protocol._validate_request("not a dict")
        assert result.is_failure
        assert "must be a dictionary" in result.error

    def test_validate_request_empty(self) -> None:
        """Test _validate_request with empty dict."""
        protocol = BaseProtocolImplementation(name="test")
        result = protocol._validate_request({})
        assert result.is_failure
        assert "cannot be empty" in result.error

    def test_build_error_response(self) -> None:
        """Test _build_error_response method."""
        protocol = BaseProtocolImplementation(name="test")
        response = protocol._build_error_response("Test error", 404)
        assert isinstance(response, dict)
        assert response["status"] == "error"
        assert response["status_code"] == 404
        assert response["error"] == "Test error"
        assert response["timestamp"] is None

    def test_build_success_response_no_data(self) -> None:
        """Test _build_success_response without data."""
        protocol = BaseProtocolImplementation(name="test")
        response = protocol._build_success_response()
        assert isinstance(response, dict)
        assert response["status"] == "success"
        assert response["status_code"] == 200
        assert "data" not in response

    def test_build_success_response_with_data(self) -> None:
        """Test _build_success_response with data."""
        protocol = BaseProtocolImplementation(name="test")
        data = {"result": "success"}
        response = protocol._build_success_response(data, 201)
        assert isinstance(response, dict)
        assert response["status"] == "success"
        assert response["status_code"] == 201
        assert response["data"] == data
