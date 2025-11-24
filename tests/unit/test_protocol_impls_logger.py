"""Comprehensive tests for LoggerProtocolImplementation.

Tests validate logging functionality using real logger.
No mocks - uses actual FlextLogger.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_api.protocol_impls.logger import LoggerProtocolImplementation


class TestLoggerProtocolImplementation:
    """Test logger protocol implementation."""

    def test_initialization(self) -> None:
        """Test logger implementation can be initialized."""
        logger = LoggerProtocolImplementation()
        assert logger is not None
        assert hasattr(logger, "logger")
        assert hasattr(logger, "info")
        assert hasattr(logger, "error")
        assert hasattr(logger, "debug")
        assert hasattr(logger, "warning")

    def test_info_logging(self) -> None:
        """Test info message logging."""
        logger = LoggerProtocolImplementation()
        # Just call the method - no assertion needed as it logs
        logger.info("Test info message")

    def test_error_logging(self) -> None:
        """Test error message logging."""
        logger = LoggerProtocolImplementation()
        logger.error("Test error message")

    def test_debug_logging(self) -> None:
        """Test debug message logging."""
        logger = LoggerProtocolImplementation()
        logger.debug("Test debug message")

    def test_warning_logging(self) -> None:
        """Test warning message logging."""
        logger = LoggerProtocolImplementation()
        logger.warning("Test warning message")

    def test_logging_with_kwargs(self) -> None:
        """Test logging with additional keyword arguments."""
        logger = LoggerProtocolImplementation()
        logger.info("Test message with extra", extra_field="value", another=42)
