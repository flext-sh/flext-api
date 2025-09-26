"""Request Status constants for flext-api domain.

Single responsibility module containing only request status constants.
"""

from __future__ import annotations

from flext_core import FlextConstants


class FlextApiRequestStatus(FlextConstants):
    """Request status constants for API operations."""

    class RequestStatus:
        """Request status values."""

        PENDING = "pending"
        IN_PROGRESS = "in_progress"
        COMPLETED = "completed"
        FAILED = "failed"
        CANCELLED = "cancelled"
        TIMEOUT = "timeout"


__all__ = ["FlextApiRequestStatus"]
