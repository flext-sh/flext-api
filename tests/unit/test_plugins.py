"""Comprehensive tests for FlextApiPlugins system.

Tests validate plugin lifecycle management using railway-oriented programming
with FlextResult[T] error handling. ALL TESTS USE REAL FUNCTIONALITY - NO MOCKS.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_api.plugins import FlextApiPlugins


class TestFlextApiPluginsPlugin:
    """Test Plugin base class functionality."""

    def test_plugin_initialization(self) -> None:
        """Test plugin initialization with metadata."""
        plugin = FlextApiPlugins.Plugin(
            name="test_plugin",
            version="1.2.3",
            description="Test plugin for unit tests",
        )

        assert plugin.name == "test_plugin"
        assert plugin.version == "1.2.3"
        assert plugin.description == "Test plugin for unit tests"
        assert not plugin._initialized

    def test_plugin_logger_property(self) -> None:
        """Test plugin logger property access."""
        plugin = FlextApiPlugins.Plugin(name="test_plugin")

        # Logger should be accessible
        logger = plugin.logger
        assert logger is not None
        assert hasattr(logger, "debug")
        assert hasattr(logger, "info")

    def test_plugin_lifecycle(self) -> None:
        """Test plugin initialize/shutdown lifecycle."""
        plugin = FlextApiPlugins.Plugin(name="test_plugin")

        # Test initialization
        init_result = plugin.initialize()
        assert init_result.is_success
        assert init_result.value is True
        assert plugin._initialized

        # Test shutdown
        shutdown_result = plugin.shutdown()
        assert shutdown_result.is_success
        assert shutdown_result.value is True
        assert not plugin._initialized

    def test_plugin_double_initialization(self) -> None:
        """Test that double initialization fails."""
        plugin = FlextApiPlugins.Plugin(name="test_plugin")

        # First initialization should succeed
        init_result1 = plugin.initialize()
        assert init_result1.is_success

        # Second initialization should fail
        init_result2 = plugin.initialize()
        assert init_result2.is_failure
        assert init_result2.error is not None and "already initialized" in init_result2.error

    def test_plugin_shutdown_without_initialization(self) -> None:
        """Test shutdown without prior initialization."""
        plugin = FlextApiPlugins.Plugin(name="test_plugin")

        # Shutdown should fail without initialization
        shutdown_result = plugin.shutdown()
        assert shutdown_result.is_failure
        assert shutdown_result.error is not None and "not initialized" in shutdown_result.error


class TestFlextApiPluginsSchema:
    """Test Schema plugin type."""

    def test_schema_plugin_creation(self) -> None:
        """Test creation of Schema plugin."""
        schema = FlextApiPlugins.Schema(
            name="test_schema",
            version="2.0.0",
        )

        assert schema.name == "test_schema"
        assert schema.version == "2.0.0"
        assert hasattr(schema, "logger")

    def test_schema_plugin_abstract_methods(self) -> None:
        """Test that Schema plugin has expected abstract methods."""
        schema = FlextApiPlugins.Schema(name="test_schema")

        # Should have lifecycle methods from Plugin base class
        assert hasattr(schema, "initialize")
        assert hasattr(schema, "shutdown")
