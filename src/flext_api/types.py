"""FLEXT API type definitions for enhanced type safety."""

from __future__ import annotations

from typing import TypeVar

# Generic type variable for data types
TData = TypeVar("TData")

# Export for type checking
__all__ = ["TData"]
