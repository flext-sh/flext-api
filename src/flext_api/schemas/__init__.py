# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Schema validation systems for flext-api.

Provides schema validation for:
- OpenAPI 3.x specifications
- JSON Schema validation
- AsyncAPI specifications

See TRANSFORMATION_PLAN.md - Phase 5 for implementation details.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING as _TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if _TYPE_CHECKING:
    from flext_api.schemas._shared import *
    from flext_api.schemas.asyncapi import *
    from flext_api.schemas.jsonschema import *
    from flext_api.schemas.openapi import *

_LAZY_IMPORTS: Mapping[str, str | Sequence[str]] = {
    "FlextApiAsyncapiSchemaValidator": "flext_api.schemas.asyncapi",
    "FlextApiJsonschemaValidator": "flext_api.schemas.jsonschema",
    "FlextApiOpenapiSchemaValidator": "flext_api.schemas.openapi",
    "FlextApiSchemaShared": "flext_api.schemas._shared",
    "_shared": "flext_api.schemas._shared",
    "asyncapi": "flext_api.schemas.asyncapi",
    "is_container_value": "flext_api.schemas._shared",
    "is_object_mapping": "flext_api.schemas._shared",
    "jsonschema": "flext_api.schemas.jsonschema",
    "load_and_validate_schema_document": "flext_api.schemas._shared",
    "load_schema_document": "flext_api.schemas._shared",
    "normalize_json_object": "flext_api.schemas._shared",
    "openapi": "flext_api.schemas.openapi",
    "parse_dict_field": "flext_api.schemas._shared",
    "parse_int_field": "flext_api.schemas._shared",
    "parse_string_field": "flext_api.schemas._shared",
    "to_general_value": "flext_api.schemas._shared",
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
