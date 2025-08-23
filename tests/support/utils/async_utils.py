"""Async testing utilities for flext-api.

Provides async test helpers using pytest-asyncio patterns.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar

# Type variable for generic async operations
T = TypeVar("T")


async def run_async_test[T](coro: Awaitable[T]) -> T:
    """Run async test with proper error handling."""
    try:
        return await coro
    except Exception as e:
        raise AssertionError(f"Async test failed: {e}") from e


async def wait_for_condition(
    condition: Callable[[], bool],
    timeout: float = 5.0,
    interval: float = 0.1,
) -> bool:
    """Wait for condition to be true with timeout."""
    elapsed = 0.0
    while elapsed < timeout:
        if condition():
            return True
        await asyncio.sleep(interval)
        elapsed += interval
    return False
