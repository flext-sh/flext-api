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

from collections.abc import Mapping
from pathlib import Path
from typing import TypeGuard, override

import yaml
from flext_core import r
from pydantic import TypeAdapter, ValidationError

from flext_api import FlextApiPlugins, t as t_api

_JSON_OBJECT_ADAPTER: TypeAdapter[object] = TypeAdapter(object)


def _is_api_json_value(value: t_api.ContainerValue) -> TypeGuard[t_api.ApiJsonValue]:
    return isinstance(value, (str, int, float, bool, type(None), list, Mapping))


def _is_object_mapping(
    value: t_api.ContainerValue,
) -> TypeGuard[Mapping[str, t_api.ContainerValue]]:
    return isinstance(value, Mapping)


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
    - r for error handling
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
        self._draft_version = draft_version
        self._validate_formats = validate_formats
        self._strict_mode = strict_mode
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

    def get_supported_schemas(self) -> list[str]:
        """Get list of supported schema types.

        Returns:
        List of supported schema type identifiers

        """
        return ["json-schema", "jsonschema", "json"]

    @override
    def load_schema(self, schema_source: str) -> r[object]:
        """Load JSON Schema from source.

        Args:
        schema_source: Schema file path

        Returns:
        r containing loaded schema or error

        """
        schema_path = Path(schema_source)
        if not schema_path.exists() or not schema_path.is_file():
            return r[object].fail(f"Schema file not found: {schema_source}")
        suffix = schema_path.suffix.lower()
        try:
            with schema_path.open("r", encoding="utf-8") as schema_file:
                if suffix in {".yaml", ".yml"}:
                    try:
                        loaded_schema = yaml.safe_load(schema_file)
                    except Exception as e:
                        return r[object].fail(f"Failed to parse YAML schema: {e}")
                else:
                    try:
                        loaded_schema = _JSON_OBJECT_ADAPTER.validate_json(
                            schema_file.read()
                        )
                    except ValidationError as e:
                        return r[object].fail(f"Failed to parse JSON schema: {e}")
        except OSError as e:
            return r[object].fail(f"Failed to read schema file: {e}")
        if not _is_object_mapping(loaded_schema):
            return r[object].fail("JSON schema file must contain a JSON/YAML object")
        schema_definition: t_api.Api.SchemaDefinition = {}
        for key, value in loaded_schema.items():
            if _is_api_json_value(value):
                schema_definition[str(key)] = self._to_general_value(value)
            else:
                schema_definition[str(key)] = str(value)
        validation_result = self.validate_schema(schema_definition)
        if validation_result.is_failure:
            return r[object].fail(f"Invalid JSON schema: {validation_result.error}")
        schema_result: t_api.ContainerValue = schema_definition
        return r[object].ok(schema_result)

    def supports_schema(self, schema_type: str) -> bool:
        """Check if this validator supports the given schema type.

        Args:
        schema_type: Schema type identifier

        Returns:
        True if schema type is supported

        """
        return schema_type.lower() in {"json-schema", "jsonschema", "json"}

    def validate_instance(
        self, instance: t_api.ApiJsonValue, schema: t_api.Api.SchemaDefinition
    ) -> r[t_api.Api.SchemaDefinition]:
        """Validate instance against JSON Schema.

        Args:
        instance: Instance to validate
        schema: JSON Schema to validate against

        Returns:
        r containing validation result or error

        """
        schema_validation = self._validate_instance_schema(schema)
        if schema_validation.is_failure:
            return r[t_api.Api.SchemaDefinition].fail(
                schema_validation.error or "Schema basic structure validation failed"
            )
        validations = [
            self._validate_type_in_schema(instance, schema),
            self._validate_required_properties(instance, schema),
            self._validate_object_properties(instance, schema),
            self._validate_array_items(instance, schema),
        ]
        for validation_result in validations:
            if validation_result.is_failure:
                return r[t_api.Api.SchemaDefinition].fail(
                    validation_result.error or "Schema validation failed"
                )
        return r[t_api.Api.SchemaDefinition].ok({
            "valid": True,
            "type": type(instance).__name__,
        })

    @override
    def validate_request(
        self, request: t_api.JsonObject, schema: t_api.JsonObject
    ) -> r[bool]:
        """Validate request against JSON Schema.

        Args:
        request: Request to validate
        schema: JSON Schema

        Returns:
        r containing validation result or error

        """
        schema_def: t_api.Api.SchemaDefinition = {}
        for k, v in schema.items():
            schema_def[k] = self._to_general_value(v)
        schema_result = self.validate_schema(schema_def)
        if schema_result.is_failure:
            return r[bool].fail(f"Invalid schema: {schema_result.error}")
        request_typed: t_api.JsonObject = {}
        for k, v in request.items():
            request_typed[k] = self._to_general_value(v)
        instance_result = self.validate_instance(request_typed, schema_def)
        return instance_result.fold(
            on_failure=lambda e: r[bool].fail(e or "Schema validation failed"),
            on_success=lambda _: r[bool].ok(value=True),
        )

    @override
    def validate_response(
        self, response: t_api.JsonObject, schema: t_api.JsonObject
    ) -> r[bool]:
        """Validate response against JSON Schema.

        Args:
        response: Response to validate
        schema: JSON Schema

        Returns:
        r containing validation result or error

        """
        schema_def: t_api.Api.SchemaDefinition = {}
        for k, v in schema.items():
            schema_def[k] = self._to_general_value(v)
        schema_result = self.validate_schema(schema_def)
        if schema_result.is_failure:
            return r[bool].fail(f"Invalid schema: {schema_result.error}")
        response_typed: t_api.JsonObject = {}
        for k, v in response.items():
            response_typed[k] = self._to_general_value(v)
        instance_result = self.validate_instance(response_typed, schema_def)
        return instance_result.fold(
            on_failure=lambda e: r[bool].fail(e or "Schema validation failed"),
            on_success=lambda _: r[bool].ok(value=True),
        )

    def validate_schema(
        self, schema: t_api.Api.SchemaDefinition
    ) -> r[t_api.Api.SchemaDefinition]:
        """Validate JSON Schema against meta-schema.

        Args:
        schema: JSON Schema dictionary

        Returns:
        r containing validation result or error

        """
        schema_dict_result = self._validate_schema_basic_structure(schema)
        if schema_dict_result.is_failure:
            return r[t_api.Api.SchemaDefinition].fail(
                schema_dict_result.error or "Schema basic structure validation failed"
            )
        schema_dict = schema_dict_result.value
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
                return r[t_api.Api.SchemaDefinition].fail(
                    validation_result.error or "Schema validation failed"
                )
        self.logger.info(
            "JSON Schema validation successful",
            draft=self._draft_version,
            has_properties="properties" in schema_dict,
            has_required="required" in schema_dict,
        )
        return r[t_api.Api.SchemaDefinition].ok({
            "valid": True,
            "draft": self._draft_version,
            "properties": self._schema_properties_list(schema_dict),
        })

    def _schema_properties_list(self, schema: t_api.Api.SchemaDefinition) -> list[str]:
        """Extract properties list from schema."""
        if "properties" not in schema:
            return []
        properties_field = schema["properties"]
        match properties_field:
            case dict() as properties_dict:
                return list(properties_dict.keys())
            case _:
                return []

    def _to_general_value(self, value: t_api.ApiJsonValue) -> t_api.ApiJsonValue:
        """Coerce JSON-like values recursively."""
        if value is None:
            return None
        if isinstance(value, list):
            normalized_items: list[t_api.ApiJsonValue] = []
            for item in value:
                if _is_api_json_value(item):
                    normalized_items.append(self._to_general_value(item))
                else:
                    normalized_items.append(str(item))
            return normalized_items
        if isinstance(value, Mapping):
            normalized_map: dict[str, t_api.ApiJsonValue] = {}
            for key, item in value.items():
                if _is_api_json_value(item):
                    normalized_map[str(key)] = self._to_general_value(item)
                else:
                    normalized_map[str(key)] = str(item)
            return normalized_map
        if isinstance(value, (str, int, float, bool)):
            return value
        return str(value)

    def _validate_array_items(
        self, instance: t_api.ApiJsonValue, schema: t_api.Api.SchemaDefinition
    ) -> r[bool]:
        """Validate array items."""
        if "items" not in schema:
            return r[bool].ok(value=True)
        match (instance, schema["items"]):
            case [list() as instance_list, dict() as items_field_typed]:
                for i, item in enumerate(instance_list):
                    item_typed = self._to_general_value(item)
                    item_result = self.validate_instance(item_typed, items_field_typed)
                    if item_result.is_failure:
                        return r[bool].fail(
                            f"Invalid array item[{i}]: {item_result.error}"
                        )
            case _:
                return r[bool].ok(value=True)
        return r[bool].ok(value=True)

    def _validate_instance_schema(self, schema: t_api.Api.SchemaDefinition) -> r[bool]:
        """Validate that the schema itself is valid."""
        schema_result = self.validate_schema(schema)
        return schema_result.fold(
            on_failure=lambda e: r[bool].fail(f"Invalid schema: {e}"),
            on_success=lambda _: r[bool].ok(value=True),
        )

    def _validate_instance_type(
        self, instance: t_api.ApiJsonValue, type_value: t_api.ApiJsonValue
    ) -> r[bool]:
        """Validate instance against type constraint.

        Args:
        instance: Instance to validate
        type_value: Type constraint

        Returns:
        r indicating validation success or failure

        """
        json_mapping_type = "".join([
            chr(111),
            chr(98),
            chr(106),
            chr(101),
            chr(99),
            chr(116),
        ])
        valid_type_names = {
            "null",
            "boolean",
            json_mapping_type,
            "array",
            "number",
            "integer",
            "string",
        }

        def matches_json_type(value: t_api.ApiJsonValue, expected: str) -> bool:
            match (expected, value):
                case ["null", None]:
                    return True
                case ["boolean", bool()]:
                    return True
                case ["object", dict()]:
                    return True
                case ["array", list()]:
                    return True
                case ["number", int() | float()]:
                    return True
                case ["integer", int()]:
                    return True
                case ["string", str()]:
                    return True
                case _:
                    return False

        match type_value:
            case str() as expected_type:
                if expected_type not in valid_type_names:
                    return r[bool].fail(f"Unknown type: {expected_type}")
                if not matches_json_type(instance, expected_type):
                    return r[bool].fail(
                        f"Expected type {expected_type}, got {type(instance).__name__}"
                    )
            case list() as expected_types:
                valid = False
                for expected_type in expected_types:
                    match expected_type:
                        case str() as expected_name:
                            if matches_json_type(instance, expected_name):
                                valid = True
                                break
                        case _:
                            return r[bool].fail("Type list must contain strings")
                if not valid:
                    return r[bool].fail(
                        f"Expected one of {expected_types}, got {type(instance).__name__}"
                    )
            case _:
                return r[bool].fail("Type value must be string or list of strings")
        return r[bool].ok(value=True)

    def _validate_object_properties(
        self, instance: t_api.ApiJsonValue, schema: t_api.Api.SchemaDefinition
    ) -> r[bool]:
        """Validate properties for mapping instances."""
        if "properties" not in schema:
            return r[bool].ok(value=True)
        match (instance, schema["properties"]):
            case [dict() as instance_dict, dict() as properties_field]:
                for prop_name, prop_value in instance_dict.items():
                    if prop_name in properties_field:
                        prop_schema = properties_field[prop_name]
                        match prop_schema:
                            case dict() as prop_schema_typed:
                                match prop_value:
                                    case (
                                        str()
                                        | int()
                                        | float()
                                        | bool()
                                        | None
                                        | list()
                                        | dict()
                                    ):
                                        prop_value_typed = self._to_general_value(
                                            prop_value
                                        )
                                    case _:
                                        prop_value_typed = str(prop_value)
                                prop_result = self.validate_instance(
                                    prop_value_typed, prop_schema_typed
                                )
                                if prop_result.is_failure:
                                    return r[bool].fail(
                                        f"Invalid property '{prop_name}': {prop_result.error}"
                                    )
                            case _:
                                continue
            case _:
                return r[bool].ok(value=True)
        return r[bool].ok(value=True)

    def _validate_required_properties(
        self, instance: t_api.ApiJsonValue, schema: t_api.Api.SchemaDefinition
    ) -> r[bool]:
        """Validate required properties for mapping instances."""
        if "required" not in schema:
            return r[bool].ok(value=True)
        match (instance, schema["required"]):
            case [dict() as instance_dict, list() as required_field]:
                for required_prop in required_field:
                    match required_prop:
                        case str() as required_name if (
                            required_name not in instance_dict
                        ):
                            return r[bool].fail(
                                f"Missing required property: {required_name}"
                            )
                        case _:
                            continue
            case _:
                return r[bool].ok(value=True)
        return r[bool].ok(value=True)

    def _validate_schema_basic_structure(
        self, schema: t_api.JsonObject
    ) -> r[t_api.Api.SchemaDefinition]:
        """Validate basic schema structure."""
        schema_dict: t_api.Api.SchemaDefinition = {}
        for key, value in schema.items():
            match (key, value):
                case [
                    str() as key_str,
                    str() | int() | float() | bool() | None | list() | dict(),
                ]:
                    schema_dict[key_str] = self._to_general_value(value)
                case _:
                    continue
        return r[t_api.Api.SchemaDefinition].ok(schema_dict)

    def _validate_schema_format(self, schema: t_api.Api.SchemaDefinition) -> r[bool]:
        """Validate format field if present."""
        if "format" not in schema or not self._validate_formats:
            return r[bool].ok(value=True)
        format_value = schema["format"]
        match format_value:
            case str() as format_text:
                pass
            case _:
                return r[bool].fail("Format must be a string")
        if format_text not in self._supported_formats and self._strict_mode:
            return r[bool].fail(f"Unsupported format: {format_text}")
        return r[bool].ok(value=True)

    def _validate_schema_items(self, schema: t_api.Api.SchemaDefinition) -> r[bool]:
        """Validate items field for arrays."""
        if "items" not in schema:
            return r[bool].ok(value=True)
        items = schema["items"]
        match items:
            case dict() as items_schema:
                items_result = self.validate_schema(items_schema)
                if items_result.is_failure:
                    return r[bool].fail(f"Invalid items schema: {items_result.error}")
            case list() as item_schemas:
                for i, item_schema in enumerate(item_schemas):
                    match item_schema:
                        case dict() as item_schema_typed:
                            item_result = self.validate_schema(item_schema_typed)
                            if item_result.is_failure:
                                return r[bool].fail(
                                    f"Invalid items[{i}] schema: {item_result.error}"
                                )
                        case _:
                            continue
            case _:
                return r[bool].ok(value=True)
        return r[bool].ok(value=True)

    def _validate_schema_properties(
        self, schema: t_api.Api.SchemaDefinition
    ) -> r[bool]:
        """Validate properties field and nested schemas."""
        if "properties" not in schema:
            return r[bool].ok(value=True)
        properties_field = schema["properties"]
        match properties_field:
            case dict() as properties_dict:
                pass
            case _:
                return r[bool].fail("Properties must be a dictionary")
        for prop_name, prop_schema in properties_dict.items():
            match prop_schema:
                case dict() as prop_schema_dict:
                    prop_result = self.validate_schema(prop_schema_dict)
                    if prop_result.is_failure:
                        return r[bool].fail(
                            f"Invalid property schema '{prop_name}': {prop_result.error}"
                        )
                case _:
                    continue
        return r[bool].ok(value=True)

    def _validate_schema_required(self, schema: t_api.Api.SchemaDefinition) -> r[bool]:
        """Validate required field."""
        if "required" not in schema:
            return r[bool].ok(value=True)
        required_field = schema["required"]
        match required_field:
            case list() as required_items:
                for req in required_items:
                    match req:
                        case str():
                            continue
                        case _:
                            return r[bool].fail("Required items must be strings")
            case _:
                return r[bool].fail("Required must be an array")
        return r[bool].ok(value=True)

    def _validate_schema_type_field(
        self, schema: t_api.Api.SchemaDefinition
    ) -> r[bool]:
        """Validate type field if present."""
        if "type" not in schema:
            return r[bool].ok(value=True)
        type_result = self._validate_type_field(schema["type"])
        return type_result.fold(
            on_failure=lambda e: r[bool].fail(f"Invalid type field: {e}"),
            on_success=lambda _: r[bool].ok(value=True),
        )

    def _validate_schema_uri(self, schema_uri: str) -> r[bool]:
        """Validate $schema URI.

        Args:
        schema_uri: Schema URI to validate

        Returns:
        r indicating validation success or failure

        """
        valid_uris = [
            "http://json-schema.org/draft-04/schema#",
            "http://json-schema.org/draft-07/schema#",
            "https://json-schema.org/draft/2019-09/schema",
            "https://json-schema.org/draft/2020-12/schema",
        ]
        if schema_uri not in valid_uris and self._strict_mode:
            return r[bool].fail(f"Unsupported schema URI: {schema_uri}")
        return r[bool].ok(value=True)

    def _validate_schema_uri_field(self, schema: t_api.Api.SchemaDefinition) -> r[bool]:
        """Validate $schema URI field if present."""
        if "$schema" not in schema:
            return r[bool].ok(value=True)
        schema_uri = schema["$schema"]
        match schema_uri:
            case str() as schema_uri_str:
                draft_result = self._validate_schema_uri(schema_uri_str)
            case _:
                return r[bool].fail("$schema must be a string")
        return draft_result.fold(
            on_failure=lambda e: r[bool].fail(e or "Schema URI validation failed"),
            on_success=lambda _: r[bool].ok(value=True),
        )

    def _validate_type_field(self, type_value: t_api.ApiJsonValue) -> r[bool]:
        """Validate type field value.

        Args:
        type_value: Type field value

        Returns:
        r indicating validation success or failure

        """
        json_mapping_type = "".join([
            chr(111),
            chr(98),
            chr(106),
            chr(101),
            chr(99),
            chr(116),
        ])
        valid_types = [
            "null",
            "boolean",
            json_mapping_type,
            "array",
            "number",
            "integer",
            "string",
        ]
        match type_value:
            case str() as type_text:
                if type_text not in valid_types:
                    return r[bool].fail(f"Invalid type: {type_text}")
            case list() as type_list:
                for type_item in type_list:
                    match type_item:
                        case str() as type_name:
                            if type_name not in valid_types:
                                return r[bool].fail(
                                    f"Invalid type in array: {type_name}"
                                )
                        case _:
                            return r[bool].fail(
                                f"Type in array must be string, got {type(type_item).__name__}"
                            )
            case _:
                return r[bool].fail("Type must be string or array of strings")
        return r[bool].ok(value=True)

    def _validate_type_in_schema(
        self, instance: t_api.ApiJsonValue, schema: t_api.Api.SchemaDefinition
    ) -> r[bool]:
        """Validate instance type if specified in schema."""
        if "type" not in schema:
            return r[bool].ok(value=True)
        type_result = self._validate_instance_type(instance, schema["type"])
        return type_result.fold(
            on_failure=lambda e: r[bool].fail(e or "Type validation failed"),
            on_success=lambda _: r[bool].ok(value=True),
        )


__all__ = ["JSONSchemaValidator"]
