"""Comprehensive tests for FlextApiSerializers.

Tests validate serialization functionality using real data.
No mocks - uses actual serialization operations.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_api.serializers import FlextApiSerializers

# Test comment for workflow validation


class TestFlextApiSerializers:
    """Test serialization functionality."""

    def test_msgpack_packb_success(self) -> None:
        """Test MessagePack packb functionality."""
        data: dict[str, str | int] = {"key": "value", "number": 42}

        result = FlextApiSerializers.MessagePack.packb(data)
        assert isinstance(result, bytes)

    def test_msgpack_unpackb_success(self) -> None:
        """Test MessagePack unpackb functionality."""
        data: dict[str, str | int] = {"key": "value", "number": 42}
        packed = FlextApiSerializers.MessagePack.packb(data)

        unpacked = FlextApiSerializers.MessagePack.unpackb(packed)
        assert isinstance(unpacked, dict)
        assert unpacked == data
