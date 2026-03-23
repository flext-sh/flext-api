"""Logger Protocol Implementation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import override

from flext_core import FlextLogger

from flext_api import FlextApiProtocols as api_protocols, t, u


class LoggerProtocolImplementation(api_protocols.Api.Logger.Logger):
    """Logger implementation conforming to Logger."""

    def __init__(self) -> None:
        """Initialize logger protocol implementation."""
        self.logger = FlextLogger(__name__)

    @override
    def debug(self, message: str, **kwargs: t.Scalar) -> None:
        """Log debug message."""
        context = self._convert_kwargs_to_context(kwargs)
        self.logger.debug(message, return_result=False, **context)

    @override
    def error(self, message: str, **kwargs: t.Scalar) -> None:
        """Log error message."""
        context = self._convert_kwargs_to_context(kwargs)
        self.logger.error(message, return_result=False, **context)

    @override
    def info(self, message: str, **kwargs: t.Scalar) -> None:
        """Log info message."""
        context = self._convert_kwargs_to_context(kwargs)
        self.logger.info(message, return_result=False, **context)

    @override
    def warning(self, message: str, **kwargs: t.Scalar) -> None:
        """Log warning message."""
        context = self._convert_kwargs_to_context(kwargs)
        self.logger.warning(message, return_result=False, **context)

    def _convert_kwargs_to_context(
        self,
        kwargs: Mapping[str, t.ApiJsonValue],
    ) -> Mapping[str, t.Container]:
        """Convert kwargs to context dict for logger compatibility."""
        context: Mapping[str, t.Container] = {}
        for key, value in kwargs.items():
            if u.is_container(value):
                context[key] = value
                continue
            if isinstance(value, (Mapping, Sequence)):
                context[key] = "<structured>"
                continue
            context[key] = "<unstructured>"
        return context
