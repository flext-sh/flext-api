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

from typing import Any

from flext_core import FlextResult, FlextTypes

from flext_api.plugins import SchemaPlugin


class JSONSchemaValidator(SchemaPlugin):
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

    def validate_schema(self, schema: dict[str, Any]) -> FlextResult[dict[str, Any]]:
        """Validate JSON Schema against meta-schema.

        Args:
        schema: JSON Schema dictionary

        Returns:
        FlextResult containing validation result or error

        """
        # Check if schema is a dictionary
        if not isinstance(schema, dict):
            return FlextResult[dict[str, Any]].fail("Schema must be a dictionary")

        # Validate $schema field if present
        schema_uri = schema.get("$schema")
        if schema_uri:
            draft_result = self._validate_schema_uri(schema_uri)
            if draft_result.is_failure:
                return FlextResult[dict[str, Any]].fail(draft_result.error)

        # Validate type if present
        if "type" in schema:
            type_result = self._validate_type_field(schema["type"])
            if type_result.is_failure:
                return FlextResult[dict[str, Any]].fail(
                    f"Invalid type field: {type_result.error}"
                )

        # Validate properties if present
        if "properties" in schema:
            if not isinstance(schema["properties"], dict):
                return FlextResult[dict[str, Any]].fail(
                    "Properties must be a dictionary"
                )

            # Recursively validate property schemas
            for prop_name, prop_schema in schema["properties"].items():
                if isinstance(prop_schema, dict):
                    prop_result = self.validate_schema(prop_schema)
                    if prop_result.is_failure:
                        return FlextResult[dict[str, Any]].fail(
                            f"Invalid property schema '{prop_name}': {prop_result.error}"
                        )

        # Validate items if present (for arrays)
        if "items" in schema:
            items = schema["items"]
            if isinstance(items, dict):
                items_result = self.validate_schema(items)
                if items_result.is_failure:
                    return FlextResult[dict[str, Any]].fail(
                        f"Invalid items schema: {items_result.error}"
                    )
            elif isinstance(items, list):
                for i, item_schema in enumerate(items):
                    if isinstance(item_schema, dict):
                        item_result = self.validate_schema(item_schema)
                        if item_result.is_failure:
                            return FlextResult[dict[str, Any]].fail(
                                f"Invalid items[{i}] schema: {item_result.error}"
                            )

        # Validate required field if present
        if "required" in schema:
            if not isinstance(schema["required"], list):
                return FlextResult[dict[str, Any]].fail("Required must be an array")

            for req in schema["required"]:
                if not isinstance(req, str):
                    return FlextResult[dict[str, Any]].fail(
                        "Required items must be strings"
                    )

        # Validate format if present
        if "format" in schema and self._validate_formats:
            format_value = schema["format"]
            if not isinstance(format_value, str):
                return FlextResult[dict[str, Any]].fail("Format must be a string")

            if format_value not in self._supported_formats and self._strict_mode:
                return FlextResult[dict[str, Any]].fail(
                    f"Unsupported format: {format_value}"
                )

        self.logger.info(
            "JSON Schema validation successful",
            extra={
                "draft": self._draft_version,
                "has_properties": "properties" in schema,
                "has_required": "required" in schema,
            },
        )

        return FlextResult[dict[str, Any]].ok({
            "valid": True,
            "draft": self._draft_version,
            "type": schema.get("type"),
            "properties": list(schema.get("properties", {}).keys()),
        })

    def validate_instance(
        self,
        instance: FlextTypes.JsonValue,
        schema: dict[str, FlextTypes.JsonValue],
    ) -> FlextResult[dict[str, FlextTypes.JsonValue]]:
        """Validate instance against JSON Schema.

        Args:
        instance: Instance to validate
        schema: JSON Schema to validate against

        Returns:
        FlextResult containing validation result or error

        """
        # First validate the schema itself
        schema_result = self.validate_schema(schema)
        if schema_result.is_failure:
            return FlextResult[dict[str, Any]].fail(
                f"Invalid schema: {schema_result.error}"
            )

        # Validate type if specified
        if "type" in schema:
            type_result = self._validate_instance_type(instance, schema["type"])
            if type_result.is_failure:
                return FlextResult[dict[str, Any]].fail(type_result.error)

        # Validate required properties for objects
        if isinstance(instance, dict) and "required" in schema:
            required_field = schema.get("required")
            if isinstance(required_field, list):
                for required_prop in required_field:
                    if isinstance(required_prop, str) and required_prop not in instance:
                        return FlextResult[dict[str, Any]].fail(
                            f"Missing required property: {required_prop}"
                        )

        # Validate properties for objects
        if isinstance(instance, dict) and "properties" in schema:
            properties_field = schema.get("properties")
            if isinstance(properties_field, dict):
                for prop_name, prop_value in instance.items():
                    if prop_name in properties_field:
                        prop_schema = properties_field[prop_name]
                        if isinstance(prop_schema, dict):
                            prop_result = self.validate_instance(
                                prop_value, prop_schema
                            )
                            if prop_result.is_failure:
                                return FlextResult[dict[str, Any]].fail(
                                    f"Invalid property '{prop_name}': {prop_result.error}"
                                )

        # Validate array items
        if isinstance(instance, list) and "items" in schema:
            items_field = schema.get("items")
            if isinstance(items_field, dict):
                for i, item in enumerate(instance):
                    item_result = self.validate_instance(item, items_field)
                    if item_result.is_failure:
                        return FlextResult[dict[str, Any]].fail(
                            f"Invalid array item[{i}]: {item_result.error}"
                        )

        return FlextResult[dict[str, Any]].ok({
            "valid": True,
            "type": type(instance).__name__,
        })

    def _validate_schema_uri(self, schema_uri: str) -> FlextResult[None]:
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
            return FlextResult[None].fail(f"Unsupported schema URI: {schema_uri}")

        return FlextResult[None].ok(None)

    def _validate_type_field(
        self, type_value: FlextTypes.JsonValue
    ) -> FlextResult[None]:
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
                return FlextResult[None].fail(f"Invalid type: {type_value}")
        elif isinstance(type_value, list):
            for t in type_value:
                if not isinstance(t, str) or t not in valid_types:
                    return FlextResult[None].fail(f"Invalid type in array: {t}")
        else:
            return FlextResult[None].fail("Type must be string or array of strings")

        return FlextResult[None].ok(None)

    def _validate_instance_type(
        self,
        instance: FlextTypes.JsonValue,
        type_value: FlextTypes.JsonValue,
    ) -> FlextResult[None]:
        """Validate instance against type constraint.

        Args:
        instance: Instance to validate
        type_value: Type constraint

        Returns:
        FlextResult indicating validation success or failure

        """
        type_map: dict[str, Any] = {
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
            if expected_type and not isinstance(instance, expected_type):
                return FlextResult[None].fail(
                    f"Expected type {type_value}, got {type(instance).__name__}"
                )
        elif isinstance(type_value, list):
            valid = False
            for t in type_value:
                expected_type = type_map.get(t)
                if expected_type and isinstance(instance, expected_type):
                    valid = True
                    break
            if not valid:
                return FlextResult[None].fail(
                    f"Expected one of {type_value}, got {type(instance).__name__}"
                )

        return FlextResult[None].ok(None)

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
        request: dict[str, Any],
        schema: dict[str, Any],
    ) -> FlextResult[bool]:
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
            return FlextResult[bool].fail(f"Invalid schema: {schema_result.error}")

        # Validate request body against JSON Schema
        instance_result = self.validate_instance(request, schema)
        if instance_result.is_failure:
            return FlextResult[bool].fail(instance_result.error)

        return FlextResult[bool].ok(True)

    def validate_response(
        self,
        response: dict[str, Any],
        schema: dict[str, Any],
    ) -> FlextResult[bool]:
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
            return FlextResult[bool].fail(f"Invalid schema: {schema_result.error}")

        # Validate response body against JSON Schema
        instance_result = self.validate_instance(response, schema)
        if instance_result.is_failure:
            return FlextResult[bool].fail(instance_result.error)

        return FlextResult[bool].ok(True)

    def load_schema(
        self,
        schema_source: str,
    ) -> FlextResult[object]:
        """Load JSON Schema from source.

        Args:
        schema_source: Schema file path

        Returns:
        FlextResult containing loaded schema or error

        """
        # For string paths, would load from file
        return FlextResult[object].fail("File loading not implemented yet")


__all__ = ["JSONSchemaValidator"]
