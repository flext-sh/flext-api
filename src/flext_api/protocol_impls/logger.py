"""Logger Protocol Implementation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import (
    Mapping,
    Sequence,
)
from typing import override

from flext_api import p, t, u


class FlextApiLoggerProtocolImplementation(p.Api.Logger):
    """Logger implementation conforming to Logger."""

    def __init__(self) -> None:
        """Initialize logger protocol implementation."""
        self.logger = u.fetch_logger(__name__)

    @override
    def debug(self, message: str, **kwargs: t.JsonValue) -> None:
        """Log debug message."""
        context = self._convert_kwargs_to_context(kwargs)
        self.logger.debug(message, return_result=False, **context)

    @override
    def error(self, message: str, **kwargs: t.JsonValue) -> None:
        """Log error message."""
        context = self._convert_kwargs_to_context(kwargs)
        self.logger.error(message, return_result=False, **context)

    @override
    def info(self, message: str, **kwargs: t.JsonValue) -> None:
        """Log info message."""
        context = self._convert_kwargs_to_context(kwargs)
        self.logger.info(message, return_result=False, **context)

    @override
    def warning(self, message: str, **kwargs: t.JsonValue) -> None:
        """Log warning message."""
        context = self._convert_kwargs_to_context(kwargs)
        self.logger.warning(message, return_result=False, **context)

    def _convert_kwargs_to_context(
        self,
        kwargs: t.JsonMapping,
    ) -> t.JsonMapping:
        """Convert kwargs to context dict for logger compatibility."""
        context: dict[str, t.JsonValue] = {}
        for key, value in kwargs.items():
            if value is None:
                context[key] = "<unstructured>"
                continue
            if isinstance(value, Mapping) or (
                isinstance(value, Sequence) and not isinstance(value, (str, bytes))
            ):
                context[key] = "<structured>"
                continue
            if u.container(value):
                context[key] = value
                continue
            context[key] = "<unstructured>"
        return context


__all__: list[str] = ["FlextApiLoggerProtocolImplementation"]
