"""Authentication Type constants for flext-api domain.

Single responsibility module containing only authentication type constants.
"""

from flext_core import FlextConstants


class FlextApiAuthenticationType(FlextConstants):
    """Authentication type constants for API operations."""

    class AuthenticationType:
        """Authentication type values."""

        NONE = "none"
        BASIC = "basic"
        BEARER = "bearer"
        API_KEY = "api_key"
        OAUTH2 = "oauth2"
        JWT = "jwt"


__all__ = ["FlextApiAuthenticationType"]
