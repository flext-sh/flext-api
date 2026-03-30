# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Flext api package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING as _TYPE_CHECKING

from flext_core.lazy import install_lazy_exports, merge_lazy_imports

if _TYPE_CHECKING:
    from flext_web import d, e, h, r, s, x

    from flext_api.__version__ import *
    from flext_api._protocols import *
    from flext_api._utilities import *
    from flext_api.api import *
    from flext_api.constants import *
    from flext_api.errors import *
    from flext_api.models import *
    from flext_api.protocol_impls import *
    from flext_api.protocols import *
    from flext_api.schemas import *
    from flext_api.server import *
    from flext_api.settings import *
    from flext_api.typings import *
    from flext_api.utilities import *

_LAZY_IMPORTS: Mapping[str, str | Sequence[str]] = merge_lazy_imports(
    (
        "flext_api._protocols",
        "flext_api._utilities",
        "flext_api.protocol_impls",
        "flext_api.schemas",
    ),
    {
        "FlextApi": "flext_api.api",
        "FlextApiConstants": "flext_api.constants",
        "FlextApiErrors": "flext_api.errors",
        "FlextApiModels": "flext_api.models",
        "FlextApiProtocols": "flext_api.protocols",
        "FlextApiServer": "flext_api.server",
        "FlextApiSettings": "flext_api.settings",
        "FlextApiTypes": "flext_api.typings",
        "FlextApiUtilities": "flext_api.utilities",
        "__author__": "flext_api.__version__",
        "__author_email__": "flext_api.__version__",
        "__description__": "flext_api.__version__",
        "__license__": "flext_api.__version__",
        "__title__": "flext_api.__version__",
        "__url__": "flext_api.__version__",
        "__version__": "flext_api.__version__",
        "__version_info__": "flext_api.__version__",
        "_protocols": "flext_api._protocols",
        "_utilities": "flext_api._utilities",
        "api": "flext_api.api",
        "c": ("flext_api.constants", "FlextApiConstants"),
        "constants": "flext_api.constants",
        "d": "flext_web",
        "e": "flext_web",
        "errors": "flext_api.errors",
        "h": "flext_web",
        "m": ("flext_api.models", "FlextApiModels"),
        "models": "flext_api.models",
        "p": ("flext_api.protocols", "FlextApiProtocols"),
        "protocol_impls": "flext_api.protocol_impls",
        "protocols": "flext_api.protocols",
        "r": "flext_web",
        "s": "flext_web",
        "schemas": "flext_api.schemas",
        "server": "flext_api.server",
        "settings": "flext_api.settings",
        "t": ("flext_api.typings", "FlextApiTypes"),
        "typings": "flext_api.typings",
        "u": ("flext_api.utilities", "FlextApiUtilities"),
        "utilities": "flext_api.utilities",
        "x": "flext_web",
    },
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
