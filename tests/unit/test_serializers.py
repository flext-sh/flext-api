"""Tests for MessagePack serialization utilities.

Tests for flext_api.serializers module, covering success and failure paths
for the unpackb() function with proper result type handling.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from tests.utilities import u


class TestsFlextApiSerializers:
    """Tests for unpackb() result type conversion."""

    def test_unpackb_success_with_dict(self) -> None:
        """Test successful unpacking of msgpack bytes to dict."""
        # Arrange: valid msgpack-encoded dict
        test_data = b"\x81\xa3key\xa5value"  # {"key": "value"} in msgpack

        # Act
        result = u.unpackb(test_data)

        # Assert
        assert result.success is True
        assert result.value == {"key": "value"}

    def test_unpackb_success_with_list(self) -> None:
        """Test successful unpacking of msgpack bytes to list."""
        # Arrange: valid msgpack-encoded list
        test_data = b"\x93\x01\x02\x03"  # [1, 2, 3] in msgpack

        # Act
        result = u.unpackb(test_data)

        # Assert
        assert result.success is True
        assert result.value == [1, 2, 3]

    def test_unpackb_success_with_scalar(self) -> None:
        """Test successful unpacking of msgpack bytes to scalar."""
        # Arrange: valid msgpack-encoded string
        test_data = b"\xa5hello"  # "hello" in msgpack

        # Act
        result = u.unpackb(test_data)

        # Assert
        assert result.success is True
        assert result.value == "hello"

    def test_unpackb_success_with_int(self) -> None:
        """Test successful unpacking of msgpack bytes to integer."""
        # Arrange: valid msgpack-encoded integer
        test_data = b"\x2a"  # 42 in msgpack

        # Act
        result = u.unpackb(test_data)

        # Assert
        assert result.success is True
        assert result.value == 42

    def test_unpackb_failure_invalid_data(self) -> None:
        """Test failure when data is invalid/unparseable."""
        # Arrange: invalid msgpack data
        test_data = b"\xff\xff\xff\xff"  # Invalid msgpack bytes

        # Act
        result = u.unpackb(test_data)

        # Assert
        assert result.failure is True
        assert result.error is not None
        assert "msgpack deserialization failed" in result.error

    def test_unpackb_failure_validation_error(self) -> None:
        """Test failure when unpacked data is outside the public recursive contract."""
        test_data = b"\xc7\x07\x01invalid"
        result = u.unpackb(test_data)
        assert result.failure is True
        assert result.error is not None

    def test_unpackb_returns_result_type(self) -> None:
        """Test that unpackb returns r with success/failure semantics."""
        # Arrange
        test_data = b"\x81\xa3key\xa5value"

        # Act
        result = u.unpackb(test_data)

        # Assert: verify r semantics (success case)
        assert result.success is True
        assert result.failure is False
        assert result.value == {"key": "value"}
        assert result.error is None
