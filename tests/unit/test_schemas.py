"""Comprehensive tests for schema validators.

Tests validate schema validator imports and exports.
No mocks - uses actual imports.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_api.schemas import (
    AsyncAPISchemaValidator,
    JSONSchemaValidator,
    OpenAPISchemaValidator,
)


class TestSchemas:
    """Test schema validators imports."""

    def test_schema_validators_importable(self) -> None:
        """Test that all schema validator classes are importable."""
        assert AsyncAPISchemaValidator is not None
        assert JSONSchemaValidator is not None
        assert OpenAPISchemaValidator is not None
