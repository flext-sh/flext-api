# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Api.services package."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from .client import FlextApiClient
    from .client_codec import FlextApiClientCodecMixin
    from .client_request import FlextApiClientRequestMixin
__all__: tuple[str, ...] = (
    "FlextApiClient",
    "FlextApiClientCodecMixin",
    "FlextApiClientRequestMixin",
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            ".client": ("FlextApiClient",),
            ".client_codec": ("FlextApiClientCodecMixin",),
            ".client_request": ("FlextApiClientRequestMixin",),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
