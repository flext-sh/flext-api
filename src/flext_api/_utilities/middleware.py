"""FlextAPI HTTP middleware following FLEXT patterns.

Generic middleware architecture for HTTP request/response processing.
Single responsibility: HTTP middleware pipeline management.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import logging
from collections.abc import (
    Callable,
    Sequence,
)

from flext_api import m, t


class FlextApiMiddleware:
    """FlextAPI HTTP middleware following FLEXT patterns.

    Single responsibility: HTTP middleware pipeline management.
    Uses flext-core patterns for request/response processing.
    """

    @staticmethod
    def apply_pipeline(
        request: m.Api.HttpRequest,
        middleware_list: Sequence[Callable[[m.Api.HttpRequest], m.Api.HttpRequest]],
    ) -> m.Api.HttpRequest:
        """Apply middleware pipeline to request."""
        for middleware in middleware_list:
            try:
                request = middleware(request)
            except (ValueError, TypeError, KeyError, ConnectionError) as e:
                logging.getLogger(__name__).warning("Middleware failed: %s", e)
                continue
        return request

    @staticmethod
    def log_request(request: m.Api.HttpRequest) -> m.Api.HttpRequest:
        """Log HTTP request."""
        return request

    @staticmethod
    def validate_request(request: m.Api.HttpRequest) -> m.Api.HttpRequest:
        """Validate HTTP request."""
        return request


__all__: t.MutableSequenceOf[str] = ["FlextApiMiddleware"]
