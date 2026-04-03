# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Protocol impls package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING as _TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if _TYPE_CHECKING:
    from flext_api import (
        base,
        http,
        http_client,
        logger,
        rfc,
        sse,
        storage_backend,
        websocket,
    )
    from flext_api.base import FlextApiBaseProtocolImplementation
    from flext_api.http import FlextWebProtocolPlugin
    from flext_api.http_client import FlextWebClientImplementation
    from flext_api.logger import FlextApiLoggerProtocolImplementation
    from flext_api.rfc import FlextApiRfcProtocolImplementation
    from flext_api.sse import FlextApiSseProtocolPlugin
    from flext_api.storage_backend import FlextApiStorageBackendImplementation
    from flext_api.websocket import FlextApiWebsocketProtocolPlugin
    from flext_core import FlextTypes
    from flext_core.constants import FlextConstants as c
    from flext_core.decorators import FlextDecorators as d
    from flext_core.exceptions import FlextExceptions as e
    from flext_core.handlers import FlextHandlers as h
    from flext_core.mixins import FlextMixins as x
    from flext_core.models import FlextModels as m
    from flext_core.protocols import FlextProtocols as p
    from flext_core.result import FlextResult as r
    from flext_core.service import FlextService as s
    from flext_core.typings import FlextTypes as t
    from flext_core.utilities import FlextUtilities as u

_LAZY_IMPORTS: FlextTypes.LazyImportIndex = {
    "FlextApiBaseProtocolImplementation": "flext_api.base",
    "FlextApiLoggerProtocolImplementation": "flext_api.logger",
    "FlextApiRfcProtocolImplementation": "flext_api.rfc",
    "FlextApiSseProtocolPlugin": "flext_api.sse",
    "FlextApiStorageBackendImplementation": "flext_api.storage_backend",
    "FlextApiWebsocketProtocolPlugin": "flext_api.websocket",
    "FlextWebClientImplementation": "flext_api.http_client",
    "FlextWebProtocolPlugin": "flext_api.http",
    "base": "flext_api.base",
    "c": ("flext_core.constants", "FlextConstants"),
    "d": ("flext_core.decorators", "FlextDecorators"),
    "e": ("flext_core.exceptions", "FlextExceptions"),
    "h": ("flext_core.handlers", "FlextHandlers"),
    "http": "flext_api.http",
    "http_client": "flext_api.http_client",
    "logger": "flext_api.logger",
    "m": ("flext_core.models", "FlextModels"),
    "p": ("flext_core.protocols", "FlextProtocols"),
    "r": ("flext_core.result", "FlextResult"),
    "rfc": "flext_api.rfc",
    "s": ("flext_core.service", "FlextService"),
    "sse": "flext_api.sse",
    "storage_backend": "flext_api.storage_backend",
    "t": ("flext_core.typings", "FlextTypes"),
    "u": ("flext_core.utilities", "FlextUtilities"),
    "websocket": "flext_api.websocket",
    "x": ("flext_core.mixins", "FlextMixins"),
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
