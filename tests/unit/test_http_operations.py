"""Unit tests for HTTP operations module.

Tests deprecated http_operations module for backward compatibility.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations


def test_http_operations_module_imports() -> None:
    """Test that http_operations module can be imported without errors."""
    # This module is deprecated but should still be importable for backward compatibility
    import flext_api.http_operations

    # Verify __all__ is empty as expected
    assert flext_api.http_operations.__all__ == []


def test_http_operations_backward_compatibility() -> None:
    """Test backward compatibility of http_operations module."""
    # Ensure the module exists and has expected attributes
    import flext_api.http_operations as http_ops

    # Should have docstring
    assert "Generic HTTP Operations" in http_ops.__doc__

    # Should have empty __all__
    assert hasattr(http_ops, "__all__")
    assert http_ops.__all__ == []
