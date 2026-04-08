# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Schemas package."""

from __future__ import annotations

from flext_core.lazy import install_lazy_exports

_LAZY_IMPORTS = {
    "FlextApiAsyncapiSchemaValidator": (
        "flext_api.schemas.asyncapi",
        "FlextApiAsyncapiSchemaValidator",
    ),
    "FlextApiJsonschemaValidator": (
        "flext_api.schemas.jsonschema",
        "FlextApiJsonschemaValidator",
    ),
    "FlextApiOpenapiSchemaValidator": (
        "flext_api.schemas.openapi",
        "FlextApiOpenapiSchemaValidator",
    ),
    "FlextApiSchemaShared": ("flext_api.schemas._shared", "FlextApiSchemaShared"),
    "asyncapi": "flext_api.schemas.asyncapi",
    "c": ("flext_core.constants", "FlextConstants"),
    "d": ("flext_core.decorators", "FlextDecorators"),
    "e": ("flext_core.exceptions", "FlextExceptions"),
    "h": ("flext_core.handlers", "FlextHandlers"),
    "is_container_value": ("flext_api.schemas._shared", "is_container_value"),
    "is_object_mapping": ("flext_api.schemas._shared", "is_object_mapping"),
    "jsonschema": "flext_api.schemas.jsonschema",
    "load_and_validate_schema_document": (
        "flext_api.schemas._shared",
        "load_and_validate_schema_document",
    ),
    "load_schema_document": ("flext_api.schemas._shared", "load_schema_document"),
    "m": ("flext_core.models", "FlextModels"),
    "normalize_json_object": ("flext_api.schemas._shared", "normalize_json_object"),
    "openapi": "flext_api.schemas.openapi",
    "p": ("flext_core.protocols", "FlextProtocols"),
    "parse_dict_field": ("flext_api.schemas._shared", "parse_dict_field"),
    "parse_int_field": ("flext_api.schemas._shared", "parse_int_field"),
    "parse_string_field": ("flext_api.schemas._shared", "parse_string_field"),
    "r": ("flext_core.result", "FlextResult"),
    "s": ("flext_core.service", "FlextService"),
    "t": ("flext_core.typings", "FlextTypes"),
    "to_general_value": ("flext_api.schemas._shared", "to_general_value"),
    "u": ("flext_core.utilities", "FlextUtilities"),
    "x": ("flext_core.mixins", "FlextMixins"),
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, publish_all=False)
