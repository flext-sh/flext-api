"""Comprehensive tests for schema validators.

Tests validate schema validator imports and exports.
No mocks - uses actual imports.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

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

    def test_openapi_load_schema_from_yaml_file(self, tmp_path) -> None:
        schema_path = tmp_path / "openapi.yaml"
        schema_path.write_text(
            "\n".join([
                "openapi: 3.1.0",
                "info:",
                "  title: Sample API",
                "  version: 1.0.0",
                "paths: {}",
            ]),
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

    def test_jsonschema_load_schema_from_yaml_file(self, tmp_path) -> None:
        schema_path = tmp_path / "schema.yaml"
        schema_path.write_text(
            "\n".join([
                "$schema: https://json-schema.org/draft/2020-12/schema",
                "type: object",
                "properties:",
                "  id:",
                "    type: string",
            ]),
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

    def test_asyncapi_load_schema_from_yaml_file(self, tmp_path) -> None:
        schema_path = tmp_path / "asyncapi.yaml"
        schema_path.write_text(
            "\n".join([
                "asyncapi: 2.6.0",
                "info:",
                "  title: Sample Events",
                "  version: 1.0.0",
                "channels: {}",
            ]),
            encoding="utf-8",
        )

        validator = AsyncAPISchemaValidator()
        result = validator.load_schema(str(schema_path))

        assert result.is_success
        assert isinstance(result.value, dict)
        assert result.value["asyncapi"] == "2.6.0"

    @pytest.mark.parametrize(
        ("validator", "schema_path"),
        [
            (OpenAPISchemaValidator(), "/tmp/flext-api-missing-openapi.json"),
            (JSONSchemaValidator(), "/tmp/flext-api-missing-jsonschema.json"),
            (AsyncAPISchemaValidator(), "/tmp/flext-api-missing-asyncapi.json"),
        ],
    )
    def test_schema_load_fails_for_missing_file(
        self, validator, schema_path: str
    ) -> None:
        result = validator.load_schema(schema_path)

        assert result.is_failure
        assert result.error is not None
        assert "Schema file not found" in result.error

    @pytest.fixture
    def invalid_schema_files(self, tmp_path: Path) -> dict[str, Path]:
        openapi_path = tmp_path / "invalid-openapi.json"
        openapi_path.write_text(
            json.dumps({"openapi": "3.1.0", "paths": {}}),
            encoding="utf-8",
        )

        jsonschema_path = tmp_path / "invalid-jsonschema.json"
        jsonschema_path.write_text(
            json.dumps({"type": "invalid-type"}),
            encoding="utf-8",
        )

        asyncapi_path = tmp_path / "invalid-asyncapi.json"
        asyncapi_path.write_text(
            json.dumps({"asyncapi": "2.6.0", "info": {"title": "Sample"}}),
            encoding="utf-8",
        )

        return {
            "openapi": openapi_path,
            "jsonschema": jsonschema_path,
            "asyncapi": asyncapi_path,
        }

    def test_schema_load_fails_for_invalid_openapi(self, invalid_schema_files) -> None:
        validator = OpenAPISchemaValidator()
        result = validator.load_schema(str(invalid_schema_files["openapi"]))

        assert result.is_failure
        assert result.error is not None
        assert "Invalid OpenAPI schema" in result.error

    def test_schema_load_fails_for_invalid_jsonschema(
        self, invalid_schema_files
    ) -> None:
        validator = JSONSchemaValidator()
        result = validator.load_schema(str(invalid_schema_files["jsonschema"]))

        assert result.is_failure
        assert result.error is not None
        assert "Invalid JSON schema" in result.error

    def test_schema_load_fails_for_invalid_asyncapi(self, invalid_schema_files) -> None:
        validator = AsyncAPISchemaValidator()
        result = validator.load_schema(str(invalid_schema_files["asyncapi"]))

        assert result.is_failure
        assert result.error is not None
        assert "Invalid AsyncAPI schema" in result.error
