"""Protocol implementations package.

Contains protocol-specific implementations for HTTP, WebSocket, GraphQL, gRPC, and SSE.

See TRANSFORMATION_PLAN.md - Phase 2, 3, 4 for implementation details.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_api.protocol_impls.http import HttpProtocolPlugin
from flext_api.protocol_impls.sse import SSEProtocolPlugin
from flext_api.protocol_impls.websocket import WebSocketProtocolPlugin

try:
    from flext_api.protocol_impls.graphql import GraphQLProtocolPlugin

    _has_graphql = True
except ImportError:
    GraphQLProtocolPlugin = None
    _has_graphql = False

__all__ = [
    "HttpProtocolPlugin",
    "SSEProtocolPlugin",
    "WebSocketProtocolPlugin",
]

if _has_graphql:
    __all__.append("GraphQLProtocolPlugin")
