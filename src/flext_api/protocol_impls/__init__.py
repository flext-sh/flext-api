"""Protocol implementations for flext-api.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_api.protocol_impls._lazy_exports import (
    __all__ as __all__,
    __dir__ as __dir__,
    __getattr__ as __getattr__,
)

if TYPE_CHECKING:
    from flext_api.protocol_impls.base import (
        BaseProtocolImplementation as BaseProtocolImplementation,
    )
    from flext_api.protocol_impls.http import (
        FlextWebProtocolPlugin as FlextWebProtocolPlugin,
    )
    from flext_api.protocol_impls.http_client import (
        FlextWebClientImplementation as FlextWebClientImplementation,
    )
    from flext_api.protocol_impls.logger import (
        LoggerProtocolImplementation as LoggerProtocolImplementation,
    )
    from flext_api.protocol_impls.rfc import (
        RFCProtocolImplementation as RFCProtocolImplementation,
    )
    from flext_api.protocol_impls.sse import SSEProtocolPlugin as SSEProtocolPlugin
    from flext_api.protocol_impls.storage_backend import (
        StorageBackendImplementation as StorageBackendImplementation,
    )
    from flext_api.protocol_impls.websocket import (
        WebSocketProtocolPlugin as WebSocketProtocolPlugin,
    )
