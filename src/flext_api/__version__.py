"""Version and package metadata using importlib.metadata.

Single source of truth pattern following flext-core standards.
All metadata comes from pyproject.toml via importlib.metadata.

Copyright (c) 2025 Algar Telecom. Todos os direitos reservados.
SPDX-License-Identifier: Proprietary
"""

from __future__ import annotations

from importlib.metadata import metadata

try:
    _metadata = metadata("flext_api")
    __version__ = _metadata["Version"]
    __version_info__ = tuple(
        int(part) if part.isdigit() else part for part in __version__.split(".")
    )
except Exception:
    __version__ = "0.0.0"
    __version_info__ = (0, 0, 0)
    _metadata = {}
__title__ = _metadata.get("Name", "flext-api")
__description__ = _metadata.get("Summary", "")
__author__ = _metadata.get("Author", "")
__author_email__ = _metadata.get("Author-Email", "")
__license__ = _metadata.get("License", "")
__url__ = ""
if "Home-Page" in _metadata:
    url_value = _metadata["Home-Page"]
    if isinstance(url_value, str):
        __url__ = url_value

__all__ = [
    "__author__",
    "__author_email__",
    "__description__",
    "__license__",
    "__title__",
    "__url__",
    "__version__",
    "__version_info__",
]
