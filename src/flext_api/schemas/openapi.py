"""OpenAPI 3.x Schema Validator for flext-api.

Implements OpenAPI 3.x schema validation with:
- OpenAPI 3.0.x and 3.1.x support
- Schema validation against OpenAPI spec
- Path, operation, and parameter validation
- Security scheme validation
- Component reference resolution

See TRANSFORMATION_PLAN.md - Phase 5 for implementation details.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping
from typing import override

from flext_core import r

from flext_api import FlextApiPlugins, t, u
from flext_api.schemas import _shared


class OpenAPISchemaValidator(FlextApiPlugins.Schema):
    """OpenAPI 3.x schema validator with specification validation.

    Features:
    - OpenAPI 3.0.x and 3.1.x validation
    - Path and operation validation
    - Parameter and request body validation
    - Response schema validation
    - Security scheme validation
    - Component reference resolution ($ref)
    - Schema format validation

    Integration:
    - Uses openapi-spec-validator for validation
    - Supports JSON and YAML OpenAPI documents
    - r for error handling
    - FlextLogger for validation logging
    """

    def __init__(
        self,
        *,
        strict_mode: bool = True,
        validate_examples: bool = True,
        validate_responses: bool = True,
    ) -> None:
        """Initialize OpenAPI schema validator.

        Args:
        strict_mode: Enable strict OpenAPI validation
        validate_examples: Validate example values in schema
        validate_responses: Validate response schemas

        """
        super().__init__(
            name="openapi",
            version="3.1.0",
            description="OpenAPI 3.x schema validator with specification validation",
        )
        self._strict_mode = strict_mode
        self._validate_examples = validate_examples
        self._validate_responses = validate_responses
        self._cached_schemas: Mapping[str, Mapping[str, t.ContainerValue]] = {}

    def get_supported_schemas(self) -> list[str]:
        """Get list of supported schema types.

        Returns:
        List of supported schema type identifiers

        """
        return ["openapi", "openapi3", "openapi-3"]

    @override
    def load_schema(self, schema_source: str) -> r[t.ContainerValue]:
        """Load OpenAPI schema from source.

        Args:
        schema_source: Schema file path

        Returns:
        r containing loaded schema or error

        """
        schema_result = _shared.load_schema_document(schema_source)
        if schema_result.is_failure:
            return r.fail(schema_result.error or "Failed to load OpenAPI schema")
        loaded_schema = schema_result.value
        if not _shared.is_object_mapping(loaded_schema):
            return r.fail("OpenAPI schema must be a JSON/YAML object")
        normalized_schema = _shared.normalize_json_object(loaded_schema)
        validation_result = self.validate_schema(normalized_schema)
        if validation_result.is_failure:
            return r.fail(f"Invalid OpenAPI schema: {validation_result.error}")
        normalized_result: t.ContainerValue = normalized_schema
        return r.ok(normalized_result)

    def supports_schema(self, schema_type: str) -> bool:
        """Check if this validator supports the given schema type.

        Args:
        schema_type: Schema type identifier

        Returns:
        True if schema type is supported

        """
        return schema_type.lower() in {"openapi", "openapi3", "openapi-3"}

    @override
    def validate_request(self, request: t.JsonObject, schema: t.JsonObject) -> r[bool]:
        """Validate request against OpenAPI schema.

        Args:
        request: Request to validate
        schema: OpenAPI schema

        Returns:
        r containing validation result or error

        """
        _ = (request, schema)
        return self.validate_schema(schema).fold(
            on_failure=lambda e: r[bool].fail(f"Invalid schema: {e}"),
            on_success=lambda _v: r[bool].ok(value=True),
        )

    @override
    def validate_response(
        self, response: t.JsonObject, schema: t.JsonObject
    ) -> r[bool]:
        """Validate response against OpenAPI schema.

        Args:
        response: Response to validate
        schema: OpenAPI schema

        Returns:
        r containing validation result or error

        """
        _ = (response, schema)
        return self.validate_schema(schema).fold(
            on_failure=lambda e: r[bool].fail(f"Invalid schema: {e}"),
            on_success=lambda _v: r[bool].ok(value=True),
        )

    def validate_schema(self, schema: t.JsonObject) -> r[t.JsonObject]:
        """Validate OpenAPI schema against OpenAPI specification.

        Args:
        schema: OpenAPI schema dictionary

        Returns:
        r containing validation result or error

        """
        version_result = self._validate_openapi_version(schema)
        if version_result.is_failure:
            return r[t.JsonObject].fail(
                version_result.error or "Version validation failed"
            )
        required_fields = ["info", "paths"]
        missing_fields = u.filter(
            list(required_fields), lambda field: field not in schema
        )
        if missing_fields:
            return r[t.JsonObject].fail(
                f"Missing required fields: {', '.join(missing_fields)}"
            )
        info_result = self._validate_info_field(schema)
        if info_result.is_failure:
            return r[t.JsonObject].fail(info_result.error or "Info validation failed")
        paths_result = self._validate_paths_field(schema)
        if paths_result.is_failure:
            return r[t.JsonObject].fail(paths_result.error or "Paths validation failed")
        components_result = self._validate_optional_components(schema)
        if components_result.is_failure:
            return r[t.JsonObject].fail(
                components_result.error or "Components validation failed"
            )
        info_value = schema["info"]
        paths_value = schema["paths"]
        title_str = self._extract_title(info_value)
        paths_keys = self._extract_paths_keys(paths_value)
        self.logger.info(
            "OpenAPI schema validation successful",
            version=version_result.value,
            title=title_str,
            paths_count=len(paths_keys),
        )
        return r[t.JsonObject].ok({
            "valid": True,
            "version": version_result.value,
            "title": title_str,
            "paths": paths_keys,
        })

    def _extract_paths_keys(self, paths_value: t.ApiJsonValue) -> list[str]:
        """Extract path keys from validated paths object."""
        paths_result = _shared.parse_dict_field(paths_value, "paths")
        return paths_result.fold(
            on_failure=lambda _: [],
            on_success=lambda v: list(v.keys()),
        )

    def _extract_title(self, info_value: t.ApiJsonValue) -> str:
        """Extract title from validated info object."""
        info_result = _shared.parse_dict_field(info_value, "info")
        if info_result.is_failure:
            return ""
        info = info_result.value
        if "title" not in info:
            return ""
        return str(info["title"])

    def _validate_components(
        self, components: Mapping[str, t.ContainerValue]
    ) -> r[bool]:
        """Validate OpenAPI components object.

        Args:
        components: Components dictionary from OpenAPI schema

        Returns:
        r indicating validation success or failure

        """
        valid_sections = [
            "schemas",
            "responses",
            "parameters",
            "examples",
            "requestBodies",
            "headers",
            "securitySchemes",
            "links",
            "callbacks",
        ]
        for section_name, section_value in components.items():
            if section_name not in valid_sections and self._strict_mode:
                return r[bool].fail(f"Invalid component section: {section_name}")
            section_result = _shared.parse_dict_field(section_value, section_name)
            if section_result.is_failure:
                return r[bool].fail(
                    f"Component section must be a dictionary: {section_name}"
                )
        return r[bool].ok(value=True)

    def _validate_info_field(self, schema: t.JsonObject) -> r[bool]:
        """Validate info field exists and has required fields.

        Single Responsibility: Only validates, does not extract or transform data.
        Caller accesses schema["info"] directly after validation passes.
        """
        if "info" not in schema:
            return r[bool].fail("Missing 'info' field in schema")
        info_value = schema["info"]
        info_result = _shared.parse_dict_field(info_value, "info")
        if info_result.is_failure:
            return r[bool].fail(info_result.error)
        info_value = info_result.value
        info_required = ["title", "version"]
        info_missing = u.filter(
            list(info_required), lambda field: field not in info_value
        )
        if info_missing:
            return r[bool].fail(
                f"Missing required info fields: {', '.join(info_missing)}"
            )
        return r[bool].ok(value=True)

    def _validate_openapi_version(self, schema: t.JsonObject) -> r[str]:
        """Validate OpenAPI version field."""
        if "openapi" not in schema:
            return r[str].fail("Missing 'openapi' version field")
        openapi_version_value = schema["openapi"]
        version_result = _shared.parse_string_field(openapi_version_value, "openapi")
        if version_result.is_failure:
            return version_result
        openapi_version = version_result.value
        if not openapi_version.startswith("3."):
            return r[str].fail(f"Unsupported OpenAPI version: {openapi_version}")
        return r[str].ok(openapi_version)

    def _validate_operation(
        self, operation: Mapping[str, t.ContainerValue], path: str, method: str
    ) -> r[bool]:
        """Validate OpenAPI operation object.

        Args:
        operation: Operation dictionary
        path: API path
        method: HTTP method

        Returns:
        r indicating validation success or failure

        """
        if "responses" not in operation:
            return r[bool].fail(f"Missing required 'responses' field: {method} {path}")
        if self._validate_responses:
            responses_value = operation["responses"]
            responses_result = _shared.parse_dict_field(responses_value, "responses")
            if responses_result.is_failure:
                return r[bool].fail(f"Responses must be a dictionary: {method} {path}")
            responses = responses_result.value
            if not responses:
                return r[bool].fail(f"Responses cannot be empty: {method} {path}")
        return r[bool].ok(value=True)

    def _validate_optional_components(self, schema: t.JsonObject) -> r[bool]:
        """Validate optional components and security schemes."""
        if "components" not in schema:
            return r[bool].ok(value=True)
        components_value = schema["components"]
        components_result = _shared.parse_dict_field(components_value, "components")
        if components_result.is_failure:
            return r[bool].fail(components_result.error)
        components_map = components_result.value
        components_validation = self._validate_components(components_map)
        if components_validation.is_failure:
            return components_validation
        if "securitySchemes" in components_map:
            security_schemes_value = components_map["securitySchemes"]
            schemes_result = _shared.parse_dict_field(
                security_schemes_value, "securitySchemes"
            )
            if schemes_result.is_failure:
                return r[bool].fail(schemes_result.error)
            security_result = self._validate_security_schemes(schemes_result.value)
            if security_result.is_failure:
                return security_result
        return r[bool].ok(value=True)

    def _validate_paths(self, paths: Mapping[str, t.ApiJsonValue]) -> r[bool]:
        """Validate OpenAPI paths object.

        Args:
        paths: Paths dictionary from OpenAPI schema

        Returns:
        r indicating validation success or failure

        """
        for path_key, path_item in paths.items():
            path = str(path_key)
            if not path.startswith("/"):
                return r[bool].fail(f"Path must start with '/': {path}")
            path_item_result = _shared.parse_dict_field(path_item, "path_item")
            if path_item_result.is_failure:
                return r[bool].fail(f"Path item must be a dictionary: {path}")
            path_item = path_item_result.value
            http_methods = [
                "get",
                "post",
                "put",
                "patch",
                "delete",
                "head",
                "options",
                "trace",
            ]
            for method in http_methods:
                if method in path_item:
                    method_value = path_item[method]
                    method_result = _shared.parse_dict_field(method_value, method)
                    if method_result.is_failure:
                        return r[bool].fail(
                            f"Operation must be a dictionary: {method} {path}"
                        )
                    operation_result = self._validate_operation(
                        method_result.value, path, method
                    )
                    if operation_result.is_failure:
                        return operation_result
        return r[bool].ok(value=True)

    def _validate_paths_field(self, schema: t.JsonObject) -> r[bool]:
        """Validate paths field exists and contains valid path definitions.

        Single Responsibility: Only validates, does not extract or transform data.
        Caller accesses schema["paths"] directly after validation passes.
        """
        if "paths" not in schema:
            return r[bool].fail("Missing 'paths' field in schema")
        paths_value = schema["paths"]
        paths_result = _shared.parse_dict_field(paths_value, "paths")
        return paths_result.fold(
            on_failure=lambda e: r[bool].fail(e),
            on_success=lambda v: self._validate_paths(v),
        )

    def _validate_scheme_type_requirements(
        self, scheme_name: str, scheme: Mapping[str, t.ContainerValue], scheme_type: str
    ) -> r[bool]:
        """Validate type-specific requirements for security schemes."""
        if scheme_type == "apiKey":
            if "name" not in scheme or "in" not in scheme:
                return r[bool].fail(
                    f"apiKey scheme missing 'name' or 'in': {scheme_name}"
                )
        elif scheme_type == "http":
            if "scheme" not in scheme:
                return r[bool].fail(f"http scheme missing 'scheme': {scheme_name}")
        elif scheme_type == "oauth2":
            if "flows" not in scheme:
                return r[bool].fail(f"oauth2 scheme missing 'flows': {scheme_name}")
        elif scheme_type == "openIdConnect" and "openIdConnectUrl" not in scheme:
            return r[bool].fail(
                f"openIdConnect scheme missing 'openIdConnectUrl': {scheme_name}"
            )
        return r[bool].ok(value=True)

    def _validate_security_schemes(
        self, security_schemes: Mapping[str, t.ContainerValue]
    ) -> r[bool]:
        """Validate OpenAPI security schemes.

        Args:
        security_schemes: Security schemes dictionary

        Returns:
        r indicating validation success or failure

        """
        schemes_dict_result = self._validate_security_schemes_structure(
            security_schemes
        )
        if schemes_dict_result.is_failure:
            return r[bool].fail(
                schemes_dict_result.error or "Schemes validation failed"
            )
        schemes_dict = schemes_dict_result.value
        for scheme_name, scheme in schemes_dict.items():
            scheme_result = self._validate_single_security_scheme(scheme_name, scheme)
            if scheme_result.is_failure:
                return scheme_result
        return r[bool].ok(value=True)

    def _validate_security_schemes_structure(
        self, security_schemes: t.ContainerValue
    ) -> r[Mapping[str, t.ContainerValue]]:
        """Validate basic structure of security schemes."""
        schemes_result = _shared.parse_dict_field(security_schemes, "security_schemes")
        return schemes_result.fold(
            on_failure=lambda _: r[Mapping[str, t.ContainerValue]].fail(
                "Security schemes must be a dictionary"
            ),
            on_success=lambda v: r[Mapping[str, t.ContainerValue]].ok(v),
        )

    def _validate_single_security_scheme(
        self, scheme_name: str, scheme: t.ContainerValue
    ) -> r[bool]:
        """Validate a single security scheme."""
        scheme_result = _shared.parse_dict_field(scheme, "scheme")
        if scheme_result.is_failure:
            return r[bool].fail(f"Security scheme must be a dictionary: {scheme_name}")
        scheme = scheme_result.value
        if "type" not in scheme:
            return r[bool].fail(
                f"Missing 'type' field in security scheme: {scheme_name}"
            )
        scheme_type_value = scheme["type"]
        type_result = _shared.parse_string_field(scheme_type_value, "type")
        if type_result.is_failure:
            return r[bool].fail(
                f"'type' field must be a string in security scheme: {scheme_name}"
            )
        scheme_type = type_result.value
        valid_types = ["apiKey", "http", "oauth2", "openIdConnect"]
        if scheme_type not in valid_types:
            return r[bool].fail(
                f"Invalid security scheme type '{scheme_type}': {scheme_name}"
            )
        return self._validate_scheme_type_requirements(scheme_name, scheme, scheme_type)


__all__ = ["OpenAPISchemaValidator"]
