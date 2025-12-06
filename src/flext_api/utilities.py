"""FlextApi utilities module."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from enum import StrEnum
from functools import cache, wraps
from typing import Annotated, TypeIs, TypeVar, get_type_hints

from flext_core import r, u as u_core
from flext_core.typings import P, R
from pydantic import BaseModel, BeforeValidator, ConfigDict, validate_call

T = TypeVar("T")


class FlextApiUtilities(u_core):
    """TypeIs (PEP 742), BeforeValidator, validate_call, collections.abc, ParamSpec."""

    class Enum:
        """TypeIs genérico, parsing, coerção - ZERO TypeGuard manual."""

        @staticmethod
        def is_member[E: StrEnum](value: object, enum_cls: type[E]) -> TypeIs[E]:
            """TypeIs narrowing em AMBAS branches if/else.

            Business Rule: TypeIs[E] returns bool but narrows value to type E when True.
            This allows type narrowing in if/else branches without explicit casts.
            Uses isinstance check first, then string membership check for StrEnum compatibility.
            Note: value must be first parameter for TypeIs to narrow correctly.

            Audit Implication: Type-safe enum validation without runtime overhead.
            """
            # TypeIs[E] narrows the first positional parameter (value)
            # When this returns True, mypy narrows 'value' to type E in the calling context
            if isinstance(value, enum_cls):
                return True
            if isinstance(value, str):
                return value in enum_cls._value2member_map_
            return False

        @staticmethod
        def is_subset[E: StrEnum](
            value: object,
            enum_cls: type[E],
            valid: frozenset[E],
        ) -> TypeIs[E]:
            """Check if value is subset of valid enum values.

            Business Rule: TypeIs[E] returns bool but narrows value to type E when True.
            Validates that value is both a valid enum member AND in the valid subset.
            Uses isinstance check first, then string parsing for StrEnum compatibility.
            Note: value must be first parameter for TypeIs to narrow correctly.

            Audit Implication: Type-safe subset validation for enum values.
            """
            # TypeIs[E] narrows the first positional parameter (value)
            if isinstance(value, enum_cls):
                return value in valid
            if isinstance(value, str):
                try:
                    parsed_value = enum_cls(value)
                    return parsed_value in valid
                except ValueError:
                    return False
            return False

        @staticmethod
        def parse[E: StrEnum](enum_cls: type[E], value: str | E) -> r[E]:
            """Parse string or enum value to enum instance.

            Business Rule: Accepts both string and enum values, converting strings
            to enum instances. Returns r for railway-oriented error handling.

            Audit Implication: Type-safe enum parsing with automatic conversion.
            """
            if isinstance(value, enum_cls):
                return r.ok(value)
            try:
                return r.ok(enum_cls(value))
            except ValueError:
                return r.fail(f"Invalid {enum_cls.__name__}: '{value}'")

        @staticmethod
        def coerce_validator[E: StrEnum](enum_cls: type[E]) -> Callable[[object], E]:
            """BeforeValidator factory para Pydantic.

            Business Rule: Creates a validator function for Pydantic's BeforeValidator
            that accepts both enum instances and string values, converting strings
            to enum instances automatically.

            Audit Implication: Enables automatic enum coercion in Pydantic models.
            """

            def _coerce(v: object) -> E:
                if isinstance(v, enum_cls):
                    return v
                if isinstance(v, str):
                    try:
                        return enum_cls(v)
                    except ValueError:
                        pass
                msg = f"Invalid {enum_cls.__name__}: {v!r}"
                raise ValueError(msg)

            return _coerce

        @staticmethod
        @cache
        def values[E: StrEnum](enum_cls: type[E]) -> frozenset[str]:
            """Get all enum values as a frozenset.

            Business Rule: Returns all enum member values as an immutable set
            for efficient membership testing and validation.

            Audit Implication: Cached for performance - same enum class returns
            same frozenset instance.
            """
            return frozenset(m.value for m in enum_cls)

    class Collection:
        """Parsing de Sequence/Mapping com StrEnums."""

        @staticmethod
        def parse_sequence[E: StrEnum](
            enum_cls: type[E],
            values: Iterable[str | E],
        ) -> r[tuple[E, ...]]:
            """Parse sequence of string or enum values to tuple of enum instances.

            Business Rule: Accepts iterable of strings or enum values, converting
            all to enum instances. Returns r with tuple of parsed enums
            or failure with list of invalid values.

            Audit Implication: Type-safe sequence parsing with detailed error reporting.
            """
            parsed, errors = [], []
            for i, v in enumerate(values):
                if isinstance(v, enum_cls):
                    parsed.append(v)
                else:
                    try:
                        parsed.append(enum_cls(v))
                    except ValueError:
                        errors.append(f"[{i}]: '{v}'")
            return r.fail(f"Invalid: {errors}") if errors else r.ok(tuple(parsed))

        @staticmethod
        def coerce_list_validator[E: StrEnum](
            enum_cls: type[E],
        ) -> Callable[[object], list[E]]:
            """Create BeforeValidator for list of enum values.

            Business Rule: Creates a validator function for Pydantic's BeforeValidator
            that accepts sequences (list, tuple, set) and converts all items to enum
            instances. Raises TypeError for invalid types, ValueError for invalid enum values.

            Audit Implication: Enables automatic enum list coercion in Pydantic models.
            """

            def _coerce(value: object) -> list[E]:
                if not isinstance(value, (list, tuple, set)):
                    msg = "Expected sequence"
                    raise TypeError(msg)
                result = []
                for i, item in enumerate(value):
                    if isinstance(item, enum_cls):
                        result.append(item)
                    elif isinstance(item, str):
                        try:
                            result.append(enum_cls(item))
                        except ValueError as err:
                            msg = f"Invalid at [{i}]: {item!r}"
                            raise ValueError(msg) from err
                    else:
                        msg = f"Expected str at [{i}]"
                        raise TypeError(msg)
                return result

            return _coerce

    class Args:
        """@validated, parse_kwargs - ZERO boilerplate de validação."""

        @staticmethod
        def validated(func: Callable[P, R]) -> Callable[P, R]:
            """Decorator com validate_call - aceita str OU enum, converte auto.

            Business Rule: Uses Pydantic validate_call to automatically convert
            string values to StrEnum types and validate all parameters according
            to their type annotations. Preserves ParamSpec signature for correct
            type checking.

            Audit Implication: Zero boilerplate validation - parameters are
            automatically validated and converted at call time.
            """
            # P and R are imported from flext_core.typings (ParamSpec and TypeVar)
            # validate_call preserves the Callable[P, R] signature correctly
            return validate_call(
                config=ConfigDict(arbitrary_types_allowed=True, use_enum_values=False),
                validate_return=False,
            )(func)

        @staticmethod
        def validated_with_result(
            func: Callable[P, r[R]],
        ) -> Callable[P, r[R]]:
            """ValidationError → r.fail().

            Business Rule: Wraps validate_call to convert ValidationError exceptions
            into r.fail() responses. Preserves ParamSpec signature for
            correct type checking.

            Audit Implication: Railway-oriented error handling - validation errors
            become FlextResult failures instead of exceptions.
            """
            # P and R are imported from flext_core.typings (ParamSpec and TypeVar)
            validated_func = validate_call(
                config=ConfigDict(
                    arbitrary_types_allowed=True,
                    use_enum_values=False,
                ),
                validate_return=False,
            )(func)

            @wraps(func)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> r[R]:
                try:
                    return validated_func(*args, **kwargs)
                except Exception as e:
                    return r.fail(f"Validation failed: {e}")

            return wrapper

        @staticmethod
        def parse_kwargs[E: StrEnum](
            kwargs: Mapping[str, object],
            enum_fields: Mapping[str, type[E]],
        ) -> r[dict[str, object]]:
            """Parse kwargs converting specific fields to StrEnums.

            Business Rule: Accepts kwargs dictionary and enum_fields mapping,
            converting string values in specified fields to enum instances.
            Returns FlextResult with parsed dict or failure with list of invalid fields.

            Audit Implication: Type-safe kwargs parsing with selective enum conversion.
            """
            parsed, errors = dict(kwargs), []
            for field, enum_cls in enum_fields.items():
                if field in parsed:
                    field_value = parsed[field]
                    if isinstance(field_value, str):
                        try:
                            parsed[field] = enum_cls(field_value)
                        except ValueError:
                            errors.append(f"{field}: '{field_value}'")
            return r.fail(f"Invalid: {errors}") if errors else r.ok(parsed)

        @staticmethod
        def get_enum_params(func: Callable[..., object]) -> dict[str, type[StrEnum]]:
            """Extrai parâmetros StrEnum da signature.

            Business Rule: Extracts parameters from function signature that are
            StrEnum types. Returns empty dict if type hints cannot be retrieved.

            Audit Implication: Enables automatic enum parameter discovery for validation.
            """
            try:
                hints = get_type_hints(func)
            except Exception:
                return {}
            enum_params: dict[str, type[StrEnum]] = {}
            for n, h in hints.items():
                if n == "return":
                    continue
                if isinstance(h, type) and issubclass(h, StrEnum):
                    enum_params[n] = h
            return enum_params

    class Model:
        """from_dict, merge_defaults, update - ZERO try/except."""

        @staticmethod
        def from_dict[M: BaseModel](
            model_cls: type[M],
            data: Mapping[str, object],
            *,
            strict: bool = False,
        ) -> r[M]:
            """Create model instance from dictionary.

            Business Rule: Validates dictionary data against Pydantic model schema
            and returns r with model instance or validation error.

            Audit Implication: Type-safe model creation with railway-oriented error handling.
            """
            try:
                return r.ok(model_cls.model_validate(data, strict=strict))
            except Exception as e:
                return r.fail(f"Validation failed: {e}")

        @staticmethod
        def merge_defaults[M: BaseModel](
            model_cls: type[M],
            defaults: Mapping[str, object],
            overrides: Mapping[str, object],
        ) -> r[M]:
            """Merge defaults and overrides into model instance.

            Business Rule: Combines defaults and overrides dictionaries (overrides
            take precedence) and creates model instance using from_dict.

            Audit Implication: Type-safe model creation with default value merging.
            """
            return FlextApiUtilities.Model.from_dict(
                model_cls,
                {**defaults, **overrides},
            )

        @staticmethod
        def update[M: BaseModel](instance: M, **updates: object) -> r[M]:
            """Update model instance with new field values.

            Business Rule: Updates model instance by merging current values with
            updates dictionary and re-validating. Returns r with updated
            instance or validation error.

            Audit Implication: Type-safe model updates with validation.
            """
            try:
                current = instance.model_dump()
                current.update(updates)
                return r.ok(type(instance).model_validate(current))
            except Exception as e:
                return r.fail(f"Update failed: {e}")

    class Pydantic:
        """Fábricas de Annotated types."""

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
                BeforeValidator(FlextApiUtilities.Enum.coerce_validator(enum_cls)),
            ]

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
