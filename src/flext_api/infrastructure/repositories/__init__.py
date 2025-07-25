"""Repository implementations for FLEXT-API infrastructure layer.

This module provides concrete implementations of domain repository interfaces.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from flext_core import FlextResult

# Import entities for repository signatures (needed at runtime for Pydantic)
# Import entities for repository signatures (not in TYPE_CHECKING to avoid forward refs)
# Import abstract repository interfaces
from flext_api.domain.ports import PipelineRepository, PluginRepository

# Import specific repository implementations
from flext_api.infrastructure.repositories.pipeline_repository import (
    FlextInMemoryPipelineRepository,
)
from flext_api.infrastructure.repositories.plugin_repository import (
    FlextInMemoryPluginRepository,
)

if TYPE_CHECKING:
    from flext_api.base import FlextAPIResponse
    from flext_api.domain.entities import FlextAPIRequest


class APIRequestRepository(ABC):
    """Repository interface for API Request entities."""

    @abstractmethod
    async def save(self, request: FlextAPIRequest) -> FlextResult[Any]:
        """Save an API request."""

    @abstractmethod
    async def find_by_id(self, request_id: str) -> FlextResult[Any]:
        """Find API request by ID."""

    @abstractmethod
    async def get_by_endpoint(self, endpoint: str) -> FlextResult[Any]:
        """Get API requests by endpoint."""


class APIResponseRepository(ABC):
    """Repository interface for API Response entities."""

    @abstractmethod
    async def save(self, response: FlextAPIResponse[Any]) -> FlextResult[Any]:
        """Save an API response."""

    @abstractmethod
    async def get_by_request_id(self, request_id: str) -> FlextResult[Any]:
        """Get API response by request ID."""

    @abstractmethod
    async def get_by_status_code(self, status_code: int) -> FlextResult[Any]:
        """Get API responses by status code."""


class InMemoryAPIRequestRepository(APIRequestRepository):
    """In-memory implementation of API Request repository."""

    def __init__(self) -> None:
        """Initialize the repository."""
        self._requests: dict[str, FlextAPIRequest] = {}

    async def save(self, request: FlextAPIRequest) -> FlextResult[Any]:
        """Save an API request."""
        try:
            self._requests[request.request_id] = request
            return FlextResult.ok(request)
        except (KeyError, ValueError, TypeError, AttributeError) as e:
            return FlextResult.fail(f"Failed to save API request: {e}")

    async def find_by_id(self, request_id: str) -> FlextResult[Any]:
        """Find API request by ID."""
        try:
            request = self._requests.get(request_id)
            return FlextResult.ok(request)
        except (KeyError, ValueError, TypeError, AttributeError) as e:
            return FlextResult.fail(f"Failed to get API request: {e}")

    async def get_by_endpoint(self, endpoint: str) -> FlextResult[Any]:
        """Get API requests by endpoint."""
        try:
            requests = [
                req for req in self._requests.values() if req.endpoint == endpoint
            ]
            return FlextResult.ok(requests)
        except (KeyError, ValueError, TypeError, AttributeError) as e:
            return FlextResult.fail(f"Failed to get API requests by endpoint: {e}")


class InMemoryAPIResponseRepository(APIResponseRepository):
    """In-memory implementation of API Response repository."""

    def __init__(self) -> None:
        """Initialize the repository."""
        self._responses: dict[str, FlextAPIResponse[Any]] = {}

    async def save(self, response: FlextAPIResponse[Any]) -> FlextResult[Any]:
        """Save an API response."""
        try:
            # Use a safe key since response_id may not exist on FlextAPIResponse
            response_key = getattr(response, "response_id", str(id(response)))
            self._responses[response_key] = response
            return FlextResult.ok(response)
        except (KeyError, ValueError, TypeError, AttributeError) as e:
            return FlextResult.fail(f"Failed to save API response: {e}")

    async def get_by_request_id(self, request_id: str) -> FlextResult[Any]:
        """Get API response by request ID."""
        try:
            response = next(
                (
                    resp
                    for resp in self._responses.values()
                    if getattr(resp, "request_id", None) == request_id
                ),
                None,
            )
            return FlextResult.ok(response)
        except (KeyError, ValueError, TypeError, AttributeError, StopIteration) as e:
            return FlextResult.fail(f"Failed to get API response: {e}")

    async def get_by_status_code(self, status_code: int) -> FlextResult[Any]:
        """Get API responses by status code."""
        try:
            responses = [
                resp
                for resp in self._responses.values()
                if getattr(resp, "status_code", None) == status_code
            ]
            return FlextResult.ok(responses)
        except (KeyError, ValueError, TypeError, AttributeError) as e:
            return FlextResult.fail(f"Failed to get API responses by status code: {e}")


__all__ = [
    "APIRequestRepository",
    "APIResponseRepository",
    "FlextInMemoryPipelineRepository",
    "FlextInMemoryPluginRepository",
    "InMemoryAPIRequestRepository",
    "InMemoryAPIResponseRepository",
    "PipelineRepository",
    "PluginRepository",
]
