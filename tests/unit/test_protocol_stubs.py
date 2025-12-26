"""Comprehensive tests for protocol stubs.

Tests validate protocol stub imports and exports.
No mocks - uses actual imports.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations



    GrpcChannel,
    GrpcMethod,
    GrpcRequest,
    GrpcResponse,
    GrpcServer,
    GrpcStub,
    ProtobufMessage,
    ProtobufSerializer,
)


class TestProtocolStubs:
    """Test protocol stubs imports."""

    def test_grpc_stub_imports(self) -> None:
        """Test that gRPC stub classes are importable."""
        assert GrpcChannel is not None
        assert GrpcMethod is not None
        assert GrpcRequest is not None
        assert GrpcResponse is not None
        assert GrpcServer is not None
        assert GrpcStub is not None

    def test_protobuf_stub_imports(self) -> None:
        """Test that protobuf stub classes are importable."""
        assert ProtobufMessage is not None
        assert ProtobufSerializer is not None
