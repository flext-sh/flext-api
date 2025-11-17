"""Protocol implementations for flext-api.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_api.protocol_impls.base import BaseProtocolImplementation
from flext_api.protocol_impls.graphql import GraphQLProtocolPlugin
from flext_api.protocol_impls.http import FlextWebProtocolPlugin
from flext_api.protocol_impls.http_client import FlextWebClientImplementation
from flext_api.protocol_impls.logger import LoggerProtocolImplementation
from flext_api.protocol_impls.rfc import RFCProtocolImplementation
from flext_api.protocol_impls.sse import SSEProtocolPlugin
from flext_api.protocol_impls.storage_backend import StorageBackendImplementation
from flext_api.protocol_impls.websocket import WebSocketProtocolPlugin

__all__ = [
    "BaseProtocolImplementation",
    "FlextWebClientImplementation",
    "FlextWebProtocolPlugin",
    "GraphQLProtocolPlugin",
    "LoggerProtocolImplementation",
    "RFCProtocolImplementation",
    "SSEProtocolPlugin",
    "StorageBackendImplementation",
    "WebSocketProtocolPlugin",
]
