"""Constants and enumerations for flext-api domain.

All constant values, literals, and enums are centralized here following FLEXT standards.
Only constants and enums - no functions or classes with behavior.
"""

from typing import ClassVar

from flext_core import FlextConstants


class FlextApiConstants(FlextConstants):
    """API-specific constants extending flext-core FlextConstants."""

    DEFAULT_TIMEOUT: ClassVar[int] = 30
    DEFAULT_MAX_RETRIES: ClassVar[int] = 3
    DEFAULT_BASE_URL: ClassVar[str] = "http://localhost:8000"
    API_VERSION: ClassVar[str] = "v1"


__all__ = ["FlextApiConstants"]
