# AUTO-GENERATED FILE — Regenerate with: make gen
"""Examples package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import (
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
)

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_api import (
        api,
        c,
        cli,
        config,
        d,
        e,
        h,
        m,
        main,
        p,
        r,
        s,
        settings,
        t,
        u,
        web,
        x,
    )


__all__: tuple[str, ...] = (
    "api",
    "c",
    "cli",
    "config",
    "d",
    "e",
    "h",
    "m",
    "main",
    "p",
    "r",
    "s",
    "settings",
    "t",
    "u",
    "web",
    "x",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "api": "flext_api",
        "c": "flext_api",
        "cli": "flext_api",
        "config": "flext_api",
        "d": "flext_api",
        "e": "flext_api",
        "h": "flext_api",
        "m": "flext_api",
        "main": "flext_api",
        "p": "flext_api",
        "r": "flext_api",
        "s": "flext_api",
        "settings": "flext_api",
        "t": "flext_api",
        "u": "flext_api",
        "web": "flext_api",
        "x": "flext_api",
    }),
    public_exports=__all__,
)
