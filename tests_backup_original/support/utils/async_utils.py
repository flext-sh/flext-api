"""Async testing utilities for flext-api.

Provides async test helpers using pytest-asyncio patterns.


Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
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
        msg = f"Async test failed: {e}"
        raise AssertionError(msg) from e


async def wait_for_condition(
    condition: Callable[[], bool],
    timeout_seconds: float = 5.0,
    interval: float = 0.1,
) -> bool:
    """Wait for condition to be true with timeout."""
    elapsed = 0.0
    while elapsed < timeout_seconds:
        if condition():
            return True
        await asyncio.sleep(interval)
        elapsed += interval
    return False
