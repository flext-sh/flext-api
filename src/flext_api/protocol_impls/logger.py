"""Logger Protocol Implementation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_core import FlextLogger
from flext_core.typings import t

from flext_api.protocols import FlextApiProtocols


class LoggerProtocolImplementation(FlextApiProtocols.Api.Logger.LoggerProtocol):
    """Logger implementation conforming to LoggerProtocol."""

    def __init__(self) -> None:
        """Initialize logger protocol implementation."""
        self.logger = FlextLogger(__name__)

    def info(self, message: str, **kwargs: object) -> None:
        """Log info message."""
        # Convert kwargs to t.GeneralValueType for logger compatibility
        context: dict[str, t.GeneralValueType] = {}
        for key, value in kwargs.items():
            # t.GeneralValueType accepts most object types
            if isinstance(value, (str, int, float, bool, type(None), list, dict)):
                context[key] = value
            else:
                context[key] = str(value)
        self.logger.info(message, return_result=False, **context)

    def error(self, message: str, **kwargs: object) -> None:
        """Log error message."""
        # Convert kwargs to t.GeneralValueType for logger compatibility
        context: dict[str, t.GeneralValueType] = {}
        for key, value in kwargs.items():
            if isinstance(value, (str, int, float, bool, type(None), list, dict)):
                context[key] = value
            else:
                context[key] = str(value)
        self.logger.error(message, return_result=False, **context)

    def debug(self, message: str, **kwargs: object) -> None:
        """Log debug message."""
        # Convert kwargs to t.GeneralValueType for logger compatibility
        context: dict[str, t.GeneralValueType] = {}
        for key, value in kwargs.items():
            if isinstance(value, (str, int, float, bool, type(None), list, dict)):
                context[key] = value
            else:
                context[key] = str(value)
        self.logger.debug(message, return_result=False, **context)

    def warning(self, message: str, **kwargs: object) -> None:
        """Log warning message."""
        # Convert kwargs to t.GeneralValueType for logger compatibility
        context: dict[str, t.GeneralValueType] = {}
        for key, value in kwargs.items():
            if isinstance(value, (str, int, float, bool, type(None), list, dict)):
                context[key] = value
            else:
                context[key] = str(value)
        self.logger.warning(message, return_result=False, **context)
