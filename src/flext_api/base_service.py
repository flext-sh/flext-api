"""Minimal base service for fixing imports."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, TypeVar

from flext_core import FlextDomainService, FlextResult, get_logger

logger = get_logger(__name__)

# Type variable for service responses
T = TypeVar('T')

class FlextApiBaseService(FlextDomainService):
    """Base service for all FLEXT API services."""

    def __init__(self) -> None:
        super().__init__()

    async def execute(self, request: Any) -> FlextResult[Any]:
        """Execute service operation."""
        return FlextResult[Any].ok(None)

class FlextApiBaseClientService(FlextApiBaseService):
    """Base client service."""
    pass

class FlextApiBaseBuilderService(FlextApiBaseService):
    """Base builder service."""
    pass

class FlextApiBaseAuthService(FlextApiBaseService):
    """Base authentication service."""
    pass

class FlextApiBaseRepositoryService(FlextApiBaseService):
    """Base repository service."""
    pass

class FlextApiBaseHandlerService(FlextApiBaseService):
    """Base handler service."""
    pass

class FlextApiBaseStreamingService(FlextApiBaseService):
    """Base streaming service."""
    pass