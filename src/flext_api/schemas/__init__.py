# AUTO-GENERATED FILE — Regenerate with: make gen
"""Schemas package."""

from __future__ import annotations

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

_LAZY_IMPORTS = build_lazy_import_map(
    {
        "._shared": (
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
        ),
        ".asyncapi": ("FlextApiAsyncapiSchemaValidator",),
        ".jsonschema": ("FlextApiJsonschemaValidator",),
        ".openapi": ("FlextApiOpenapiSchemaValidator",),
    },
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, publish_all=False)
