# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""FlextApi utilities subpackage."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_api._utilities.adapters import *
    from flext_api._utilities.app import *
    from flext_api._utilities.client import *
    from flext_api._utilities.lifecycle_manager import *
    from flext_api._utilities.middleware import *
    from flext_api._utilities.registry import *
    from flext_api._utilities.serializers import *
    from flext_api._utilities.server_factory import *
    from flext_api._utilities.settings_manager import *
    from flext_api._utilities.storage import *
    from flext_api._utilities.webhook import *

_LAZY_IMPORTS: Mapping[str, str | Sequence[str]] = {
    "FlextApiAdapters": "flext_api._utilities.adapters",
    "FlextApiApp": "flext_api._utilities.app",
    "FlextApiClient": "flext_api._utilities.client",
    "FlextApiLifecycleManager": "flext_api._utilities.lifecycle_manager",
    "FlextApiMiddleware": "flext_api._utilities.middleware",
    "FlextApiRegistry": "flext_api._utilities.registry",
    "FlextApiSerializers": "flext_api._utilities.serializers",
    "FlextApiServerFactory": "flext_api._utilities.server_factory",
    "FlextApiSettingsManager": "flext_api._utilities.settings_manager",
    "FlextApiStorage": "flext_api._utilities.storage",
    "FlextWebhookHandler": "flext_api._utilities.webhook",
    "adapters": "flext_api._utilities.adapters",
    "app": "flext_api._utilities.app",
    "client": "flext_api._utilities.client",
    "lifecycle_manager": "flext_api._utilities.lifecycle_manager",
    "middleware": "flext_api._utilities.middleware",
    "registry": "flext_api._utilities.registry",
    "serializers": "flext_api._utilities.serializers",
    "server_factory": "flext_api._utilities.server_factory",
    "settings_manager": "flext_api._utilities.settings_manager",
    "storage": "flext_api._utilities.storage",
    "webhook": "flext_api._utilities.webhook",
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
