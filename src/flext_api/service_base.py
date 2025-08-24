"""Minimal base service for fixing imports."""

from __future__ import annotations

from typing import TypeVar

from flext_core import FlextDomainService, FlextResult, get_logger

logger = get_logger(__name__)

# Type variable for service responses
T = TypeVar("T")


class FlextApiBaseService(FlextDomainService[dict[str, object]]):
    """Base service for all FLEXT API services."""

    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._is_running = False

    def execute(self) -> FlextResult[dict[str, object]]:
        """Execute service operation (sync version from base class)."""
        return FlextResult[dict[str, object]].ok({})

    async def execute_async(self, _request: object) -> FlextResult[dict[str, object]]:
        """Execute service operation with request parameter (async version)."""
        return FlextResult[dict[str, object]].ok({})

    def start(self) -> FlextResult[None]:
        """Start the service."""
        logger.info("Starting service", service_type=type(self).__name__)
        self._is_running = True
        return FlextResult[None].ok(None)

    def stop(self) -> FlextResult[None]:
        """Stop the service."""
        logger.info("Stopping service", service_type=type(self).__name__)
        self._is_running = False
        return FlextResult[None].ok(None)

    def health_check(self) -> FlextResult[dict[str, object]]:
        """Perform health check."""
        return FlextResult[dict[str, object]].ok({
            "status": "healthy" if self._is_running else "stopped",
            "service": type(self).__name__,
            "is_running": self._is_running,
        })

    async def start_async(self) -> FlextResult[None]:
        """Async start service."""
        result = self.start()
        if result.success:
            try:
                return await self._do_start()
            except NotImplementedError:
                # _do_start not implemented, just return the base start result
                return result
            except Exception as e:
                logger.exception("Async start failed")
                return FlextResult[None].fail(f"Async start error: {e}")
        return result

    async def stop_async(self) -> FlextResult[None]:
        """Async stop service."""
        try:
            stop_result = await self._do_stop()
            if not stop_result.success:
                # Log warning but still proceed with base stop
                logger.warning(
                    "Custom stop logic failed, proceeding with base stop",
                    error=stop_result.error,
                )
            return self.stop()
        except NotImplementedError:
            # _do_stop not implemented, just use base stop
            return self.stop()
        except Exception as e:
            logger.exception("Async stop failed")
            return FlextResult[None].fail(f"Async stop error: {e}")

    async def health_check_async(self) -> FlextResult[dict[str, object]]:
        """Async health check."""
        base_result = self.health_check()
        if not base_result.success:
            return base_result

        # Try to get additional health details if implemented
        try:
            details_result = await self._get_health_details()
            if not details_result.success:
                return FlextResult[dict[str, object]].fail(
                    details_result.error or "Health details check failed"
                )

            # Merge base health info with custom details
            health_data = base_result.value
            health_data.update(details_result.value)
            return FlextResult[dict[str, object]].ok(health_data)
        except NotImplementedError:
            # _get_health_details not implemented, just return base result
            return base_result
        except Exception as e:
            logger.exception("Health details check failed")
            return FlextResult[dict[str, object]].fail(f"Health details error: {e}")

    @property
    def is_running(self) -> bool:
        """Check if service is running."""
        return self._is_running

    async def _do_start(self) -> FlextResult[None]:
        """Override this method for async start logic."""
        # Default implementation does nothing
        return FlextResult[None].ok(None)

    async def _do_stop(self) -> FlextResult[None]:
        """Override this method for async stop logic."""
        # Default implementation does nothing
        return FlextResult[None].ok(None)

    async def _get_health_details(self) -> FlextResult[dict[str, object]]:
        """Override this method for custom health details."""
        # Default implementation returns empty details
        return FlextResult[dict[str, object]].ok({})


# ELIMINATION: All specialized base services removed
# Use flext-core protocols instead:
# - FlextProtocols.Domain.Service for generic services
# - FlextProtocols.Domain.Repository[T] for repositories
# - FlextProtocols.Application.Handler[TInput, TOutput] for handlers
# - FlextProtocols.Infrastructure.Auth for authentication
# - Custom streaming can extend FlextApiBaseService directly

# Export only the main base service - protocols come from flext-core
__all__: list[str] = ["FlextApiBaseService"]
