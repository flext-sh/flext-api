# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Api.services package."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from . import _services
    from ._services.async_request import FlextApiClientAsyncRequestMixin
    from ._services.base_request import FlextApiClientBaseRequestMixin
    from ._services.codec import FlextApiClientCodecMixin
    from ._services.request import FlextApiClientRequestMixin
    from .async_client import FlextApiAsyncClient
    from .base_client import FlextApiClientBase
    from .client import FlextApiClient
__all__: tuple[str, ...] = (
    "FlextApiAsyncClient",
    "FlextApiClient",
    "FlextApiClientAsyncRequestMixin",
    "FlextApiClientBase",
    "FlextApiClientBaseRequestMixin",
    "FlextApiClientCodecMixin",
    "FlextApiClientRequestMixin",
    "_services",
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            "._services": ("_services",),
            "._services.async_request": ("FlextApiClientAsyncRequestMixin",),
            "._services.base_request": ("FlextApiClientBaseRequestMixin",),
            "._services.codec": ("FlextApiClientCodecMixin",),
            "._services.request": ("FlextApiClientRequestMixin",),
            ".async_client": ("FlextApiAsyncClient",),
            ".base_client": ("FlextApiClientBase",),
            ".client": ("FlextApiClient",),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
