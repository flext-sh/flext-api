"""FLEXT API Retry Helper - Standalone retry logic module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Protocol

from flext_core import FlextLogger, FlextResult


class RetryOperation(Protocol):
    """Protocol for operations that can be retried."""

    def __call__(
        self, *args: object, **kwargs: object
    ) -> Awaitable[FlextResult[object]]:
        """Execute the operation with arguments."""
        ...


class FlextApiRetryHelper:
    """Retry logic service for FLEXT API client operations.

    Provides exponential backoff retry functionality for HTTP requests
    with configurable retry attempts and backoff factors.

    This class was extracted from the monolithic FlextApiClient to follow
    FLEXT "one class per module" architectural principle.
    """

    def __init__(
        self,
        max_retries: int,
        backoff_factor: float = 1.0,
        logger: FlextLogger | None = None,
    ) -> None:
        """Initialize retry helper with retry configuration.

        Args:
            max_retries: Maximum number of retry attempts
            backoff_factor: Factor for exponential backoff calculation
            logger: Optional logger for retry events

        """
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self._logger = logger or FlextLogger(__name__)

    async def execute_with_retry(
        self,
        operation: RetryOperation,
        *args: object,
        **kwargs: object,
    ) -> FlextResult[object]:
        """Execute operation with retry logic and exponential backoff.

        Args:
            operation: Async function to execute with retry logic
            *args: Positional arguments to pass to operation
            **kwargs: Keyword arguments to pass to operation

        Returns:
            FlextResult containing operation result or final error after all retries.

        """
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                self._logger.debug(
                    f"Attempting operation (attempt {attempt + 1}/{self.max_retries + 1})"
                )

                # Execute the operation
                result = await operation(*args, **kwargs)

                if result.is_success:
                    if attempt > 0:
                        self._logger.info(
                            f"Operation succeeded on attempt {attempt + 1}"
                        )
                    return result
                # Operation returned failure result
                last_error = result.error
                if attempt < self.max_retries:
                    self._logger.warning(
                        f"Operation failed on attempt {attempt + 1}: {result.error}"
                    )

            except Exception as e:
                last_error = str(e)
                self._logger.warning(
                    f"Operation raised exception on attempt {attempt + 1}: {e}"
                )

            # If we have more retries, wait with exponential backoff
            if attempt < self.max_retries:
                delay = self.backoff_factor * (2**attempt)
                self._logger.debug(f"Waiting {delay} seconds before retry")
                await asyncio.sleep(delay)

        # All retries exhausted
        error_msg = (
            f"Operation failed after {self.max_retries + 1} attempts: {last_error}"
        )
        self._logger.error(error_msg)
        return FlextResult[object].fail(error_msg)

    async def execute_simple_retry(
        self,
        operation: Callable[[], Awaitable[object]],
    ) -> FlextResult[object]:
        """Execute simple operation with retry logic (no FlextResult return).

        For operations that don't return FlextResult but may raise exceptions.

        Args:
            operation: Simple async function that may raise exceptions

        Returns:
            FlextResult containing operation result or error after all retries.

        """
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                self._logger.debug(
                    f"Attempting simple operation (attempt {attempt + 1}/{self.max_retries + 1})"
                )

                # Execute the operation
                result = await operation()

                if attempt > 0:
                    self._logger.info(
                        f"Simple operation succeeded on attempt {attempt + 1}"
                    )

                return FlextResult[object].ok(result)

            except Exception as e:
                last_error = str(e)
                self._logger.warning(
                    f"Simple operation failed on attempt {attempt + 1}: {e}"
                )

                # If we have more retries, wait with exponential backoff
                if attempt < self.max_retries:
                    delay = self.backoff_factor * (2**attempt)
                    self._logger.debug(f"Waiting {delay} seconds before retry")
                    await asyncio.sleep(delay)

        # All retries exhausted
        error_msg = f"Simple operation failed after {self.max_retries + 1} attempts: {last_error}"
        self._logger.error(error_msg)
        return FlextResult[object].fail(error_msg)

    def calculate_delay(self, attempt: int) -> float:
        """Calculate backoff delay for given attempt number.

        Args:
            attempt: Attempt number (0-based)

        Returns:
            Delay in seconds using exponential backoff.

        """
        return float(self.backoff_factor * (2**attempt))

    def get_retry_info(self) -> dict[str, object]:
        """Get information about retry configuration.

        Returns:
            Dictionary containing retry configuration details.

        """
        return {
            "max_retries": self.max_retries,
            "backoff_factor": self.backoff_factor,
            "total_attempts": self.max_retries + 1,
        }


__all__ = ["FlextApiRetryHelper"]
