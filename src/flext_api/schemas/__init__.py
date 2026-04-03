# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Schemas package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING as _TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if _TYPE_CHECKING:
    from flext_api.schemas import _shared, asyncapi, jsonschema, openapi
    from flext_api.schemas._shared import (
        FlextApiSchemaShared,
        is_container_value,
        is_object_mapping,
        load_and_validate_schema_document,
        load_schema_document,
        normalize_json_object,
        parse_dict_field,
        parse_int_field,
        parse_string_field,
        to_general_value,
    )
    from flext_api.schemas.asyncapi import FlextApiAsyncapiSchemaValidator
    from flext_api.schemas.jsonschema import FlextApiJsonschemaValidator
    from flext_api.schemas.openapi import FlextApiOpenapiSchemaValidator
    from flext_core import FlextTypes
    from flext_core.constants import FlextConstants as c
    from flext_core.decorators import FlextDecorators as d
    from flext_core.exceptions import FlextExceptions as e
    from flext_core.handlers import FlextHandlers as h
    from flext_core.mixins import FlextMixins as x
    from flext_core.models import FlextModels as m
    from flext_core.protocols import FlextProtocols as p
    from flext_core.result import FlextResult as r
    from flext_core.service import FlextService as s
    from flext_core.typings import FlextTypes as t
    from flext_core.utilities import FlextUtilities as u

_LAZY_IMPORTS: FlextTypes.LazyImportIndex = {
    "FlextApiAsyncapiSchemaValidator": "flext_api.schemas.asyncapi",
    "FlextApiJsonschemaValidator": "flext_api.schemas.jsonschema",
    "FlextApiOpenapiSchemaValidator": "flext_api.schemas.openapi",
    "FlextApiSchemaShared": "flext_api.schemas._shared",
    "_shared": "flext_api.schemas._shared",
    "asyncapi": "flext_api.schemas.asyncapi",
    "c": ("flext_core.constants", "FlextConstants"),
    "d": ("flext_core.decorators", "FlextDecorators"),
    "e": ("flext_core.exceptions", "FlextExceptions"),
    "h": ("flext_core.handlers", "FlextHandlers"),
    "is_container_value": "flext_api.schemas._shared",
    "is_object_mapping": "flext_api.schemas._shared",
    "jsonschema": "flext_api.schemas.jsonschema",
    "load_and_validate_schema_document": "flext_api.schemas._shared",
    "load_schema_document": "flext_api.schemas._shared",
    "m": ("flext_core.models", "FlextModels"),
    "normalize_json_object": "flext_api.schemas._shared",
    "openapi": "flext_api.schemas.openapi",
    "p": ("flext_core.protocols", "FlextProtocols"),
    "parse_dict_field": "flext_api.schemas._shared",
    "parse_int_field": "flext_api.schemas._shared",
    "parse_string_field": "flext_api.schemas._shared",
    "r": ("flext_core.result", "FlextResult"),
    "s": ("flext_core.service", "FlextService"),
    "t": ("flext_core.typings", "FlextTypes"),
    "to_general_value": "flext_api.schemas._shared",
    "u": ("flext_core.utilities", "FlextUtilities"),
    "x": ("flext_core.mixins", "FlextMixins"),
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
