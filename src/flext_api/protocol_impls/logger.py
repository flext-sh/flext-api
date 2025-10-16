"""Logger Protocol Implementation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_core import FlextLogger

from flext_api.protocols import FlextApiProtocols


class LoggerProtocolImplementation(FlextApiProtocols.LoggerProtocol):
    """Logger implementation conforming to LoggerProtocol."""

    def __init__(self) -> None:
        """Initialize logger protocol implementation."""
        self.logger = FlextLogger(__name__)

    def info(self, message: str, **kwargs: object) -> None:
        """Log info message."""
        # ✅ Use direct kwargs instead of extra={} to prevent global context binding
        self.logger.info(message, **kwargs)

    def error(self, message: str, **kwargs: object) -> None:
        """Log error message."""
        # ✅ Use direct kwargs instead of extra={} to prevent global context binding
        self.logger.error(message, **kwargs)

    def debug(self, message: str, **kwargs: object) -> None:
        """Log debug message."""
        # ✅ Use direct kwargs instead of extra={} to prevent global context binding
        self.logger.debug(message, **kwargs)

    def warning(self, message: str, **kwargs: object) -> None:
        """Log warning message."""
        # ✅ Use direct kwargs instead of extra={} to prevent global context binding
        self.logger.warning(message, **kwargs)
