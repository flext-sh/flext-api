# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Api package."""

from __future__ import annotations

from typing import TYPE_CHECKING

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
from flext_api._exports import FLEXT_API_LAZY_IMPORTS
from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_api.api import FlextApi as FlextApi, api as api
    from flext_api.base import FlextApiServiceBase as FlextApiServiceBase, s as s
    from flext_api.constants import FlextApiConstants as FlextApiConstants, c as c
    from flext_api.models import FlextApiModels as FlextApiModels, m as m
    from flext_api.protocols import FlextApiProtocols as FlextApiProtocols, p as p
    from flext_api.settings import FlextApiSettings as FlextApiSettings
    from flext_api.typings import FlextApiTypes as FlextApiTypes, t as t
    from flext_api.utilities import FlextApiUtilities as FlextApiUtilities, u as u
    from flext_web import d as d, e as e, h as h, r as r, x as x


_LAZY_IMPORTS = FLEXT_API_LAZY_IMPORTS


_EAGER_EXPORTS = (
    __author__,
    __author_email__,
    __description__,
    __license__,
    __title__,
    __url__,
    __version__,
    __version_info__,
)


_PUBLIC_EXPORTS: tuple[str, ...] = (
    "FlextApi",
    "FlextApiConstants",
    "FlextApiModels",
    "FlextApiProtocols",
    "FlextApiServiceBase",
    "FlextApiSettings",
    "FlextApiTypes",
    "FlextApiUtilities",
    "api",
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
)

__all__: tuple[str, ...] = (
    "FlextApi",
    "FlextApiConstants",
    "FlextApiModels",
    "FlextApiProtocols",
    "FlextApiServiceBase",
    "FlextApiSettings",
    "FlextApiTypes",
    "FlextApiUtilities",
    "__author__",
    "__author_email__",
    "__description__",
    "__license__",
    "__title__",
    "__url__",
    "__version__",
    "__version_info__",
    "api",
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
)


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    public_exports=_PUBLIC_EXPORTS,
)
