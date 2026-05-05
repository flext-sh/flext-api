# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Api package."""

from __future__ import annotations

import typing as _t

from flext_api.__version__ import (
    __author__,
    __author_email__,
    __description__,
    __license__,
    __title__,
    __url__,
    __version__,
    __version_info__,
)
from flext_core.lazy import (
    build_lazy_import_map,
    install_lazy_exports,
    merge_lazy_imports,
)

if _t.TYPE_CHECKING:
    from flext_api._protocols.base import FlextApiProtocolsBase
    from flext_api._protocols.plugins import FlextApiProtocolPlugins
    from flext_api._protocols.serialization import FlextApiProtocolsSerialization
    from flext_api._protocols.transports import FlextApiProtocolsTransports
    from flext_api._typings.serialization import FlextApiTypingsSerialization
    from flext_api._utilities.client import FlextApiClient
    from flext_api._utilities.serializers import FlextApiUtilitiesSerializers
    from flext_api._utilities.settings_manager import FlextApiUtilitiesSettingsManager
    from flext_api.api import FlextApi
    from flext_api.base import FlextApiServiceBase, s
    from flext_api.constants import FlextApiConstants, c
    from flext_api.models import FlextApiModels, m
    from flext_api.protocols import FlextApiProtocols, p
    from flext_api.settings import FlextApiSettings
    from flext_api.typings import FlextApiTypes, t
    from flext_api.utilities import FlextApiUtilities, u
    from flext_web import d, e, h, r, x
_LAZY_IMPORTS = merge_lazy_imports(
    (
        "._protocols",
        "._typings",
        "._utilities",
        ".protocol_impls",
    ),
    build_lazy_import_map(
        {
            "._protocols.base": ("FlextApiProtocolsBase",),
            "._protocols.plugins": ("FlextApiProtocolPlugins",),
            "._protocols.serialization": ("FlextApiProtocolsSerialization",),
            "._protocols.transports": ("FlextApiProtocolsTransports",),
            "._typings.serialization": ("FlextApiTypingsSerialization",),
            "._utilities.client": ("FlextApiClient",),
            "._utilities.serializers": ("FlextApiUtilitiesSerializers",),
            "._utilities.settings_manager": ("FlextApiUtilitiesSettingsManager",),
            ".api": ("FlextApi",),
            ".base": (
                "FlextApiServiceBase",
                "s",
            ),
            ".constants": (
                "FlextApiConstants",
                "c",
            ),
            ".models": (
                "FlextApiModels",
                "m",
            ),
            ".protocols": (
                "FlextApiProtocols",
                "p",
            ),
            ".settings": ("FlextApiSettings",),
            ".typings": (
                "FlextApiTypes",
                "t",
            ),
            ".utilities": (
                "FlextApiUtilities",
                "u",
            ),
            "flext_web": (
                "d",
                "e",
                "h",
                "r",
                "x",
            ),
        },
    ),
    exclude_names=(
        "cleanup_submodule_namespace",
        "install_lazy_exports",
        "lazy_getattr",
        "logger",
        "merge_lazy_imports",
        "output",
        "output_reporting",
        "pytest_addoption",
        "pytest_collect_file",
        "pytest_collection_modifyitems",
        "pytest_configure",
        "pytest_runtest_setup",
        "pytest_runtest_teardown",
        "pytest_sessionfinish",
        "pytest_sessionstart",
        "pytest_terminal_summary",
        "pytest_warning_recorded",
    ),
    module_name=__name__,
)


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    [
        "__author__",
        "__author_email__",
        "__description__",
        "__license__",
        "__title__",
        "__url__",
        "__version__",
        "__version_info__",
    ],
)

__all__: list[str] = [
    "FlextApi",
    "FlextApiClient",
    "FlextApiConstants",
    "FlextApiModels",
    "FlextApiProtocolPlugins",
    "FlextApiProtocols",
    "FlextApiProtocolsBase",
    "FlextApiProtocolsSerialization",
    "FlextApiProtocolsTransports",
    "FlextApiServiceBase",
    "FlextApiSettings",
    "FlextApiTypes",
    "FlextApiTypingsSerialization",
    "FlextApiUtilities",
    "FlextApiUtilitiesSerializers",
    "FlextApiUtilitiesSettingsManager",
    "__author__",
    "__author_email__",
    "__description__",
    "__license__",
    "__title__",
    "__url__",
    "__version__",
    "__version_info__",
    "c",
    "d",
    "e",
    "h",
    "m",
    "p",
    "r",
    "s",
    "t",
    "u",
    "x",
]
