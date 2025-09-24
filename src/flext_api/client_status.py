"""Client Status constants for flext-api domain.

Single responsibility module containing only client status constants.
"""

from flext_core import FlextConstants


class FlextApiClientStatus(FlextConstants):
    """Client status constants for API operations."""

    class ClientStatus:
        """Client status values."""

        IDLE = "idle"
        CONNECTING = "connecting"
        CONNECTED = "connected"
        DISCONNECTING = "disconnecting"
        DISCONNECTED = "disconnected"
        ERROR = "error"


__all__ = ["FlextApiClientStatus"]
