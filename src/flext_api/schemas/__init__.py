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

from typing import TYPE_CHECKING

from flext_api.schemas._lazy_exports import (
    __all__ as __all__,
    __dir__ as __dir__,
    __getattr__ as __getattr__,
)

if TYPE_CHECKING:
    from flext_api.schemas.asyncapi import (
        AsyncAPISchemaValidator as AsyncAPISchemaValidator,
    )
    from flext_api.schemas.jsonschema import JSONSchemaValidator as JSONSchemaValidator
    from flext_api.schemas.openapi import (
        OpenAPISchemaValidator as OpenAPISchemaValidator,
    )
