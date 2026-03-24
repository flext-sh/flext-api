"""Shared schema validation utilities for OpenAPI and AsyncAPI validators.

Eliminates duplication between OpenAPI and AsyncAPI validators.
Implements DRY principle with Single Responsibility Pattern.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, MutableMapping, Sequence
from pathlib import Path
from typing import TypeIs

import yaml
from flext_core import r
from pydantic import TypeAdapter, ValidationError

from flext_api import FlextApiModels, t, u

_JSON_OBJECT_ADAPTER: TypeAdapter[t.ContainerValue] = TypeAdapter(t.ContainerValue)
_CONTAINER_VALUE_ADAPTER: TypeAdapter[t.ContainerValue] = TypeAdapter(t.ContainerValue)


class FlextApiSchemaShared:
    """Facade for shared schema validation utilities.

    Single namespace class providing all shared schema operations
    used by OpenAPI and AsyncAPI validators.
    """

    @staticmethod
    def is_container_value(value: t.ContainerValue) -> TypeIs[t.ContainerValue]:
        """Type guard to check if value is a valid container value.

        Args:
            value: Value to check

        Returns:
            True if value is a valid container value

        """
        return isinstance(value, (str, int, float, bool, type(None), list, Mapping))

    @staticmethod
    def is_object_mapping(
        value: t.ContainerValue,
    ) -> TypeIs[Mapping[str, t.ContainerValue]]:
        """Type guard to check if value is a mapping of container values.

        Args:
            value: Value to check

        Returns:
            True if value is a mapping

        """
        return isinstance(value, Mapping)

    @staticmethod
    def load_schema_document(schema_source: str) -> r[t.ContainerValue]:
        """Load OpenAPI/AsyncAPI schema from file source.

        Supports both JSON and YAML formats.

        Args:
            schema_source: Path to schema file

        Returns:
            r containing loaded schema or error message

        """
        schema_path = Path(schema_source)
        if not schema_path.exists() or not schema_path.is_file():
            return r[t.ContainerValue].fail(f"Schema file not found: {schema_source}")
        suffix = schema_path.suffix.lower()
        try:
            with schema_path.open("r", encoding="utf-8") as schema_file:
                if suffix in {".yaml", ".yml"}:
                    parsed_yaml = u.try_(lambda: yaml.safe_load(schema_file)).map_error(
                        lambda e: f"Failed to parse YAML schema: {e}",
                    )
                    return parsed_yaml.map(
                        lambda value: _CONTAINER_VALUE_ADAPTER.validate_python(value),
                    )
                return u.try_(
                    lambda: _CONTAINER_VALUE_ADAPTER.validate_json(schema_file.read()),
                    catch=ValidationError,
                ).map_error(lambda e: f"Failed to parse JSON schema: {e}")
        except OSError as e:
            return r[t.ContainerValue].fail(f"Failed to read schema file: {e}")

    @staticmethod
    def normalize_json_object(
        value: Mapping[str, t.ContainerValue],
    ) -> t.JsonObject:
        """Normalize a mapping to a JSON t.NormalizedValue.

        Recursively converts values to valid JSON types.

        Args:
            value: Mapping to normalize

        Returns:
            Normalized JSON t.NormalizedValue

        """
        normalized: MutableMapping[str, t.ContainerValue] = {}
        for key, item in value.items():
            if FlextApiSchemaShared.is_container_value(item):
                normalized_value = FlextApiSchemaShared.to_general_value(item)
            else:
                normalized_value = str(item)
            normalized[str(key)] = normalized_value
        return normalized

    @staticmethod
    def to_general_value(value: t.ContainerValue) -> t.ContainerValue:
        """Convert value to a general container value type.

        Recursively processes nested structures.

        Args:
            value: Value to convert

        Returns:
            Converted value as a general container type

        """
        if isinstance(value, list):
            normalized_values: Sequence[t.ContainerValue] = [
                FlextApiSchemaShared.to_general_value(item) for item in value
            ]
            return normalized_values
        if isinstance(value, Mapping):
            normalized_mapping: MutableMapping[str, t.ContainerValue] = {}
            for key, item in value.items():
                normalized_mapping[str(key)] = FlextApiSchemaShared.to_general_value(
                    item,
                )
            return normalized_mapping
        if u.is_primitive(value):
            return value
        return str(value)

    @staticmethod
    def parse_dict_field(
        value: t.ApiJsonValue,
        field_name: str,
    ) -> r[Mapping[str, t.ContainerValue]]:
        """Parse and validate a dictionary field.

        Args:
            value: Value to parse as dictionary
            field_name: Name of field (for error messages)

        Returns:
            r containing parsed dictionary or error message

        """
        try:
            if not isinstance(value, Mapping):
                return r[t.ContainerValueMapping].fail(
                    f"'{field_name}' field must be a dictionary",
                )
            parsed = FlextApiModels.Api.DictField(value=dict(value))
        except ValidationError:
            return r[t.ContainerValueMapping].fail(
                f"'{field_name}' field must be a dictionary",
            )
        return r[t.ContainerValueMapping].ok(parsed.value)

    @staticmethod
    def parse_string_field(value: t.ApiJsonValue, field_name: str) -> r[str]:
        """Parse and validate a string field.

        Args:
            value: Value to parse as string
            field_name: Name of field (for error messages)

        Returns:
            r containing parsed string or error message

        """
        try:
            if not isinstance(value, str):
                return r[str].fail(f"'{field_name}' field must be a string")
            parsed = FlextApiModels.Api.StringField(value=value)
        except ValidationError:
            return r[str].fail(f"'{field_name}' field must be a string")
        return r[str].ok(parsed.value)

    @staticmethod
    def parse_int_field(value: t.ApiJsonValue, field_name: str) -> r[int]:
        """Parse and validate an integer field.

        Args:
            value: Value to parse as integer
            field_name: Name of field (for error messages)

        Returns:
            r containing parsed integer or error message

        """
        try:
            if not isinstance(value, int):
                return r[int].fail(f"'{field_name}' field must be an integer")
            parsed = FlextApiModels.Api.IntField(value=value)
        except ValidationError:
            return r[int].fail(f"'{field_name}' field must be an integer")
        return r[int].ok(parsed.value)

    @staticmethod
    def load_and_validate_schema_document[TValidation](
        schema_source: str,
        *,
        schema_label: str,
        validate_schema: Callable[[t.JsonObject], r[TValidation]],
    ) -> r[t.ContainerValue]:
        """Load and validate a schema document.

        Args:
            schema_source: Path to schema file
            schema_label: Label for error messages
            validate_schema: Callable to validate the normalized schema

        Returns:
            r containing the normalized schema or error message

        """
        schema_result = FlextApiSchemaShared.load_schema_document(schema_source)
        if schema_result.is_failure:
            return r[t.ContainerValue].fail(
                schema_result.error or f"Failed to load {schema_label} schema",
            )
        loaded_schema = schema_result.value
        if not FlextApiSchemaShared.is_object_mapping(loaded_schema):
            return r[t.ContainerValue].fail(
                f"{schema_label} schema must be a JSON/YAML t.NormalizedValue",
            )
        normalized_schema = FlextApiSchemaShared.normalize_json_object(loaded_schema)
        validation_result = validate_schema(normalized_schema)
        if validation_result.is_failure:
            return r[t.ContainerValue].fail(
                f"Invalid {schema_label} schema: {validation_result.error}",
            )
        normalized_result: t.ContainerValue = normalized_schema
        return r[t.ContainerValue].ok(normalized_result)


# Module-level aliases for pyrefly compatibility (callers do `_shared.parse_dict_field(...)`)
is_container_value = FlextApiSchemaShared.is_container_value
is_object_mapping = FlextApiSchemaShared.is_object_mapping
load_schema_document = FlextApiSchemaShared.load_schema_document
normalize_json_object = FlextApiSchemaShared.normalize_json_object
to_general_value = FlextApiSchemaShared.to_general_value
parse_dict_field = FlextApiSchemaShared.parse_dict_field
parse_string_field = FlextApiSchemaShared.parse_string_field
parse_int_field = FlextApiSchemaShared.parse_int_field
load_and_validate_schema_document = (
    FlextApiSchemaShared.load_and_validate_schema_document
)

__all__ = [
    "FlextApiSchemaShared",
    "is_container_value",
    "is_object_mapping",
    "load_and_validate_schema_document",
    "load_schema_document",
    "normalize_json_object",
    "parse_dict_field",
    "parse_int_field",
    "parse_string_field",
    "to_general_value",
]
