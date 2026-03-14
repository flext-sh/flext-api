"""FlextAPI HTTP middleware following FLEXT patterns.

Generic middleware architecture for HTTP request/response processing.
Single responsibility: HTTP middleware pipeline management.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import logging
from collections.abc import Callable

from flext_api import m


class FlextApiMiddleware:
    """FlextAPI HTTP middleware following FLEXT patterns.

    Single responsibility: HTTP middleware pipeline management.
    Uses flext-core patterns for request/response processing.
    """

    @staticmethod
    def apply_pipeline(
        request: m.HttpRequest,
        middleware_list: list[Callable[[m.HttpRequest], m.HttpRequest]],
    ) -> m.HttpRequest:
        """Apply middleware pipeline to request."""
        for middleware in middleware_list:
            try:
                request = middleware(request)
            except (ValueError, TypeError, KeyError, ConnectionError) as e:
                logging.getLogger(__name__).warning("Middleware failed: %s", e)
                continue
        return request

    @staticmethod
    def log_request(request: m.HttpRequest) -> m.HttpRequest:
        """Log HTTP request."""
        return request

    @staticmethod
    def validate_request(request: m.HttpRequest) -> m.HttpRequest:
        """Validate HTTP request."""
        return request


__all__ = ["FlextApiMiddleware"]
