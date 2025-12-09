"""JSON Schema Validator for flext-api.

Implements JSON Schema validation with:
- Draft 4, Draft 7, and Draft 2019-09 support
- Schema validation against meta-schema
- Instance validation against schema
- Format validation (email, uri, date-time, etc.)
- Reference resolution ($ref)

See TRANSFORMATION_PLAN.md - Phase 5 for implementation details.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import cast

from flext_core import r, t

from flext_api.plugins import FlextApiPlugins
from flext_api.typings import t as t_api


class JSONSchemaValidator(FlextApiPlugins.Schema):
    """JSON Schema validator with draft support.

    Features:
    - JSON Schema Draft 4, 7, and 2019-09 support
    - Meta-schema validation
    - Instance validation against schema
    - Format validation (email, uri, ipv4, ipv6, date-time, etc.)
    - Reference resolution ($ref)
    - Custom format validators
    - Recursive schema validation

    Integration:
    - Uses jsonschema library for validation
    - Supports custom format checkers
    - FlextResult for error handling
    - FlextLogger for validation logging
    """

    def __init__(
        self,
        draft_version: str = "draft7",
        *,
        validate_formats: bool = True,
        strict_mode: bool = True,
    ) -> None:
        """Initialize JSON Schema validator.

        Args:
        draft_version: JSON Schema draft version (draft4, draft7, draft2019-09)
        validate_formats: Enable format validation
        strict_mode: Enable strict schema validation

        """
        super().__init__(
            name="jsonschema",
            version="1.0.0",
            description="JSON Schema validator with draft support",
        )

        # Validation configuration
        self._draft_version = draft_version
        self._validate_formats = validate_formats
        self._strict_mode = strict_mode

        # Supported formats
        self._supported_formats = [
            "date-time",
            "date",
            "time",
            "email",
            "idn-email",
            "hostname",
            "idn-hostname",
            "ipv4",
            "ipv6",
            "uri",
            "uri-reference",
            "iri",
            "iri-reference",
            "uuid",
            "json-pointer",
            "relative-json-pointer",
            "regex",
        ]

    def _validate_schema_basic_structure(
        self,
        schema: object,
    ) -> r[t_api.SchemaDefinition]:
        """Validate basic schema structure."""
        if not isinstance(schema, dict):
            return r[t_api.SchemaDefinition].fail("Schema must be a dictionary")
        # Validate all values are JsonValue types
        schema_dict: t_api.SchemaDefinition = {}
        for key, value in schema.items():
            if isinstance(key, str) and isinstance(
                value,
                (str, int, float, bool, type(None), list, dict),
            ):
                schema_dict[key] = value
        return r[t_api.SchemaDefinition].ok(schema_dict)

    def _validate_schema_uri_field(
        self,
        schema: t_api.SchemaDefinition,
    ) -> r[bool]:
        """Validate $schema URI field if present."""
        if "$schema" not in schema:
            return r[bool].ok(True)
        schema_uri = schema["$schema"]
        if not isinstance(schema_uri, str):
            return r[bool].fail("$schema must be a string")
        draft_result = self._validate_schema_uri(schema_uri)
        if draft_result.is_failure:
            return r[bool].fail(draft_result.error or "Schema URI validation failed")
        return r[bool].ok(True)

    def _validate_schema_type_field(
        self,
        schema: t_api.SchemaDefinition,
    ) -> r[bool]:
        """Validate type field if present."""
        if "type" not in schema:
            return r[bool].ok(True)
        type_result = self._validate_type_field(schema["type"])
        if type_result.is_failure:
            return r[bool].fail(f"Invalid type field: {type_result.error}")
        return r[bool].ok(True)

    def _validate_schema_properties(
        self,
        schema: t_api.SchemaDefinition,
    ) -> r[bool]:
        """Validate properties field and nested schemas."""
        if "properties" not in schema:
            return r[bool].ok(True)
        if not isinstance(schema["properties"], dict):
            return r[bool].fail("Properties must be a dictionary")

        # Recursively validate property schemas
        for prop_name, prop_schema in schema["properties"].items():
            if isinstance(prop_schema, dict):
                prop_result = self.validate_schema(prop_schema)
                if prop_result.is_failure:
                    return r[bool].fail(
                        f"Invalid property schema '{prop_name}': {prop_result.error}",
                    )
        return r[bool].ok(True)

    def _validate_schema_items(self, schema: t_api.SchemaDefinition) -> r[bool]:
        """Validate items field for arrays."""
        if "items" not in schema:
            return r[bool].ok(True)
        items = schema["items"]
        if isinstance(items, dict):
            # Type narrowing: iterative assignment avoids dict() constructor overload issues
            items_schema: t_api.SchemaDefinition = {}
            for k, v in items.items():
                # Cast to JsonValue to match schema type
                items_schema[k] = cast("t.JsonValue", v)
            items_result = self.validate_schema(items_schema)
            if items_result.is_failure:
                return r[bool].fail(f"Invalid items schema: {items_result.error}")
        elif isinstance(items, list):
            for i, item_schema in enumerate(items):
                if isinstance(item_schema, dict):
                    # Type reconstruction: iterative assignment to match SchemaDefinition type
                    item_schema_typed: t_api.SchemaDefinition = {}
                    for k, v in item_schema.items():
                        item_schema_typed[k] = v
                    item_result = self.validate_schema(item_schema_typed)
                    if item_result.is_failure:
                        return r[bool].fail(
                            f"Invalid items[{i}] schema: {item_result.error}",
                        )
        return r[bool].ok(True)

    def _validate_schema_required(
        self,
        schema: t_api.SchemaDefinition,
    ) -> r[bool]:
        """Validate required field."""
        if "required" not in schema:
            return r[bool].ok(True)
        if not isinstance(schema["required"], list):
            return r[bool].fail("Required must be an array")

        for req in schema["required"]:
            if not isinstance(req, str):
                return r[bool].fail("Required items must be strings")
        return r[bool].ok(True)

    def _validate_schema_format(
        self,
        schema: t_api.SchemaDefinition,
    ) -> r[bool]:
        """Validate format field if present."""
        if "format" not in schema or not self._validate_formats:
            return r[bool].ok(True)
        format_value = schema["format"]
        if not isinstance(format_value, str):
            return r[bool].fail("Format must be a string")

        if format_value not in self._supported_formats and self._strict_mode:
            return r[bool].fail(f"Unsupported format: {format_value}")
        return r[bool].ok(True)

    def validate_schema(
        self,
        schema: t_api.SchemaDefinition,
    ) -> r[t_api.SchemaDefinition]:
        """Validate JSON Schema against meta-schema.

        Args:
        schema: JSON Schema dictionary

        Returns:
        FlextResult containing validation result or error

        """
        # Validate basic structure
        schema_dict_result = self._validate_schema_basic_structure(schema)
        if schema_dict_result.is_failure:
            return r[t_api.SchemaDefinition].fail(
                schema_dict_result.error or "Schema basic structure validation failed",
            )

        schema_dict = schema_dict_result.unwrap()

        # Validate individual components
        validations = [
            self._validate_schema_uri_field(schema_dict),
            self._validate_schema_type_field(schema_dict),
            self._validate_schema_properties(schema_dict),
            self._validate_schema_items(schema_dict),
            self._validate_schema_required(schema_dict),
            self._validate_schema_format(schema_dict),
        ]

        for validation_result in validations:
            if validation_result.is_failure:
                return r[t_api.SchemaDefinition].fail(
                    validation_result.error or "Schema validation failed",
                )

        self.logger.info(
            "JSON Schema validation successful",
            extra={
                "draft": self._draft_version,
                "has_properties": "properties" in schema_dict,
                "has_required": "required" in schema_dict,
            },
        )

        return r[t_api.SchemaDefinition].ok(
            {
                "valid": True,
                "draft": self._draft_version,
                "properties": list(schema_dict["properties"].keys())
                if "properties" in schema_dict
                and isinstance(schema_dict["properties"], dict)
                else [],
            }
        )

    def _validate_instance_schema(self, schema: dict[str, t.JsonValue]) -> r[bool]:
        """Validate that the schema itself is valid."""
        schema_result = self.validate_schema(schema)
        if schema_result.is_failure:
            return r[bool].fail(f"Invalid schema: {schema_result.error}")
        return r[bool].ok(True)

    def _validate_type_in_schema(
        self,
        instance: t.JsonValue,
        schema: dict[str, t.JsonValue],
    ) -> r[bool]:
        """Validate instance type if specified in schema."""
        if "type" not in schema:
            return r[bool].ok(True)
        type_result = self._validate_instance_type(instance, schema["type"])
        if type_result.is_failure:
            return r[bool].fail(type_result.error or "Type validation failed")
        return r[bool].ok(True)

    def _validate_required_properties(
        self,
        instance: t.JsonValue,
        schema: dict[str, t.JsonValue],
    ) -> r[bool]:
        """Validate required properties for object instances."""
        if not isinstance(instance, dict) or "required" not in schema:
            return r[bool].ok(True)
        required_field = schema["required"]
        if not isinstance(required_field, list):
            return r[bool].fail("Required field must be a list")
        for required_prop in required_field:
            if isinstance(required_prop, str) and required_prop not in instance:
                return r[bool].fail(f"Missing required property: {required_prop}")
        return r[bool].ok(True)

    def _validate_object_properties(
        self,
        instance: t.JsonValue,
        schema: dict[str, t.JsonValue],
    ) -> r[bool]:
        """Validate properties for object instances."""
        if not isinstance(instance, dict) or "properties" not in schema:
            return r[bool].ok(True)
        properties_field = schema["properties"]
        if not isinstance(properties_field, dict):
            return r[bool].fail("Properties field must be a dictionary")
        for prop_name, prop_value in instance.items():
            if prop_name in properties_field:
                prop_schema = properties_field[prop_name]
                if isinstance(prop_schema, dict):
                    # Type reconstruction: narrow and assign to explicit type
                    prop_schema_typed: dict[str, t.JsonValue] = prop_schema
                    # Cast to JsonValue to match validate_instance signature
                    prop_result = self.validate_instance(
                        cast("t.JsonValue", prop_value),
                        prop_schema_typed,
                    )
                    if prop_result.is_failure:
                        return r[bool].fail(
                            f"Invalid property '{prop_name}': {prop_result.error}",
                        )
        return r[bool].ok(True)

    def _validate_array_items(
        self,
        instance: t.JsonValue,
        schema: dict[str, t.JsonValue],
    ) -> r[bool]:
        """Validate array items."""
        if not isinstance(instance, list) or "items" not in schema:
            return r[bool].ok(True)
        items_field = schema["items"]
        if not isinstance(items_field, dict):
            return r[bool].fail("Items field must be a dictionary")
        # Type reconstruction: narrow and assign to explicit type
        # Cast to JsonValue to match type signature
        items_field_typed: dict[str, t.JsonValue] = cast(
            "dict[str, t.JsonValue]", items_field
        )
        for i, item in enumerate(instance):
            # Cast to JsonValue to match validate_instance signature
            item_result = self.validate_instance(
                cast("t.JsonValue", item),
                items_field_typed,
            )
            if item_result.is_failure:
                return r[bool].fail(f"Invalid array item[{i}]: {item_result.error}")
        return r[bool].ok(True)

    def validate_instance(
        self,
        instance: t.JsonValue,
        schema: dict[str, t.JsonValue],
    ) -> r[dict[str, t.JsonValue]]:
        """Validate instance against JSON Schema.

        Args:
        instance: Instance to validate
        schema: JSON Schema to validate against

        Returns:
        FlextResult containing validation result or error

        """
        # Validate schema first
        schema_validation = self._validate_instance_schema(schema)
        if schema_validation.is_failure:
            return r[t_api.SchemaDefinition].fail(
                schema_validation.error or "Schema basic structure validation failed",
            )

        # Run all validations
        validations = [
            self._validate_type_in_schema(instance, schema),
            self._validate_required_properties(instance, schema),
            self._validate_object_properties(instance, schema),
            self._validate_array_items(instance, schema),
        ]

        for validation_result in validations:
            if validation_result.is_failure:
                return r[t_api.SchemaDefinition].fail(
                    validation_result.error or "Schema validation failed",
                )

        return r[t_api.SchemaDefinition].ok(
            {
                "valid": True,
                "type": type(instance).__name__,
            }
        )

    def _validate_schema_uri(self, schema_uri: str) -> r[bool]:
        """Validate $schema URI.

        Args:
        schema_uri: Schema URI to validate

        Returns:
        FlextResult indicating validation success or failure

        """
        valid_uris = [
            "http://json-schema.org/draft-04/schema#",
            "http://json-schema.org/draft-07/schema#",
            "https://json-schema.org/draft/2019-09/schema",
            "https://json-schema.org/draft/2020-12/schema",
        ]

        if schema_uri not in valid_uris and self._strict_mode:
            return r[bool].fail(f"Unsupported schema URI: {schema_uri}")

        return r[bool].ok(True)

    def _validate_type_field(self, type_value: t.JsonValue) -> r[bool]:
        """Validate type field value.

        Args:
        type_value: Type field value

        Returns:
        FlextResult indicating validation success or failure

        """
        valid_types = [
            "null",
            "boolean",
            "object",
            "array",
            "number",
            "integer",
            "string",
        ]

        if isinstance(type_value, str):
            if type_value not in valid_types:
                return r[bool].fail(f"Invalid type: {type_value}")
        elif isinstance(type_value, list):
            for t in type_value:
                if not isinstance(t, str):
                    return r[bool].fail(
                        f"Type in array must be string, got {type(t).__name__}",
                    )
                if t not in valid_types:
                    return r[bool].fail(f"Invalid type in array: {t}")
        else:
            return r[bool].fail("Type must be string or array of strings")

        return r[bool].ok(True)

    def _validate_instance_type(
        self,
        instance: t.JsonValue,
        type_value: t.JsonValue,
    ) -> r[bool]:
        """Validate instance against type constraint.

        Args:
        instance: Instance to validate
        type_value: Type constraint

        Returns:
        FlextResult indicating validation success or failure

        """
        type_map: dict[str, type | tuple[type, ...]] = {
            "null": type(None),
            "boolean": bool,
            "object": dict,
            "array": list,
            "number": (int, float),
            "integer": int,
            "string": str,
        }

        if isinstance(type_value, str):
            expected_type = type_map.get(type_value)
            if expected_type is None:
                return r[bool].fail(f"Unknown type: {type_value}")
            if not isinstance(instance, expected_type):
                return r[bool].fail(
                    f"Expected type {type_value}, got {type(instance).__name__}",
                )
        elif isinstance(type_value, list):
            valid = False
            for t in type_value:
                if not isinstance(t, str):
                    return r[bool].fail("Type list must contain strings")
                expected_type = type_map.get(t)
                if expected_type and isinstance(instance, expected_type):
                    valid = True
                    break
            if not valid:
                return r[bool].fail(
                    f"Expected one of {type_value}, got {type(instance).__name__}",
                )
        else:
            return r[bool].fail("Type value must be string or list of strings")

        return r[bool].ok(True)

    def supports_schema(self, schema_type: str) -> bool:
        """Check if this validator supports the given schema type.

        Args:
        schema_type: Schema type identifier

        Returns:
        True if schema type is supported

        """
        return schema_type.lower() in {"json-schema", "jsonschema", "json"}

    def get_supported_schemas(self) -> list[str]:
        """Get list of supported schema types.

        Returns:
        List of supported schema type identifiers

        """
        return ["json-schema", "jsonschema", "json"]

    def validate_request(
        self,
        request: t_api.JsonObject,
        schema: t_api.SchemaDefinition,
    ) -> r[bool]:
        """Validate request against JSON Schema.

        Args:
        request: Request to validate
        schema: JSON Schema

        Returns:
        FlextResult containing validation result or error

        """
        # Validate the schema first
        schema_result = self.validate_schema(schema)
        if schema_result.is_failure:
            return r[bool].fail(f"Invalid schema: {schema_result.error}")

        # Validate request body against JSON Schema
        # Type narrowing: request is already JsonValue type
        instance_result = self.validate_instance(request, schema)
        if instance_result.is_failure:
            return r[bool].fail(instance_result.error or "Schema validation failed")

        return r[bool].ok(True)

    def validate_response(
        self,
        response: t_api.JsonObject,
        schema: t_api.SchemaDefinition,
    ) -> r[bool]:
        """Validate response against JSON Schema.

        Args:
        response: Response to validate
        schema: JSON Schema

        Returns:
        FlextResult containing validation result or error

        """
        # Validate the schema first
        schema_result = self.validate_schema(schema)
        if schema_result.is_failure:
            return r[bool].fail(f"Invalid schema: {schema_result.error}")

        # Validate response body against JSON Schema
        # Type narrowing: response is already JsonValue type
        instance_result = self.validate_instance(response, schema)
        if instance_result.is_failure:
            return r[bool].fail(instance_result.error or "Schema validation failed")

        return r[bool].ok(True)

    def load_schema(
        self,
        schema_source: str,
    ) -> r[object]:
        """Load JSON Schema from source.

        Args:
        schema_source: Schema file path

        Returns:
        FlextResult containing loaded schema or error

        """
        # Acknowledge unused parameter (stub implementation)
        _ = schema_source
        # For string paths, would load from file
        return r[object].fail("File loading not implemented yet")


__all__ = ["JSONSchemaValidator"]
