"""FlextApi utilities module."""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated

from flext_core import r, u as u_core
from pydantic import BeforeValidator


class FlextApiUtilities(u_core):
    """FlextApi utilities extending FlextUtilities with API-specific helpers.

    Architecture: Advanced utilities with ZERO code bloat through:
    - TypeIs/TypeGuard for narrowing (PEP 742)
    - BeforeValidator factories for Pydantic coercion
    - @validated decorators eliminating manual validation
    - Generic parsing utilities for StrEnums (inherited from parent)
    """

    # ═══════════════════════════════════════════════════════════════════
    # API NAMESPACE: Project-specific utilities
    # ═══════════════════════════════════════════════════════════════════

    class Api:
        """API-specific utility namespace.

        This namespace groups all API-specific utilities for better organization
        and cross-project access. Access via u.Api.* pattern.

        Example:
            from flext_api.utilities import u
            result = u.Api.Collection.parse_sequence(Status, ["active", "pending"])
            parsed = u.Api.Args.parse_kwargs(kwargs, enum_fields)

        """

        class Collection(u_core.Collection):
            """Collection utilities extending u_core.Collection via inheritance.

            Exposes all flext-core Collection methods through inheritance hierarchy.
            Access via u.Api.Collection.* pattern.
            """

        # ═══════════════════════════════════════════════════════════════════
        # ARGS UTILITIES: @validated, parse_kwargs - ZERO validation boilerplate
        # ═══════════════════════════════════════════════════════════════════

        class Args(u_core.Args):
            """Args utilities extending u_core.Args via inheritance.

            Exposes all flext-core Args methods through inheritance hierarchy,
            including validated, validated_with_result, parse_kwargs, and get_enum_params.
            Access via u.Api.Args.* pattern.
            """

        # ═══════════════════════════════════════════════════════════════════
        # MODEL UTILITIES: from_dict, merge_defaults, update - ZERO try/except
        # ═══════════════════════════════════════════════════════════════════

        class Model(u_core.Model):
            """Model utilities extending u_core.Model via inheritance.

            Exposes all flext-core Model methods through inheritance hierarchy.
            Access via u.Api.Model.* pattern.
            """

        # ═══════════════════════════════════════════════════════════════════
        # PYDANTIC UTILITIES: Annotated type factories
        # ═══════════════════════════════════════════════════════════════════

        class Pydantic:
            """Annotated type factories."""

            @staticmethod
            def coerced_enum[E: StrEnum](enum_cls: type[E]) -> object:
                """Create Annotated type with automatic enum coercion.

                Business Rule: Returns an Annotated type that automatically converts
                string values to enum instances using BeforeValidator. This enables
                Pydantic models to accept both string and enum values for enum fields.
                Returns `object` type annotation because Annotated is a special typing
                form that cannot be expressed as a regular type annotation.

                Audit Implication: Type-safe enum coercion in Pydantic models without
                manual validation code. The returned value is an Annotated type that
                Pydantic recognizes for automatic validation.
                """
                # Return Annotated type directly - Pydantic recognizes this pattern
                # The BeforeValidator is instantiated with the coerce_validator function
                # Annotated is a special typing form, not a regular class type
                return Annotated[
                    enum_cls,
                    BeforeValidator(u_core.Enum.coerce_validator(enum_cls)),
                ]

        # ═══════════════════════════════════════════════════════════════════
        # REQUEST UTILITIES: Request utilities for extracting and validating HTTP request components
        # ═══════════════════════════════════════════════════════════════════

        class RequestUtils:
            """Request utilities for extracting and validating HTTP request components."""

            @staticmethod
            def extract_body_from_kwargs(
                data: object | None,
                kwargs: dict[str, object] | None,
            ) -> r[object | None]:
                """Extract body from data or kwargs."""
                if data is not None:
                    return r.ok(data)
                if kwargs is not None and "data" in kwargs:
                    return r.ok(kwargs["data"])
                if kwargs is not None and "json" in kwargs:
                    return r.ok(kwargs["json"])
                return r.ok(None)

            @staticmethod
            def merge_headers(
                headers: dict[str, str] | None,
                kwargs: dict[str, object] | None,
            ) -> r[dict[str, str]]:
                """Merge headers from headers dict and kwargs."""
                merged: dict[str, str] = {}
                if headers:
                    merged.update(headers)
                if kwargs and "headers" in kwargs:
                    headers_value = kwargs["headers"]
                    if isinstance(headers_value, dict):
                        merged.update({k: str(v) for k, v in headers_value.items()})
                return r.ok(merged)

            @staticmethod
            def validate_and_extract_timeout(
                timeout: float | None,
                kwargs: dict[str, object] | None,
            ) -> r[float]:
                """Validate and extract timeout from timeout value or kwargs."""
                if timeout is not None and timeout > 0:
                    return r.ok(timeout)
                if kwargs and "timeout" in kwargs:
                    timeout_value = kwargs["timeout"]
                    if isinstance(timeout_value, (int, float)) and timeout_value > 0:
                        return r.ok(float(timeout_value))
                return r.fail("Timeout must be a positive number")


u = FlextApiUtilities  # Runtime alias (not TypeAlias to avoid PYI042)

__all__ = [
    "FlextApiUtilities",
    "u",
]
