"""Logger Protocol Implementation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import cast

from flext_core import FlextLogger, t

from flext_api.protocols import FlextApiProtocols as api_protocols
from flext_api.typings import t as api_t


class LoggerProtocolImplementation(api_protocols.Api.Logger.LoggerProtocol):
    """Logger implementation conforming to LoggerProtocol."""

    def __init__(self) -> None:
        """Initialize logger protocol implementation."""
        self.logger = FlextLogger(__name__)

    def _convert_kwargs_to_context(
        self,
        kwargs: dict[str, api_t.GeneralValueType],
    ) -> dict[str, t.GeneralValueType]:
        """Convert kwargs to context dict for logger compatibility."""
        context: dict[str, t.GeneralValueType] = {}
        for key, value in kwargs.items():
            # t.GeneralValueType accepts most object types
            if isinstance(value, (str, int, float, bool, type(None), list, dict)):
                context[key] = value
            else:
                context[key] = str(value)
        return context

    def info(self, message: str, **kwargs: object) -> None:
        """Log info message."""
        context = self._convert_kwargs_to_context(
            cast("dict[str, api_t.GeneralValueType]", kwargs)
        )
        self.logger.info(message, return_result=False, **context)

    def error(self, message: str, **kwargs: object) -> None:
        """Log error message."""
        context = self._convert_kwargs_to_context(
            cast("dict[str, api_t.GeneralValueType]", kwargs)
        )
        self.logger.error(message, return_result=False, **context)

    def debug(self, message: str, **kwargs: object) -> None:
        """Log debug message."""
        context = self._convert_kwargs_to_context(
            cast("dict[str, api_t.GeneralValueType]", kwargs)
        )
        self.logger.debug(message, return_result=False, **context)

    def warning(self, message: str, **kwargs: object) -> None:
        """Log warning message."""
        context = self._convert_kwargs_to_context(
            cast("dict[str, api_t.GeneralValueType]", kwargs)
        )
        self.logger.warning(message, return_result=False, **context)
