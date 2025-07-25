"""Common validation utilities for FLEXT API.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException


def validate_entity_name(name: str) -> str:
    """Validate and normalize entity name (pipeline, plugin, etc.).

    Args:
        name: The name to validate,

    Returns:
        Normalized lowercase name

    Raises:
        ValueError: If name format is invalid,

    """
    if not name or not name.strip():
        msg = "Name cannot be empty"
        raise ValueError(msg)

    if len(name) < 3 or len(name) > 100:
        msg = "Name must be between 3 and 100 characters"
        raise ValueError(msg)

    if not name.replace("-", "").replace("_", "").isalnum():
        msg = "Name must contain only alphanumeric characters, hyphens, and underscores"
        raise ValueError(msg)

    return name.lower()


def validate_uuid(uuid_str: str, entity_name: str = "ID") -> UUID:
    """Validate UUID string format and convert to UUID object.

    Args:
        uuid_str: String representation of UUID,
        entity_name: Name of the entity for error messages,

    Returns:
        Valid UUID object

    Raises:
        HTTPException: 400 if UUID format is invalid,

    """
    try:
        return UUID(uuid_str)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid {entity_name} format: {e}",
        ) from e
