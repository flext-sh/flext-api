"""Version and package metadata using importlib.metadata.

Single source of truth pattern following flext-core standards.
All metadata comes from pyproject.toml via importlib.metadata.

Copyright (c) 2025 Algar Telecom. Todos os direitos reservados.
SPDX-License-Identifier: Proprietary
"""

from __future__ import annotations

from collections.abc import Mapping
from importlib.metadata import metadata

_metadata_map: Mapping[str, str] = {}
try:
    _metadata = metadata("flext_api")
    _metadata_map = {key: value for key, value in _metadata.items()}
    __version__ = _metadata["Version"]
    __version_info__ = tuple(
        int(part) if part.isdigit() else part for part in __version__.split(".")
    )
except Exception:
    __version__ = "0.0.0"
    __version_info__ = (0, 0, 0)
__title__ = _metadata_map.get("Name", "flext-api")
__description__ = _metadata_map.get("Summary", "")
__author__ = _metadata_map.get("Author", "")
__author_email__ = _metadata_map.get("Author-Email", "")
__license__ = _metadata_map.get("License", "")
__url__ = ""
url_value = _metadata_map.get("Home-Page", "")
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
