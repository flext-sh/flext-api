"""Version and package metadata for flext-api.

Consolidated version information with structured metadata.
"""

from __future__ import annotations

from importlib.metadata import metadata
from typing import Final

# Package metadata from importlib.metadata
_metadata = metadata("flext-api")

__version__ = _metadata["Version"]
__version_info__ = tuple(
    int(part) if part.isdigit() else part for part in __version__.split(".")
)
__title__ = _metadata["Name"]
__description__ = _metadata["Summary"]
__author__ = _metadata.get("Author")
__author_email__ = _metadata.get("Author-Email")
__license__ = _metadata.get("License")
__url__ = _metadata.get("Home-Page")


class FlextApiVersion:
    """Structured metadata for the flext api distribution."""

    def __init__(self, version: str, version_info: tuple[int | str, ...]) -> None:
        """Initialize version information.

        Args:
            version: Version string
            version_info: Version info tuple

        """
        self._version = version
        self._version_info = version_info

    @property
    def version(self) -> str:
        """Return the version string."""
        return self._version

    @property
    def version_info(self) -> tuple[int | str, ...]:
        """Return the version info tuple."""
        return self._version_info

    @classmethod
    def current(cls) -> FlextApiVersion:
        """Return canonical metadata loaded from package."""
        return cls(__version__, __version_info__)


VERSION: Final[FlextApiVersion] = FlextApiVersion.current()

__all__ = [
    "VERSION",
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
