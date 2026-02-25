"""Comprehensive tests for schema validators.

Tests validate schema validator imports and exports.
No mocks - uses actual imports.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json

from flext_api import (
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

    def test_openapi_load_schema_from_json_file(self, tmp_path) -> None:
        schema_path = tmp_path / "openapi.json"
        schema_path.write_text(
            json.dumps({
                "openapi": "3.1.0",
                "info": {"title": "Sample API", "version": "1.0.0"},
                "paths": {},
            }),
            encoding="utf-8",
        )

        validator = OpenAPISchemaValidator()
        result = validator.load_schema(str(schema_path))

        assert result.is_success
        assert isinstance(result.value, dict)
        assert result.value["openapi"] == "3.1.0"

    def test_jsonschema_load_schema_from_json_file(self, tmp_path) -> None:
        schema_path = tmp_path / "schema.json"
        schema_path.write_text(
            json.dumps({
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "type": "object",
                "properties": {"name": {"type": "string"}},
            }),
            encoding="utf-8",
        )

        validator = JSONSchemaValidator()
        result = validator.load_schema(str(schema_path))

        assert result.is_success
        assert isinstance(result.value, dict)
        assert result.value["type"] == "object"

    def test_asyncapi_load_schema_from_json_file(self, tmp_path) -> None:
        schema_path = tmp_path / "asyncapi.json"
        schema_path.write_text(
            json.dumps({
                "asyncapi": "2.6.0",
                "info": {"title": "Sample Events", "version": "1.0.0"},
                "channels": {},
            }),
            encoding="utf-8",
        )

        validator = AsyncAPISchemaValidator()
        result = validator.load_schema(str(schema_path))

        assert result.is_success
        assert isinstance(result.value, dict)
        assert result.value["asyncapi"] == "2.6.0"

    def test_schema_load_fails_for_missing_file(self) -> None:
        validator = OpenAPISchemaValidator()
        result = validator.load_schema("/tmp/flext-api-missing-schema.json")

        assert result.is_failure
        assert result.error is not None
        assert "Schema file not found" in result.error
