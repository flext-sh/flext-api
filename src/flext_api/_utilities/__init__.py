# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""FlextApi utilities subpackage."""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from flext_core import FlextTypes

    from flext_api._utilities import (
        adapters,
        app,
        client,
        lifecycle_manager,
        middleware,
        registry,
        serializers,
        server_factory,
        settings_manager,
        storage,
        webhook,
    )
    from flext_api._utilities.adapters import FlextApiAdapters
    from flext_api._utilities.app import FlextApiApp
    from flext_api._utilities.client import FlextApiClient
    from flext_api._utilities.lifecycle_manager import FlextApiLifecycleManager
    from flext_api._utilities.middleware import FlextApiMiddleware
    from flext_api._utilities.registry import FlextApiRegistry
    from flext_api._utilities.serializers import FlextApiSerializers
    from flext_api._utilities.server_factory import FlextApiServerFactory
    from flext_api._utilities.settings_manager import FlextApiSettingsManager
    from flext_api._utilities.storage import FlextApiStorage
    from flext_api._utilities.webhook import FlextWebhookHandler

_LAZY_IMPORTS: Mapping[str, Sequence[str]] = {
    "FlextApiAdapters": ["flext_api._utilities.adapters", "FlextApiAdapters"],
    "FlextApiApp": ["flext_api._utilities.app", "FlextApiApp"],
    "FlextApiClient": ["flext_api._utilities.client", "FlextApiClient"],
    "FlextApiLifecycleManager": [
        "flext_api._utilities.lifecycle_manager",
        "FlextApiLifecycleManager",
    ],
    "FlextApiMiddleware": ["flext_api._utilities.middleware", "FlextApiMiddleware"],
    "FlextApiRegistry": ["flext_api._utilities.registry", "FlextApiRegistry"],
    "FlextApiSerializers": ["flext_api._utilities.serializers", "FlextApiSerializers"],
    "FlextApiServerFactory": [
        "flext_api._utilities.server_factory",
        "FlextApiServerFactory",
    ],
    "FlextApiSettingsManager": [
        "flext_api._utilities.settings_manager",
        "FlextApiSettingsManager",
    ],
    "FlextApiStorage": ["flext_api._utilities.storage", "FlextApiStorage"],
    "FlextWebhookHandler": ["flext_api._utilities.webhook", "FlextWebhookHandler"],
    "adapters": ["flext_api._utilities.adapters", ""],
    "app": ["flext_api._utilities.app", ""],
    "client": ["flext_api._utilities.client", ""],
    "lifecycle_manager": ["flext_api._utilities.lifecycle_manager", ""],
    "middleware": ["flext_api._utilities.middleware", ""],
    "registry": ["flext_api._utilities.registry", ""],
    "serializers": ["flext_api._utilities.serializers", ""],
    "server_factory": ["flext_api._utilities.server_factory", ""],
    "settings_manager": ["flext_api._utilities.settings_manager", ""],
    "storage": ["flext_api._utilities.storage", ""],
    "webhook": ["flext_api._utilities.webhook", ""],
}

__all__ = [
    "FlextApiAdapters",
    "FlextApiApp",
    "FlextApiClient",
    "FlextApiLifecycleManager",
    "FlextApiMiddleware",
    "FlextApiRegistry",
    "FlextApiSerializers",
    "FlextApiServerFactory",
    "FlextApiSettingsManager",
    "FlextApiStorage",
    "FlextWebhookHandler",
    "adapters",
    "app",
    "client",
    "lifecycle_manager",
    "middleware",
    "registry",
    "serializers",
    "server_factory",
    "settings_manager",
    "storage",
    "webhook",
]


_LAZY_CACHE: MutableMapping[str, FlextTypes.ModuleExport] = {}


def __getattr__(name: str) -> FlextTypes.ModuleExport:
    """Lazy-load module attributes on first access (PEP 562).

    A local cache ``_LAZY_CACHE`` persists resolved objects across repeated
    accesses during process lifetime.

    Args:
        name: Attribute name requested by dir()/import.

    Returns:
        Lazy-loaded module export type.

    Raises:
        AttributeError: If attribute not registered.

    """
    if name in _LAZY_CACHE:
        return _LAZY_CACHE[name]

    value = lazy_getattr(name, _LAZY_IMPORTS, globals(), __name__)
    _LAZY_CACHE[name] = value
    return value


def __dir__() -> Sequence[str]:
    """Return list of available attributes for dir() and autocomplete.

    Returns:
        List of public names from module exports.

    """
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)
