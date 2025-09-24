"""Content Type constants for flext-api domain.

Single responsibility module containing only content type constants.
"""

from flext_core import FlextConstants


class FlextApiContentType(FlextConstants):
    """Content type constants for API operations."""

    class ContentType:
        """Content type values."""

        JSON = "application/json"
        XML = "application/xml"
        FORM = "application/x-www-form-urlencoded"
        MULTIPART = "multipart/form-data"
        TEXT = "text/plain"
        HTML = "text/html"


__all__ = ["FlextApiContentType"]
