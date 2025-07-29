"""Tests for types module."""

from __future__ import annotations

from flext_api.types import TData


class TestTypes:
    """Test cases for type definitions."""

    def test_tdata_typevar(self) -> None:
        """Test TData type variable."""
        # TData is a TypeVar, basic existence test
        assert TData is not None
        assert hasattr(TData, "__name__")
        if TData.__name__ != "TData":
            raise AssertionError(f"Expected {'TData'}, got {TData.__name__}")

    def test_tdata_usage(self) -> None:
        """Test TData can be used in type annotations."""

        def example_function(data: TData) -> TData:
            return data

        # Should work with any type
        result1 = example_function("string")
        if result1 != "string":
            raise AssertionError(f"Expected {'string'}, got {result1}")

        result2 = example_function(42)
        if result2 != 42:
            raise AssertionError(f"Expected {42}, got {result2}")

        result3 = example_function({"key": "value"})
        if result3 != {"key": "value"}:
            raise AssertionError(f'Expected {{"key": "value"}}, got {result3}')
