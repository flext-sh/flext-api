"""Tests for types module.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_api.api_types import TData


class TestTypes:
    """Test cases for type definitions."""

    def test_tdata_typevar(self) -> None:
        """Test TData type variable."""        # TData is a TypeVar, basic existence test
        assert TData is not None
        assert hasattr(TData, "__name__")
        if TData.__name__ != "TData":
            msg = f"Expected {'TData'}, got {TData.__name__}"
            raise AssertionError(msg)

    def test_tdata_usage(self) -> None:
        """Test TData can be used in type annotations."""
        def example_function(data: TData) -> TData:
            """Example function function.

            Args:
                data (TData): Description.

            Returns:
                TData: Description.

            """
            return data

        # Should work with any type
        result1 = example_function("string")
        if result1 != "string":
            msg = f"Expected {'string'}, got {result1}"
            raise AssertionError(msg)

        result2 = example_function(42)
        if result2 != 42:
            msg = f"Expected {42}, got {result2}"
            raise AssertionError(msg)

        result3 = example_function({"key": "value"})
        if result3 != {"key": "value"}:
            msg = f'Expected {{"key": "value"}}, got {result3}'
            raise AssertionError(msg)
