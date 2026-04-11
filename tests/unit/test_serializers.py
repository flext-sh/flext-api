"""Tests for MessagePack serialization utilities.

Tests for flext_api.serializers module, covering success and failure paths
for the unpackb() function with proper result type handling.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import msgpack
from flext_tests import tm

from flext_api import FlextApiUtilitiesSerializers


class TestMessagePackUnpackb:
    """Tests for unpackb() result type conversion."""

    def test_unpackb_success_with_dict(self) -> None:
        """Test successful unpacking of msgpack bytes to dict."""
        # Arrange: valid msgpack-encoded dict
        test_data = b"\x81\xa3key\xa5value"  # {"key": "value"} in msgpack

        # Act
        result = FlextApiUtilitiesSerializers.unpackb(test_data)

        # Assert
        tm.that(result.success, eq=True)
        tm.that(result.value, eq={"key": "value"})

    def test_unpackb_success_with_list(self) -> None:
        """Test successful unpacking of msgpack bytes to list."""
        # Arrange: valid msgpack-encoded list
        test_data = b"\x93\x01\x02\x03"  # [1, 2, 3] in msgpack

        # Act
        result = FlextApiUtilitiesSerializers.unpackb(test_data)

        # Assert
        tm.that(result.success, eq=True)
        tm.that(result.value, eq=[1, 2, 3])

    def test_unpackb_success_with_scalar(self) -> None:
        """Test successful unpacking of msgpack bytes to scalar."""
        # Arrange: valid msgpack-encoded string
        test_data = b"\xa5hello"  # "hello" in msgpack

        # Act
        result = FlextApiUtilitiesSerializers.unpackb(test_data)

        # Assert
        tm.that(result.success, eq=True)
        tm.that(result.value, eq="hello")

    def test_unpackb_success_with_int(self) -> None:
        """Test successful unpacking of msgpack bytes to integer."""
        # Arrange: valid msgpack-encoded integer
        test_data = b"\x2a"  # 42 in msgpack

        # Act
        result = FlextApiUtilitiesSerializers.unpackb(test_data)

        # Assert
        tm.that(result.success, eq=True)
        tm.that(result.value, eq=42)

    def test_unpackb_failure_invalid_data(self) -> None:
        """Test failure when data is invalid/unparseable."""
        # Arrange: invalid msgpack data
        test_data = b"\xff\xff\xff\xff"  # Invalid msgpack bytes

        # Act
        result = FlextApiUtilitiesSerializers.unpackb(test_data)

        # Assert
        tm.that(result.failure, eq=True)
        assert result.error is not None
        tm.that(result.error, has="msgpack deserialization failed")

    def test_unpackb_failure_validation_error(self) -> None:
        """Test failure when unpacked data is outside the public recursive contract."""
        packed = msgpack.packb(msgpack.ExtType(1, b"invalid"))
        assert isinstance(packed, bytes)
        test_data = packed
        result = FlextApiUtilitiesSerializers.unpackb(test_data)
        tm.that(result.failure, eq=True)
        assert result.error is not None
        tm.that(result.error.lower(), has="validation")

    def test_unpackb_returns_result_type(self) -> None:
        """Test that unpackb returns r with success/failure semantics."""
        # Arrange
        test_data = b"\x81\xa3key\xa5value"

        # Act
        result = FlextApiUtilitiesSerializers.unpackb(test_data)

        # Assert: verify r semantics (success case)
        tm.that(result.success, eq=True)
        tm.that(result.failure, eq=False)
        tm.that(result.value, eq={"key": "value"})
        tm.that(result.error, eq=None)
