# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Protocol impls package."""

from __future__ import annotations

import typing as _t

from flext_api.protocol_impls.base import FlextApiBaseProtocolImplementation
from flext_api.protocol_impls.http import FlextWebProtocolPlugin
from flext_api.protocol_impls.http_client import FlextWebClientImplementation
from flext_api.protocol_impls.logger import FlextApiLoggerProtocolImplementation
from flext_api.protocol_impls.rfc import FlextApiRfcProtocolImplementation
from flext_api.protocol_impls.sse import FlextApiSseProtocolPlugin
from flext_api.protocol_impls.storage_backend import (
    FlextApiStorageBackendImplementation,
)
from flext_api.protocol_impls.websocket import FlextApiWebsocketProtocolPlugin
from flext_core.constants import FlextConstants as c
from flext_core.decorators import FlextDecorators as d
from flext_core.exceptions import FlextExceptions as e
from flext_core.handlers import FlextHandlers as h
from flext_core.lazy import install_lazy_exports
from flext_core.mixins import FlextMixins as x
from flext_core.models import FlextModels as m
from flext_core.protocols import FlextProtocols as p
from flext_core.result import FlextResult as r
from flext_core.service import FlextService as s
from flext_core.typings import FlextTypes as t
from flext_core.utilities import FlextUtilities as u

if _t.TYPE_CHECKING:
    import flext_api.protocol_impls.base as _flext_api_protocol_impls_base

    base = _flext_api_protocol_impls_base
    import flext_api.protocol_impls.http as _flext_api_protocol_impls_http

    http = _flext_api_protocol_impls_http
    import flext_api.protocol_impls.http_client as _flext_api_protocol_impls_http_client

    http_client = _flext_api_protocol_impls_http_client
    import flext_api.protocol_impls.logger as _flext_api_protocol_impls_logger

    logger = _flext_api_protocol_impls_logger
    import flext_api.protocol_impls.rfc as _flext_api_protocol_impls_rfc

    rfc = _flext_api_protocol_impls_rfc
    import flext_api.protocol_impls.sse as _flext_api_protocol_impls_sse

    sse = _flext_api_protocol_impls_sse
    import flext_api.protocol_impls.storage_backend as _flext_api_protocol_impls_storage_backend

    storage_backend = _flext_api_protocol_impls_storage_backend
    import flext_api.protocol_impls.websocket as _flext_api_protocol_impls_websocket

    websocket = _flext_api_protocol_impls_websocket

    _ = (
        FlextApiBaseProtocolImplementation,
        FlextApiLoggerProtocolImplementation,
        FlextApiRfcProtocolImplementation,
        FlextApiSseProtocolPlugin,
        FlextApiStorageBackendImplementation,
        FlextApiWebsocketProtocolPlugin,
        FlextWebClientImplementation,
        FlextWebProtocolPlugin,
        base,
        c,
        d,
        e,
        h,
        http,
        http_client,
        logger,
        m,
        p,
        r,
        rfc,
        s,
        sse,
        storage_backend,
        t,
        u,
        websocket,
        x,
    )
_LAZY_IMPORTS = {
    "FlextApiBaseProtocolImplementation": "flext_api.protocol_impls.base",
    "FlextApiLoggerProtocolImplementation": "flext_api.protocol_impls.logger",
    "FlextApiRfcProtocolImplementation": "flext_api.protocol_impls.rfc",
    "FlextApiSseProtocolPlugin": "flext_api.protocol_impls.sse",
    "FlextApiStorageBackendImplementation": "flext_api.protocol_impls.storage_backend",
    "FlextApiWebsocketProtocolPlugin": "flext_api.protocol_impls.websocket",
    "FlextWebClientImplementation": "flext_api.protocol_impls.http_client",
    "FlextWebProtocolPlugin": "flext_api.protocol_impls.http",
    "base": "flext_api.protocol_impls.base",
    "c": ("flext_core.constants", "FlextConstants"),
    "d": ("flext_core.decorators", "FlextDecorators"),
    "e": ("flext_core.exceptions", "FlextExceptions"),
    "h": ("flext_core.handlers", "FlextHandlers"),
    "http": "flext_api.protocol_impls.http",
    "http_client": "flext_api.protocol_impls.http_client",
    "logger": "flext_api.protocol_impls.logger",
    "m": ("flext_core.models", "FlextModels"),
    "p": ("flext_core.protocols", "FlextProtocols"),
    "r": ("flext_core.result", "FlextResult"),
    "rfc": "flext_api.protocol_impls.rfc",
    "s": ("flext_core.service", "FlextService"),
    "sse": "flext_api.protocol_impls.sse",
    "storage_backend": "flext_api.protocol_impls.storage_backend",
    "t": ("flext_core.typings", "FlextTypes"),
    "u": ("flext_core.utilities", "FlextUtilities"),
    "websocket": "flext_api.protocol_impls.websocket",
    "x": ("flext_core.mixins", "FlextMixins"),
}

__all__ = [
    "FlextApiBaseProtocolImplementation",
    "FlextApiLoggerProtocolImplementation",
    "FlextApiRfcProtocolImplementation",
    "FlextApiSseProtocolPlugin",
    "FlextApiStorageBackendImplementation",
    "FlextApiWebsocketProtocolPlugin",
    "FlextWebClientImplementation",
    "FlextWebProtocolPlugin",
    "base",
    "c",
    "d",
    "e",
    "h",
    "http",
    "http_client",
    "logger",
    "m",
    "p",
    "r",
    "rfc",
    "s",
    "sse",
    "storage_backend",
    "t",
    "u",
    "websocket",
    "x",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
