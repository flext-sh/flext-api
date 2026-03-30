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
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_api.schemas import (
        asyncapi as asyncapi,
        jsonschema as jsonschema,
        openapi as openapi,
    )
    from flext_api.schemas.asyncapi import (
        FlextApiAsyncapiSchemaValidator as FlextApiAsyncapiSchemaValidator,
    )
    from flext_api.schemas.jsonschema import (
        FlextApiJsonschemaValidator as FlextApiJsonschemaValidator,
    )
    from flext_api.schemas.openapi import (
        FlextApiOpenapiSchemaValidator as FlextApiOpenapiSchemaValidator,
    )

_LAZY_IMPORTS: Mapping[str, Sequence[str]] = {
    "FlextApiAsyncapiSchemaValidator": [
        "flext_api.schemas.asyncapi",
        "FlextApiAsyncapiSchemaValidator",
    ],
    "FlextApiJsonschemaValidator": [
        "flext_api.schemas.jsonschema",
        "FlextApiJsonschemaValidator",
    ],
    "FlextApiOpenapiSchemaValidator": [
        "flext_api.schemas.openapi",
        "FlextApiOpenapiSchemaValidator",
    ],
    "asyncapi": ["flext_api.schemas.asyncapi", ""],
    "jsonschema": ["flext_api.schemas.jsonschema", ""],
    "openapi": ["flext_api.schemas.openapi", ""],
}

_EXPORTS: Sequence[str] = [
    "FlextApiAsyncapiSchemaValidator",
    "FlextApiJsonschemaValidator",
    "FlextApiOpenapiSchemaValidator",
    "asyncapi",
    "jsonschema",
    "openapi",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, _EXPORTS)
