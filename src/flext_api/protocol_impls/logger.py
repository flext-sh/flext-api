"""Logger Protocol Implementation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import override

from flext_core import FlextLogger, FlextRuntime

from flext_api import FlextApiProtocols as api_protocols, t


class LoggerProtocolImplementation(api_protocols.Api.Logger.LoggerProtocol):
    """Logger implementation conforming to LoggerProtocol."""

    def __init__(self) -> None:
        """Initialize logger protocol implementation."""
        self.logger = FlextLogger(__name__)

    def _convert_kwargs_to_context(
        self,
        kwargs: Mapping[str, t.ContainerValue],
    ) -> Mapping[str, t.ContainerValue]:
        """Convert kwargs to context dict for logger compatibility."""
        context: dict[str, t.ContainerValue] = {}
        for key, value in kwargs.items():
            if value is None or isinstance(value, str | int | float | bool):
                context[key] = value
                continue
            if isinstance(value, (Mapping, Sequence)):
                context[key] = FlextRuntime.normalize_to_general_value(value)
                continue
            context[key] = str(value)
        return context

    @override
    def info(self, message: str, **kwargs: t.ContainerValue) -> None:
        """Log info message."""
        context = self._convert_kwargs_to_context(kwargs)
        self.logger.info(message, return_result=False, **context)

    @override
    def error(self, message: str, **kwargs: t.ContainerValue) -> None:
        """Log error message."""
        context = self._convert_kwargs_to_context(kwargs)
        self.logger.error(message, return_result=False, **context)

    @override
    def debug(self, message: str, **kwargs: t.ContainerValue) -> None:
        """Log debug message."""
        context = self._convert_kwargs_to_context(kwargs)
        self.logger.debug(message, return_result=False, **context)

    @override
    def warning(self, message: str, **kwargs: t.ContainerValue) -> None:
        """Log warning message."""
        context = self._convert_kwargs_to_context(kwargs)
        self.logger.warning(message, return_result=False, **context)
