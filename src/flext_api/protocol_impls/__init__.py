# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Protocol implementations for flext-api.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_api.protocol_impls import (
        base as base,
        http as http,
        http_client as http_client,
        logger as logger,
        rfc as rfc,
        sse as sse,
        storage_backend as storage_backend,
        websocket as websocket,
    )
    from flext_api.protocol_impls.base import (
        FlextApiBaseProtocolImplementation as FlextApiBaseProtocolImplementation,
    )
    from flext_api.protocol_impls.http import (
        FlextWebProtocolPlugin as FlextWebProtocolPlugin,
    )
    from flext_api.protocol_impls.http_client import (
        FlextWebClientImplementation as FlextWebClientImplementation,
    )
    from flext_api.protocol_impls.logger import (
        FlextApiLoggerProtocolImplementation as FlextApiLoggerProtocolImplementation,
    )
    from flext_api.protocol_impls.rfc import (
        FlextApiRfcProtocolImplementation as FlextApiRfcProtocolImplementation,
    )
    from flext_api.protocol_impls.sse import (
        FlextApiSseProtocolPlugin as FlextApiSseProtocolPlugin,
    )
    from flext_api.protocol_impls.storage_backend import (
        FlextApiStorageBackendImplementation as FlextApiStorageBackendImplementation,
    )
    from flext_api.protocol_impls.websocket import (
        FlextApiWebsocketProtocolPlugin as FlextApiWebsocketProtocolPlugin,
    )

_LAZY_IMPORTS: Mapping[str, Sequence[str]] = {
    "FlextApiBaseProtocolImplementation": [
        "flext_api.protocol_impls.base",
        "FlextApiBaseProtocolImplementation",
    ],
    "FlextApiLoggerProtocolImplementation": [
        "flext_api.protocol_impls.logger",
        "FlextApiLoggerProtocolImplementation",
    ],
    "FlextApiRfcProtocolImplementation": [
        "flext_api.protocol_impls.rfc",
        "FlextApiRfcProtocolImplementation",
    ],
    "FlextApiSseProtocolPlugin": [
        "flext_api.protocol_impls.sse",
        "FlextApiSseProtocolPlugin",
    ],
    "FlextApiStorageBackendImplementation": [
        "flext_api.protocol_impls.storage_backend",
        "FlextApiStorageBackendImplementation",
    ],
    "FlextApiWebsocketProtocolPlugin": [
        "flext_api.protocol_impls.websocket",
        "FlextApiWebsocketProtocolPlugin",
    ],
    "FlextWebClientImplementation": [
        "flext_api.protocol_impls.http_client",
        "FlextWebClientImplementation",
    ],
    "FlextWebProtocolPlugin": [
        "flext_api.protocol_impls.http",
        "FlextWebProtocolPlugin",
    ],
    "base": ["flext_api.protocol_impls.base", ""],
    "http": ["flext_api.protocol_impls.http", ""],
    "http_client": ["flext_api.protocol_impls.http_client", ""],
    "logger": ["flext_api.protocol_impls.logger", ""],
    "rfc": ["flext_api.protocol_impls.rfc", ""],
    "sse": ["flext_api.protocol_impls.sse", ""],
    "storage_backend": ["flext_api.protocol_impls.storage_backend", ""],
    "websocket": ["flext_api.protocol_impls.websocket", ""],
}

_EXPORTS: Sequence[str] = [
    "FlextApiBaseProtocolImplementation",
    "FlextApiLoggerProtocolImplementation",
    "FlextApiRfcProtocolImplementation",
    "FlextApiSseProtocolPlugin",
    "FlextApiStorageBackendImplementation",
    "FlextApiWebsocketProtocolPlugin",
    "FlextWebClientImplementation",
    "FlextWebProtocolPlugin",
    "base",
    "http",
    "http_client",
    "logger",
    "rfc",
    "sse",
    "storage_backend",
    "websocket",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, _EXPORTS)
