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
        self.logger.info(message, extra=kwargs)

    def error(self, message: str, **kwargs: object) -> None:
        """Log error message."""
        self.logger.error(message, extra=kwargs)

    def debug(self, message: str, **kwargs: object) -> None:
        """Log debug message."""
        self.logger.debug(message, extra=kwargs)

    def warning(self, message: str, **kwargs: object) -> None:
        """Log warning message."""
        self.logger.warning(message, extra=kwargs)
