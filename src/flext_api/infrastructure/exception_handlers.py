"""SOLID-compliant exception handling for FLEXT API.

This module implements the Open/Closed Principle by providing extensible
exception handlers that can be added without modifying existing code.
"""

from __future__ import annotations

from flext_core import FlextError, FlextResult

from flext_api import get_logger

# Create logger using flext-core get_logger function
logger = get_logger(__name__)

# ==============================================================================
# OPEN/CLOSED PRINCIPLE: Extensible Exception Handlers
# ==============================================================================


class BaseExceptionHandler:
    """Base class for exception handlers (OCP compliance)."""

    def __init__(self) -> None:
        """Initialize base exception handler."""
        # Use flext-core get_logger function
        self.logger = get_logger(self.__class__.__module__)
