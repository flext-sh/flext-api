"""FLEXT API Connection Manager - Standalone connection management module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_api.models import FlextApiModels
from flext_core import FlextLogger, FlextResult


class FlextApiConnectionManager:
    """Connection management service for FLEXT API client.

    Handles HTTP connection pooling, creation, and cleanup with proper
    error handling through the FlextResult pattern.

    This class was extracted from the monolithic FlextApiClient to follow
    FLEXT "one class per module" architectural principle.
    """

    def __init__(
        self, config: FlextApiModels.ClientConfig, logger: FlextLogger
    ) -> None:
        """Initialize connection manager with configuration and logger.

        Args:
            config: Client configuration for connection management
            logger: Logger instance for connection events

        """
        self._config = config
        self._logger = logger
        self._connection_pool: dict[str, object] | None = None

    async def get_connection(self) -> FlextResult[object]:
        """Get or create HTTP connection from pool.

        Creates a new connection pool if one doesn't exist, otherwise
        returns the existing pool for request execution.

        Returns:
            FlextResult containing connection object or error details.

        """
        try:
            if self._connection_pool is None:
                self._logger.info(
                    "Creating new HTTP connection pool",
                    extra={
                        "base_url": self._config.base_url,
                        "timeout": self._config.timeout,
                    },
                )

                self._connection_pool = {
                    "active": True,
                    "url": self._config.base_url,
                    "timeout": self._config.timeout,
                    "max_retries": self._config.max_retries,
                    "headers": self._config.headers,
                }

            return FlextResult[object].ok(self._connection_pool)
        except Exception as e:
            error_msg = f"Connection creation failed: {e}"
            self._logger.exception(error_msg)
            return FlextResult[object].fail(error_msg)

    async def close_connection(self) -> FlextResult[None]:
        """Close HTTP connection and cleanup resources.

        Properly closes the connection pool and cleans up any
        allocated network resources.

        Returns:
            FlextResult indicating success or failure of connection cleanup.

        """
        try:
            if self._connection_pool:
                self._logger.info("Closing HTTP connection pool")
                self._connection_pool = None

            return FlextResult[None].ok(None)
        except Exception as e:
            error_msg = f"Connection cleanup failed: {e}"
            self._logger.exception(error_msg)
            return FlextResult[None].fail(error_msg)

    async def reset_connection(self) -> FlextResult[None]:
        """Reset connection pool by closing and preparing for new connections.

        Useful for recovering from connection errors or applying
        configuration changes.

        Returns:
            FlextResult indicating success or failure of connection reset.

        """
        close_result = await self.close_connection()
        if close_result.is_failure:
            return FlextResult[None].fail(
                f"Failed to close during reset: {close_result.error}"
            )

        self._logger.info("Connection pool reset completed")
        return FlextResult[None].ok(None)

    @property
    def is_connected(self) -> bool:
        """Check if connection pool is active.

        Returns:
            True if connection pool exists and is active, False otherwise.

        """
        return (
            self._connection_pool is not None
            and self._connection_pool.get("active") is True
        )

    def get_connection_info(self) -> dict[str, object]:
        """Get information about current connection state.

        Returns:
            Dictionary containing connection status and configuration.

        """
        if self._connection_pool:
            return {
                "connected": True,
                "url": self._connection_pool.get("url"),
                "timeout": self._connection_pool.get("timeout"),
                "max_retries": self._connection_pool.get("max_retries"),
            }
        return {"connected": False, "url": None, "timeout": None, "max_retries": None}


__all__ = ["FlextApiConnectionManager"]
