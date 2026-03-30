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
        base,
        http,
        http_client,
        logger,
        rfc,
        sse,
        storage_backend,
        websocket,
    )
    from flext_api.protocol_impls.base import *
    from flext_api.protocol_impls.http import *
    from flext_api.protocol_impls.http_client import *
    from flext_api.protocol_impls.logger import *
    from flext_api.protocol_impls.rfc import *
    from flext_api.protocol_impls.sse import *
    from flext_api.protocol_impls.storage_backend import *
    from flext_api.protocol_impls.websocket import *

_LAZY_IMPORTS: Mapping[str, str | Sequence[str]] = {
    "FlextApiBaseProtocolImplementation": "flext_api.protocol_impls.base",
    "FlextApiLoggerProtocolImplementation": "flext_api.protocol_impls.logger",
    "FlextApiRfcProtocolImplementation": "flext_api.protocol_impls.rfc",
    "FlextApiSseProtocolPlugin": "flext_api.protocol_impls.sse",
    "FlextApiStorageBackendImplementation": "flext_api.protocol_impls.storage_backend",
    "FlextApiWebsocketProtocolPlugin": "flext_api.protocol_impls.websocket",
    "FlextWebClientImplementation": "flext_api.protocol_impls.http_client",
    "FlextWebProtocolPlugin": "flext_api.protocol_impls.http",
    "base": "flext_api.protocol_impls.base",
    "http": "flext_api.protocol_impls.http",
    "http_client": "flext_api.protocol_impls.http_client",
    "logger": "flext_api.protocol_impls.logger",
    "rfc": "flext_api.protocol_impls.rfc",
    "sse": "flext_api.protocol_impls.sse",
    "storage_backend": "flext_api.protocol_impls.storage_backend",
    "websocket": "flext_api.protocol_impls.websocket",
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, sorted(_LAZY_IMPORTS))
