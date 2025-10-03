"""Logger Protocol Implementation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_api.protocols import FlextApiProtocols
from flext_core import FlextLogger


class LoggerProtocolImplementation(FlextApiProtocols.LoggerProtocol):
    """Logger implementation conforming to LoggerProtocol."""

    def __init__(self) -> None:
        """Initialize logger protocol implementation."""
        self._logger = FlextLogger(__name__)

    def info(self, message: str, **kwargs: object) -> None:
        """Log info message."""
        self._logger.info(message, extra=kwargs)

    def error(self, message: str, **kwargs: object) -> None:
        """Log error message."""
        self._logger.error(message, extra=kwargs)

    def debug(self, message: str, **kwargs: object) -> None:
        """Log debug message."""
        self._logger.debug(message, extra=kwargs)

    def warning(self, message: str, **kwargs: object) -> None:
        """Log warning message."""
        self._logger.warning(message, extra=kwargs)
