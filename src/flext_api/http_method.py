"""HTTP Method constants for flext-api domain.

Single responsibility module containing only HTTP method constants.
"""

from flext_core import FlextConstants


class FlextApiHttpMethod(FlextConstants):
    """HTTP method constants for API operations."""

    class HttpMethod:
        """HTTP method values."""

        GET = "GET"
        POST = "POST"
        PUT = "PUT"
        DELETE = "DELETE"
        PATCH = "PATCH"
        HEAD = "HEAD"
        OPTIONS = "OPTIONS"
        TRACE = "TRACE"
        CONNECT = "CONNECT"


__all__ = ["FlextApiHttpMethod"]
