"""Type definitions for API components.

Simple generic type variable definition used across the API library
for type-safe data handling.

Main export:
    - TData: Generic type variable for flexible data types

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import TypeVar

# Generic type variable for data types
TData = TypeVar("TData")

# Export for type checking
__all__ = ["TData"]
