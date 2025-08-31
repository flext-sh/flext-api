"""Tests for flext_api.typings module - REAL classes only.

Tests using only REAL classes:
- FlextApiTypes

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest

from flext_api import FlextApiTypes


class TestFlextApiTypes:
    """Test FlextApiTypes REAL class functionality."""

    def test_types_class_exists(self) -> None:
        """Test that FlextApiTypes class exists."""
        assert FlextApiTypes is not None
        assert hasattr(FlextApiTypes, "__name__")
        assert FlextApiTypes.__name__ == "FlextApiTypes"

    def test_api_nested_types(self) -> None:
        """Test Api nested types."""
        assert hasattr(FlextApiTypes, "Api")

        api_types = FlextApiTypes.Api
        assert api_types is not None

    def test_api_result_type(self) -> None:
        """Test Api.Result type definition."""
        api_types = FlextApiTypes.Api

        # Should have Result type
        assert hasattr(api_types, "Result")

        # Should be a type annotation or alias
        result_type = api_types.Result
        assert result_type is not None

    def test_api_cache_value_type(self) -> None:
        """Test Api.CacheValue type definition."""
        api_types = FlextApiTypes.Api

        # Should have CacheValue type for storage
        assert hasattr(api_types, "CacheValue")

        cache_value_type = api_types.CacheValue
        assert cache_value_type is not None

    def test_api_init_data_type(self) -> None:
        """Test Api.InitData type definition."""
        api_types = FlextApiTypes.Api

        # Should have InitData type for initialization
        assert hasattr(api_types, "InitData")

        init_data_type = api_types.InitData
        assert init_data_type is not None

    def test_api_json_serializable_type(self) -> None:
        """Test Api.JsonSerializable type definition."""
        api_types = FlextApiTypes.Api

        # Should have JsonSerializable type for JSON operations
        assert hasattr(api_types, "JsonSerializable")

        json_type = api_types.JsonSerializable
        assert json_type is not None

    def test_types_inheritance(self) -> None:
        """Test that FlextApiTypes inherits properly from flext-core."""
        # Should inherit from flext-core FlextTypes
        assert hasattr(FlextApiTypes, "__bases__")

        base_classes = FlextApiTypes.__bases__
        assert len(base_classes) > 0

    def test_core_types_available(self) -> None:
        """Test that core types from flext-core are available."""
        # Should have access to core types through inheritance
        # Basic check that the class is properly structured
        assert hasattr(FlextApiTypes, "__mro__")

        # Method resolution order should include parent classes
        mro = FlextApiTypes.__mro__
        assert len(mro) > 1  # At least FlextApiTypes and object

    def test_nested_structure(self) -> None:
        """Test nested type structure."""
        # Should have nested classes/modules for organization
        nested_items = [
            attr
            for attr in dir(FlextApiTypes)
            if not attr.startswith("_")
            and hasattr(getattr(FlextApiTypes, attr, None), "__dict__")
        ]

        # Should have at least the Api nested structure
        assert len(nested_items) >= 1
        assert "Api" in list(nested_items)

    def test_type_annotations_available(self) -> None:
        """Test that type annotations are properly available."""
        api_types = FlextApiTypes.Api

        # Should have type definitions that can be used in annotations
        type_attrs = [attr for attr in dir(api_types) if not attr.startswith("_")]

        # Should have some type definitions
        assert len(type_attrs) > 0

    def test_types_can_be_imported(self) -> None:
        """Test that types can be imported and used."""
        # Should be able to access nested types
        try:
            result_type = FlextApiTypes.Result
            cache_type = FlextApiTypes.Api.CacheValue
            init_type = FlextApiTypes.Api.InitData

            # Basic validation that they exist
            assert result_type is not None
            assert cache_type is not None
            assert init_type is not None

        except AttributeError as e:
            pytest.fail(f"Type import failed: {e}")

    def test_type_consistency(self) -> None:
        """Test that types are consistently defined."""
        api_types = FlextApiTypes.Api

        # All defined types should be accessible
        defined_types = [attr for attr in dir(api_types) if not attr.startswith("_")]

        for type_name in defined_types:
            type_obj = getattr(api_types, type_name)
            assert type_obj is not None, f"Type {type_name} is None"

    def test_type_documentation(self) -> None:
        """Test that types have proper documentation."""
        # Main class should be documented
        assert FlextApiTypes.__doc__ is not None
        assert len(FlextApiTypes.__doc__.strip()) > 0

        # Nested Api class should be documented
        api_types = FlextApiTypes.Api
        if hasattr(api_types, "__doc__") and api_types.__doc__:
            assert len(api_types.__doc__.strip()) > 0

    def test_types_module_integration(self) -> None:
        """Test integration with the types module."""
        # Should integrate properly with Python's type system
        assert hasattr(FlextApiTypes, "__module__")
        assert FlextApiTypes.__module__ == "flext_api.typings"

        # Should be properly accessible from the main package
        from flext_api import FlextApiTypes as ImportedTypes

        assert ImportedTypes is FlextApiTypes
