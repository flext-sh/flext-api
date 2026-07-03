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

if TYPE_CHECKING:
    from flext_core import (
        d as d,
        e as e,
        h as h,
        r as r,
        s as s,
        x as x,
    )

install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    public_exports=_PUBLIC_EXPORTS,
)
