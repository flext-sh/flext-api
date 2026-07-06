# AUTO-GENERATED FILE — Regenerate with: make gen
"""Package version and metadata for flext-api.

Subclass of ``FlextVersion`` — overrides only ``_metadata``.
All derived attributes (``__version__``, ``__title__``, etc.) are
computed automatically via ``FlextVersion.__init_subclass__``.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from importlib.metadata import PackageMetadata, metadata

from flext_api import t
from flext_core.__version__ import FlextVersion


class FlextApiVersion(FlextVersion):
    """flext-api version — MRO-derived from FlextVersion."""

    _metadata: PackageMetadata = metadata("flext-api")


__version__ = FlextApiVersion.__version__
__version_info__ = FlextApiVersion.__version_info__
__title__ = FlextApiVersion.__title__
__description__ = FlextApiVersion.__description__
__author__ = FlextApiVersion.__author__
__author_email__ = FlextApiVersion.__author_email__
__license__ = FlextApiVersion.__license__
__url__ = FlextApiVersion.__url__
__all__: t.MutableSequenceOf[str] = [
    "FlextApiVersion",
    "__author__",
    "__author_email__",
    "__description__",
    "__license__",
    "__title__",
    "__url__",
    "__version__",
    "__version_info__",
]
