"""Simple unit tests for schema validators.

Focused tests for OpenAPI, JSON Schema, and API validators.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_api.schemas import (
    AsyncAPISchemaValidator,
    JSONSchemaValidator,
    OpenAPISchemaValidator,
)


class TestOpenAPISchemaValidator:
    """Simple test suite for OpenAPISchemaValidator."""

    def test_validator_initialization(self) -> None:
        """Test OpenAPI validator initialization."""
        validator = OpenAPISchemaValidator(
            strict_mode=True,
            validate_examples=True,
            validate_responses=True,
        )

        assert validator is not None
        assert validator.name == "openapi"
        assert validator._strict_mode is True
        assert validator._validate_examples is True
        assert validator._validate_responses is True

    def test_validator_supports_schema(self) -> None:
        """Test schema type support checking."""
        validator = OpenAPISchemaValidator()

        assert validator.supports_schema("openapi") is True
        assert validator.supports_schema("openapi3") is True
        assert validator.supports_schema("openapi-3") is True
        assert validator.supports_schema("json-schema") is False

    def test_validator_get_supported_schemas(self) -> None:
        """Test getting list of supported schemas."""
        validator = OpenAPISchemaValidator()

        schemas = validator.get_supported_schemas()

        assert "openapi" in schemas
        assert "openapi3" in schemas
        assert "openapi-3" in schemas

    def test_validate_minimal_openapi_schema(self) -> None:
        """Test validation of minimal OpenAPI schema."""
        validator = OpenAPISchemaValidator()

        schema = {
            "openapi": "3.0.0",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {},
        }

        result = validator.validate_schema(schema)

        assert result.is_success
        assert result.unwrap()["valid"] is True
        assert result.unwrap()["version"] == "3.0.0"

    def test_validate_openapi_missing_version(self) -> None:
        """Test validation fails for missing openapi version."""
        validator = OpenAPISchemaValidator()

        schema = {
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {},
        }

        result = validator.validate_schema(schema)

        assert result.is_failure
        assert "Missing 'openapi' version field" in result.error

    def test_validate_openapi_missing_info(self) -> None:
        """Test validation fails for missing info."""
        validator = OpenAPISchemaValidator()

        schema = {"openapi": "3.0.0", "paths": {}}

        result = validator.validate_schema(schema)

        assert result.is_failure
        assert "Missing required fields" in result.error

    def test_validate_openapi_with_paths(self) -> None:
        """Test validation of OpenAPI schema with paths."""
        validator = OpenAPISchemaValidator()

        schema = {
            "openapi": "3.1.0",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {
                "/users": {
                    "get": {
                        "summary": "Get users",
                        "responses": {"200": {"description": "Success"}},
                    }
                }
            },
        }

        result = validator.validate_schema(schema)

        assert result.is_success
        assert "/users" in result.unwrap()["paths"]

    def test_validate_openapi_invalid_path(self) -> None:
        """Test validation fails for invalid path."""
        validator = OpenAPISchemaValidator()

        schema = {
            "openapi": "3.0.0",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {"users": {"get": {"responses": {"200": {"description": "OK"}}}}},
        }

        result = validator.validate_schema(schema)

        assert result.is_failure
        assert "Path must start with '/'" in result.error

    def test_validate_openapi_with_security_schemes(self) -> None:
        """Test validation of OpenAPI with security schemes."""
        validator = OpenAPISchemaValidator()

        schema = {
            "openapi": "3.0.0",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {},
            "components": {
                "securitySchemes": {"bearerAuth": {"type": "http", "scheme": "bearer"}}
            },
        }

        result = validator.validate_schema(schema)

        assert result.is_success


class TestJSONSchemaValidator:
    """Simple test suite for JSONSchemaValidator."""

    def test_validator_initialization(self) -> None:
        """Test JSON Schema validator initialization."""
        validator = JSONSchemaValidator(
            draft_version="draft7",
            validate_formats=True,
            strict_mode=True,
        )

        assert validator is not None
        assert validator.name == "jsonschema"
        assert validator._draft_version == "draft7"
        assert validator._validate_formats is True
        assert validator._strict_mode is True

    def test_validator_supports_schema(self) -> None:
        """Test schema type support checking."""
        validator = JSONSchemaValidator()

        assert validator.supports_schema("json-schema") is True
        assert validator.supports_schema("jsonschema") is True
        assert validator.supports_schema("json") is True
        assert validator.supports_schema("openapi") is False

    def test_validator_get_supported_schemas(self) -> None:
        """Test getting list of supported schemas."""
        validator = JSONSchemaValidator()

        schemas = validator.get_supported_schemas()

        assert "json-schema" in schemas
        assert "jsonschema" in schemas
        assert "json" in schemas

    def test_validate_simple_json_schema(self) -> None:
        """Test validation of simple JSON schema."""
        validator = JSONSchemaValidator()

        schema = {"type": "string"}

        result = validator.validate_schema(schema)

        assert result.is_success
        assert result.unwrap()["valid"] is True

    def test_validate_json_schema_with_properties(self) -> None:
        """Test validation of JSON schema with properties."""
        validator = JSONSchemaValidator()

        schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
            "required": ["name"],
        }

        result = validator.validate_schema(schema)

        assert result.is_success
        assert "name" in result.unwrap()["properties"]
        assert "age" in result.unwrap()["properties"]

    def test_validate_json_schema_invalid_type(self) -> None:
        """Test validation fails for invalid type."""
        validator = JSONSchemaValidator()

        schema = {"type": "invalid_type"}

        result = validator.validate_schema(schema)

        assert result.is_failure
        assert "Invalid type" in result.error

    def test_validate_json_schema_with_array_items(self) -> None:
        """Test validation of JSON schema with array items."""
        validator = JSONSchemaValidator()

        schema = {"type": "array", "items": {"type": "string"}}

        result = validator.validate_schema(schema)

        assert result.is_success

    def test_validate_instance_string(self) -> None:
        """Test instance validation for string."""
        validator = JSONSchemaValidator()

        schema = {"type": "string"}
        instance = "hello"

        result = validator.validate_instance(instance, schema)

        assert result.is_success

    def test_validate_instance_type_mismatch(self) -> None:
        """Test instance validation fails for type mismatch."""
        validator = JSONSchemaValidator()

        schema = {"type": "string"}
        instance = 123

        result = validator.validate_instance(instance, schema)

        assert result.is_failure
        assert "Expected type string" in result.error

    def test_validate_instance_missing_required(self) -> None:
        """Test instance validation fails for missing required property."""
        validator = JSONSchemaValidator()

        schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"],
        }
        instance = {}

        result = validator.validate_instance(instance, schema)

        assert result.is_failure
        assert "Missing required property: name" in result.error

    def test_validate_instance_object_with_properties(self) -> None:
        """Test instance validation for object with properties."""
        validator = JSONSchemaValidator()

        schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
            "required": ["name"],
        }
        instance = {"name": "John", "age": 30}

        result = validator.validate_instance(instance, schema)

        assert result.is_success

    def test_validate_instance_array(self) -> None:
        """Test instance validation for array."""
        validator = JSONSchemaValidator()

        schema = {"type": "array", "items": {"type": "string"}}
        instance = ["hello", "world"]

        result = validator.validate_instance(instance, schema)

        assert result.is_success


class TestAsyncAPISchemaValidator:
    """Simple test suite for AsyncAPISchemaValidator."""

    def test_validator_initialization(self) -> None:
        """Test AsyncAPI validator initialization."""
        validator = AsyncAPISchemaValidator(
            strict_mode=True,
            validate_messages=True,
            validate_bindings=True,
        )

        assert validator is not None
        assert validator.name == "asyncapi"
        assert validator._strict_mode is True
        assert validator._validate_messages is True
        assert validator._validate_bindings is True

    def test_validator_supports_schema(self) -> None:
        """Test schema type support checking."""
        validator = AsyncAPISchemaValidator()

        assert validator.supports_schema("asyncapi") is True
        assert validator.supports_schema("async-api") is True
        assert validator.supports_schema("asyncapi2") is True
        assert validator.supports_schema("asyncapi3") is True
        assert validator.supports_schema("openapi") is False

    def test_validator_get_supported_schemas(self) -> None:
        """Test getting list of supported schemas."""
        validator = AsyncAPISchemaValidator()

        schemas = validator.get_supported_schemas()

        assert "asyncapi" in schemas
        assert "async-api" in schemas
        assert "asyncapi2" in schemas
        assert "asyncapi3" in schemas

    def test_validate_minimalapi_v2_schema(self) -> None:
        """Test validation of minimal AsyncAPI 2.x schema."""
        validator = AsyncAPISchemaValidator()

        schema = {
            "asyncapi": "2.6.0",
            "info": {"title": "Test API", "version": "1.0.0"},
            "channels": {},
        }

        result = validator.validate_schema(schema)

        assert result.is_success
        assert result.unwrap()["valid"] is True
        assert result.unwrap()["version"] == "2.6.0"

    def test_validate_minimalapi_v3_schema(self) -> None:
        """Test validation of minimal AsyncAPI 3.x schema."""
        validator = AsyncAPISchemaValidator()

        schema = {
            "asyncapi": "3.0.0",
            "info": {"title": "Test API", "version": "1.0.0"},
            "channels": {},
        }

        result = validator.validate_schema(schema)

        assert result.is_success
        assert result.unwrap()["version"] == "3.0.0"

    def test_validateapi_missing_version(self) -> None:
        """Test validation fails for missing asyncapi version."""
        validator = AsyncAPISchemaValidator()

        schema = {
            "info": {"title": "Test API", "version": "1.0.0"},
            "channels": {},
        }

        result = validator.validate_schema(schema)

        assert result.is_failure
        assert "Missing 'asyncapi' version field" in result.error

    def test_validateapi_unsupported_version(self) -> None:
        """Test validation fails for unsupported version."""
        validator = AsyncAPISchemaValidator()

        schema = {
            "asyncapi": "1.0.0",
            "info": {"title": "Test API", "version": "1.0.0"},
            "channels": {},
        }

        result = validator.validate_schema(schema)

        assert result.is_failure
        assert "Unsupported AsyncAPI version" in result.error

    def test_validateapi_with_channels(self) -> None:
        """Test validation of AsyncAPI with channels."""
        validator = AsyncAPISchemaValidator()

        schema = {
            "asyncapi": "2.6.0",
            "info": {"title": "Test API", "version": "1.0.0"},
            "channels": {
                "user/signup": {
                    "subscribe": {
                        "message": {
                            "payload": {
                                "type": "object",
                                "properties": {"userId": {"type": "string"}},
                            }
                        }
                    }
                }
            },
        }

        result = validator.validate_schema(schema)

        assert result.is_success
        assert "user/signup" in result.unwrap()["channels"]

    def test_validateapi_with_servers(self) -> None:
        """Test validation of AsyncAPI with servers."""
        validator = AsyncAPISchemaValidator()

        schema = {
            "asyncapi": "2.6.0",
            "info": {"title": "Test API", "version": "1.0.0"},
            "channels": {},
            "servers": {
                "production": {
                    "url": "wss://example.com",
                    "protocol": "wss",
                    "description": "Production server",
                }
            },
        }

        result = validator.validate_schema(schema)

        assert result.is_success

    def test_validateapi_server_missing_protocol(self) -> None:
        """Test validation fails for server missing protocol."""
        validator = AsyncAPISchemaValidator()

        schema = {
            "asyncapi": "2.6.0",
            "info": {"title": "Test API", "version": "1.0.0"},
            "channels": {},
            "servers": {"production": {"url": "wss://example.com"}},
        }

        result = validator.validate_schema(schema)

        assert result.is_failure
        assert "missing 'protocol'" in result.error
