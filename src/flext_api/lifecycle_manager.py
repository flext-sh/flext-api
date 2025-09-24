"""FLEXT API Lifecycle Manager - Standalone client lifecycle management module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_api.models import FlextApiModels
from flext_core import FlextLogger, FlextResult


class FlextApiLifecycleManager:
    """Lifecycle management service for FLEXT API client.

    Handles client startup, shutdown, and resource management with proper
    error handling through the FlextResult pattern.

    This class was extracted from the monolithic FlextApiClient to follow
    FLEXT "one class per module" architectural principle.
    """

    def __init__(
        self, config: FlextApiModels.ClientConfig, logger: FlextLogger
    ) -> None:
        """Initialize lifecycle manager with configuration and logger.

        Args:
            config: Client configuration for lifecycle management
            logger: Logger instance for lifecycle events

        """
        self._config = config
        self._logger = logger
        self._is_started = False

    async def start_client(self) -> FlextResult[None]:
        """Start the HTTP client with resource initialization.

        Initializes HTTP client resources, connection pools, and
        prepares the client for request execution.

        Returns:
            FlextResult indicating success or failure of client startup.

        """
        if self._is_started:
            return FlextResult[None].fail("Client already started")

        try:
            self._logger.info(
                "Starting HTTP client",
                extra={
                    "base_url": getattr(self._config, "base_url", ""),
                    "timeout": getattr(self._config, "timeout", 30),
                },
            )
            self._is_started = True
            return FlextResult[None].ok(None)
        except Exception as e:
            error_msg = f"Failed to start client: {e}"
            self._logger.exception(error_msg)
            return FlextResult[None].fail(error_msg)

    async def stop_client(self) -> FlextResult[None]:
        """Stop the HTTP client and cleanup resources.

        Gracefully shuts down the HTTP client, closes connection pools,
        and cleans up any allocated resources.

        Returns:
            FlextResult indicating success or failure of client shutdown.

        """
        if not self._is_started:
            return FlextResult[None].fail("Client not started")

        try:
            self._logger.info("Stopping HTTP client")
            self._is_started = False
            return FlextResult[None].ok(None)
        except Exception as e:
            error_msg = f"Failed to stop client: {e}"
            self._logger.exception(error_msg)
            return FlextResult[None].fail(error_msg)

    @property
    def is_started(self) -> bool:
        """Check if the client is currently started.

        Returns:
            True if client is started and ready for requests, False otherwise.

        """
        return self._is_started

    async def restart_client(self) -> FlextResult[None]:
        """Restart the HTTP client by stopping and starting again.

        Convenience method that performs a clean shutdown followed by
        startup, useful for configuration changes or error recovery.

        Returns:
            FlextResult indicating success or failure of client restart.

        """
        # Stop client if running
        if self._is_started:
            stop_result = await self.stop_client()
            if stop_result.is_failure:
                return FlextResult[None].fail(
                    f"Failed to stop during restart: {stop_result.error}"
                )

        # Start client
        start_result = await self.start_client()
        if start_result.is_failure:
            return FlextResult[None].fail(
                f"Failed to start during restart: {start_result.error}"
            )

        return FlextResult[None].ok(None)


__all__ = ["FlextApiLifecycleManager"]
