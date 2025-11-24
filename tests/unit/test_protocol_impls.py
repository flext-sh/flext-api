"""Comprehensive tests for protocol implementations.

Tests validate protocol implementation imports and exports.
No mocks - uses actual imports.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_api.protocol_impls import (
    BaseProtocolImplementation,
    FlextWebClientImplementation,
    FlextWebProtocolPlugin,
    GraphQLProtocolPlugin,
    LoggerProtocolImplementation,
    RFCProtocolImplementation,
    SSEProtocolPlugin,
    StorageBackendImplementation,
    WebSocketProtocolPlugin,
)


class TestProtocolImpls:
    """Test protocol implementations imports."""

    def test_all_protocol_impls_importable(self) -> None:
        """Test that all protocol implementation classes are importable."""
        assert BaseProtocolImplementation is not None
        assert FlextWebClientImplementation is not None
        assert FlextWebProtocolPlugin is not None
        assert GraphQLProtocolPlugin is not None
        assert LoggerProtocolImplementation is not None
        assert RFCProtocolImplementation is not None
        assert SSEProtocolPlugin is not None
        assert StorageBackendImplementation is not None
        assert WebSocketProtocolPlugin is not None
