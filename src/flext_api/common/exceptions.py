"""Common exception handling utilities for FLEXT API.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import inspect
from functools import wraps
from typing import TYPE_CHECKING, Any

from fastapi import HTTPException

if TYPE_CHECKING:
    from collections.abc import Callable


def handle_api_exceptions(
    operation_name: str,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator to handle common API exceptions with consistent error format.

    Args:
        operation_name: Human-readable name of the operation being performed,

    Returns:
        Decorated function that handles exceptions consistently

    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        # Preserve ALL function metadata for FastAPI compatibility
        sig = inspect.signature(func)

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: object) -> Any:
            try:
                return await func(*args, **kwargs)
            except HTTPException:
                raise  # Re-raise HTTP exceptions as-is
            except Exception as e:
                raise HTTPException(
                    status_code=500, detail=f"Failed to {operation_name}: {e}"
                ) from e

        # Preserve complete signature and annotations for FastAPI
        wrapper.__signature__ = sig  # type: ignore[attr-defined]
        wrapper.__annotations__ = getattr(func, "__annotations__", {})

        # Copy other important attributes that FastAPI might check
        for attr in ["__module__", "__qualname__", "__doc__"]:
            if hasattr(func, attr):
                setattr(wrapper, attr, getattr(func, attr))

        return wrapper

    return decorator


def ensure_service_available(service: Any, service_name: str) -> None:
    """Ensure a service is available, raising HTTPException if not.

    Args:
        service: The service instance to check,
        service_name: Human-readable name of the service,

    Raises:
        HTTPException: 503 if service is None,

    """
    if service is None:
        raise HTTPException(
            status_code=503,
            detail=f"{service_name} not available - register implementation",
        )
