"""Tests for MessagePack serialization utilities.

Tests for flext_api.serializers module, covering success and failure paths
for the MessagePack.unpackb() function with proper result type handling.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from flext_tests import tm

from flext_api.serializers import FlextApiSerializers


class TestMessagePackUnpackb:
    """Tests for MessagePack.unpackb() result type conversion."""

    def test_unpackb_success_with_dict(self) -> None:
        """Test successful unpacking of msgpack bytes to dict."""
        # Arrange: valid msgpack-encoded dict
        test_data = b"\x81\xa3key\xa5value"  # {"key": "value"} in msgpack

        # Act
        result = FlextApiSerializers.MessagePack.unpackb(test_data)

        # Assert
        tm.that(result.is_success, eq=True)
        tm.that(result.value == {"key": "value"}, eq=True)

    def test_unpackb_success_with_list(self) -> None:
        """Test successful unpacking of msgpack bytes to list."""
        # Arrange: valid msgpack-encoded list
        test_data = b"\x93\x01\x02\x03"  # [1, 2, 3] in msgpack

        # Act
        result = FlextApiSerializers.MessagePack.unpackb(test_data)

        # Assert
        tm.that(result.is_success, eq=True)
        tm.that(result.value == [1, 2, 3], eq=True)

    def test_unpackb_success_with_scalar(self) -> None:
        """Test successful unpacking of msgpack bytes to scalar."""
        # Arrange: valid msgpack-encoded string
        test_data = b"\xa5hello"  # "hello" in msgpack

        # Act
        result = FlextApiSerializers.MessagePack.unpackb(test_data)

        # Assert
        tm.that(result.is_success, eq=True)
        tm.that(result.value == "hello", eq=True)

    def test_unpackb_success_with_int(self) -> None:
        """Test successful unpacking of msgpack bytes to integer."""
        # Arrange: valid msgpack-encoded integer
        test_data = b"\x2a"  # 42 in msgpack

        # Act
        result = FlextApiSerializers.MessagePack.unpackb(test_data)

        # Assert
        tm.that(result.is_success, eq=True)
        tm.that(result.value == 42, eq=True)

    def test_unpackb_failure_msgpack_not_available(self) -> None:
        """Test failure when msgpack module is not available."""
        # Arrange: mock _load_msgpack to return None
        with patch("flext_api.serializers._load_msgpack", return_value=None):
            test_data = b"\x81\xa3key\xa5value"

            # Act
            result = FlextApiSerializers.MessagePack.unpackb(test_data)

            # Assert
            tm.that(result.is_failure, eq=True)
            assert result.error is not None
            tm.that("msgpack module not available" in result.error, eq=True)

    def test_unpackb_failure_unpackb_function_not_found(self) -> None:
        """Test failure when msgpack.unpackb function is not found."""
        # Arrange: mock module without unpackb function
        mock_module = MagicMock()
        mock_module.unpackb = None

        with patch("flext_api.serializers._load_msgpack", return_value=mock_module):
            test_data = b"\x81\xa3key\xa5value"

            # Act
            result = FlextApiSerializers.MessagePack.unpackb(test_data)

            # Assert
            tm.that(result.is_failure, eq=True)
            assert result.error is not None
            tm.that("msgpack.unpackb function not found" in result.error, eq=True)

    def test_unpackb_failure_invalid_data(self) -> None:
        """Test failure when data is invalid/unparseable."""
        # Arrange: invalid msgpack data
        test_data = b"\xff\xff\xff\xff"  # Invalid msgpack bytes

        # Act
        result = FlextApiSerializers.MessagePack.unpackb(test_data)

        # Assert
        tm.that(result.is_failure, eq=True)
        assert result.error is not None
        tm.that("msgpack deserialization failed" in result.error, eq=True)

    def test_unpackb_failure_validation_error(self) -> None:
        """Test failure when validation fails on unpacked data."""
        # Arrange: mock unpackb to return data that fails validation
        mock_module = MagicMock()
        mock_unpackb = MagicMock(return_value=object())  # object() fails validation
        mock_module.unpackb = mock_unpackb

        with patch("flext_api.serializers._load_msgpack", return_value=mock_module):
            test_data = b"\x00"

            # Act
            result = FlextApiSerializers.MessagePack.unpackb(test_data)

            # Assert
            tm.that(result.is_failure, eq=True)
            assert result.error is not None
            tm.that("validation" in result.error.lower(), eq=True)

    def test_unpackb_returns_result_type(self) -> None:
        """Test that unpackb returns r[T] type."""
        # Arrange
        test_data = b"\x81\xa3key\xa5value"

        # Act
        result = FlextApiSerializers.MessagePack.unpackb(test_data)

        # Assert: verify it's a FlextResult instance
        tm.that(hasattr(result, "is_success"), eq=True)
        tm.that(hasattr(result, "is_failure"), eq=True)
        tm.that(hasattr(result, "value"), eq=True)
        tm.that(hasattr(result, "error"), eq=True)
