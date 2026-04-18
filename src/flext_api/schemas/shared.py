"""Shared schema validation utilities for OpenAPI and AsyncAPI validators.

Eliminates duplication between OpenAPI and AsyncAPI validators.
Implements DRY principle with Single Responsibility Pattern.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from pathlib import Path
from typing import TypeIs

from flext_api import c, m, p, r, t, u


class FlextApiSchemaShared:
    """Facade for shared schema validation utilities.

    Single namespace class providing all shared schema operations
    used by OpenAPI and AsyncAPI validators.
    """

    @staticmethod
    def container_value(value: t.ContainerValue) -> TypeIs[t.ContainerValue]:
        """Type guard to check if value is a valid container value.

        Args:
            value: Value to check

        Returns:
            True if value is a valid container value

        """
        return isinstance(value, (str, int, float, bool, type(None), list, Mapping))

    @staticmethod
    def object_mapping(
        value: t.ContainerValue,
    ) -> TypeIs[t.ContainerValueMapping]:
        """Type guard to check if value is a mapping of container values.

        Args:
            value: Value to check

        Returns:
            True if value is a mapping

        """
        return isinstance(value, Mapping)

    @staticmethod
    def load_schema_document(schema_source: str) -> p.Result[t.ContainerValue]:
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
            text = schema_path.read_text(encoding="utf-8")
        except OSError as e:
            return r[t.ContainerValue].fail(f"Failed to read schema file: {e}")
        if suffix in {".yaml", ".yml"}:
            parsed_yaml = u.Cli.yaml_parse(text).map_error(
                lambda e: f"Failed to parse YAML schema: {e}",
            )
            return parsed_yaml.map(
                lambda value: t.Api.CONTAINER_VALUE_ADAPTER.validate_python(value),
            )
        return u.try_(
            lambda: t.Api.CONTAINER_VALUE_ADAPTER.validate_json(text),
            catch=c.ValidationError,
        ).map_error(lambda e: f"Failed to parse JSON schema: {e}")

    @staticmethod
    def normalize_json_object(
        value: t.ContainerValueMapping,
    ) -> t.JsonObject:
        """Normalize a mapping to a JSON t.RecursiveContainer.

        Recursively converts values to valid JSON types.

        Args:
            value: Mapping to normalize

        Returns:
            Normalized JSON t.RecursiveContainer

        """
        normalized: t.MutableContainerValueMapping = {}
        for key, item in value.items():
            normalized[key] = FlextApiSchemaShared.to_general_value(item)
        return normalized

    @staticmethod
    def to_general_value(value: t.ContainerValue) -> t.ContainerValue:
        """Validate value as a general container value using centralized contracts."""
        return t.Api.CONTAINER_VALUE_ADAPTER.validate_python(value)

    @staticmethod
    def parse_dict_field(
        value: t.ApiJsonValue,
        field_name: str,
    ) -> p.Result[t.ContainerValueMapping]:
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
            parsed = m.Api.DictField(value=dict(value))
        except c.ValidationError:
            return r[t.ContainerValueMapping].fail(
                f"'{field_name}' field must be a dictionary",
            )
        return r[t.ContainerValueMapping].ok(parsed.value)

    @staticmethod
    def parse_string_field(value: t.ApiJsonValue, field_name: str) -> p.Result[str]:
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
            parsed = m.Api.StringField(value=value)
        except c.ValidationError:
            return r[str].fail(f"'{field_name}' field must be a string")
        return r[str].ok(parsed.value)

    @staticmethod
    def parse_int_field(value: t.ApiJsonValue, field_name: str) -> p.Result[int]:
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
            parsed = m.Api.IntField(value=value)
        except c.ValidationError:
            return r[int].fail(f"'{field_name}' field must be an integer")
        return r[int].ok(parsed.value)

    @staticmethod
    def load_and_validate_schema_document[TValidation](
        schema_source: str,
        *,
        schema_label: str,
        validate_schema: Callable[[t.JsonObject], p.Result[TValidation]],
    ) -> p.Result[t.ContainerValue]:
        """Load and validate a schema document.

        Args:
            schema_source: Path to schema file
            schema_label: Label for error messages
            validate_schema: Callable to validate the normalized schema

        Returns:
            r containing the normalized schema or error message

        """
        schema_result = FlextApiSchemaShared.load_schema_document(schema_source)
        if schema_result.failure:
            return r[t.ContainerValue].fail(
                schema_result.error or f"Failed to load {schema_label} schema",
            )
        loaded_schema = schema_result.value
        if not FlextApiSchemaShared.object_mapping(loaded_schema):
            return r[t.ContainerValue].fail(
                f"{schema_label} schema must be a JSON/YAML t.RecursiveContainer",
            )
        normalized_schema = FlextApiSchemaShared.normalize_json_object(loaded_schema)
        validation_result = validate_schema(normalized_schema)
        if validation_result.failure:
            return r[t.ContainerValue].fail(
                f"Invalid {schema_label} schema: {validation_result.error}",
            )
        normalized_result: t.ContainerValue = normalized_schema
        return r[t.ContainerValue].ok(normalized_result)


__all__: list[str] = ["FlextApiSchemaShared"]
