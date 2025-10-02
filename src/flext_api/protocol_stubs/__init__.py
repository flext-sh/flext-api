"""Protocol stubs for future integrations.

This module contains protocol stubs for gRPC and Protobuf integrations.
These are placeholders for future flext-grpc integration.

See TRANSFORMATION_PLAN.md - Phase 8 for implementation details.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_api.protocol_stubs.grpc_stub import (
    GrpcChannel,
    GrpcMethod,
    GrpcRequest,
    GrpcResponse,
    GrpcServer,
    GrpcStub,
)
from flext_api.protocol_stubs.protobuf_stub import (
    ProtobufMessage,
    ProtobufSerializer,
)

__all__ = [
    "GrpcChannel",
    "GrpcMethod",
    "GrpcRequest",
    "GrpcResponse",
    "GrpcServer",
    "GrpcStub",
    "ProtobufMessage",
    "ProtobufSerializer",
]
