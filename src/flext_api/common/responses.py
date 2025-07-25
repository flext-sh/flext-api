"""Common response models for FLEXT API.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginatedResponse[T](BaseModel):
    """Generic paginated response to eliminate duplication across list endpoints."""

    items: list[T] = Field(description="List of items")
    total_count: int = Field(description="Total number of items")
    page: int = Field(description="Current page number")
    page_size: int = Field(description="Page size")
    has_next: bool = Field(description="Whether there are more pages")
    has_previous: bool = Field(description="Whether there are previous pages")


def create_health_check_response(
    entity_name: str,
    is_healthy: bool,
    message: str | None = None,
    error_message: str | None = None,
    details: Any = None,
) -> dict[str, Any]:
    """Create standardized health check response format.

    Args:
        entity_name: Name of the entity being checked,
        is_healthy: Whether the health check passed,
        message: Optional success message,
        error_message: Optional error message,
        details: Optional additional details,

    Returns:
        Standardized health check response dictionary

    """
    return {
        f"{entity_name}_name": entity_name,
        "status": "healthy" if is_healthy else "unhealthy",
        "message": message or "Health check completed",
        "error": error_message or "",
        "timestamp": datetime.now(UTC).isoformat(),
        "details": str(details) if details else "{}",
    }
