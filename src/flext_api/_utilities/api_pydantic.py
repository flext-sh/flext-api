"""API Pydantic utility shard."""

from __future__ import annotations

from enum import StrEnum

from flext_api import p, t
from flext_web import m, u


class FlextApiUtilitiesApiPydantic:
    """Pydantic utility namespace shard for ``u.Api``."""

    class Pydantic:
        """Annotated type factories."""

        @staticmethod
        def coerced_enum_validator(enum_cls: type[StrEnum]) -> p.BeforeValidator:
            """Create a validator for automatic StrEnum coercion."""

            def _coerce(v: str | StrEnum) -> StrEnum:
                result = u.parse(v, enum_cls)
                if result.failure:
                    msg = result.error or f"Invalid {enum_cls.__name__}: {v!r}"
                    raise ValueError(msg)
                return enum_cls(v) if not isinstance(v, enum_cls) else v

            return m.BeforeValidator(_coerce)


__all__: t.MutableSequenceOf[str] = ["FlextApiUtilitiesApiPydantic"]
