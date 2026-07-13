"""Behavioral tests for flext_api serialization utilities.

Exercises the PUBLIC contract of ``u.Api.packb`` / ``u.Api.unpackb`` only:
observable return values, the ``r[t.JsonValue]`` outcome of the fallible
``unpackb`` operation, round-trip idempotence, and error propagation. No
implementation internals are inspected.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest

from flext_api import t
from tests import u
from flext_tests import tm


class TestsFlextApiSerializers:
    """Public-contract behavior of packb/unpackb."""

    # ---- unpackb success --------------------------------------------------

    @pytest.mark.parametrize(
        ("packed", "expected"),
        [
            (b"\x81\xa3key\xa5value", {"key": "value"}),
            (b"\x93\x01\x02\x03", [1, 2, 3]),
            (b"\xa5hello", "hello"),
            (b"\x2a", 42),
            (b"\xc3", True),
            (b"\xc2", False),
            (b"\x90", []),
            (b"\x80", {}),
        ],
    )
    def test_unpackb_returns_success_carrying_decoded_value(
        self, packed: bytes, expected: t.JsonValue
    ) -> None:
        """Valid msgpack decodes to its JSON value inside a successful result."""
        result = u.Api.unpackb(packed)

        tm.that(result.success, eq=True)
        tm.that(result.failure, eq=False)
        tm.that(result.value, eq=expected)
        tm.that(result.error, none=True)

    def test_unpackb_success_unwraps_to_value(self) -> None:
        """unwrap() on a success yields the decoded value directly."""
        result = u.Api.unpackb(b"\x81\xa3key\xa5value")

        tm.that(result.unwrap(), eq={"key": "value"})

    def test_unpackb_success_supports_map_combinator(self) -> None:
        """A successful result composes through map() over its value."""
        result = u.Api.unpackb(b"\x2a").map(lambda value: [value])

        tm.that(result.success, eq=True)
        tm.that(result.value, eq=[42])

    def test_unpackb_success_supports_flat_map_combinator(self) -> None:
        """A successful result chains a further fallible step via flat_map()."""
        result = u.Api.unpackb(b"\x2a").flat_map(
            lambda value: u.Api.unpackb(u.Api.packb(value))
        )

        tm.that(result.success, eq=True)
        tm.that(result.value, eq=42)

    def test_unpackb_nil_is_success_without_accessible_payload(self) -> None:
        """Msgpack nil decodes to a success, but the None payload is guarded.

        The result contract forbids a None success payload, so any payload
        access raises ValueError even though the operation itself succeeded.
        """
        result = u.Api.unpackb(b"\xc0")

        tm.that(result.success, eq=True)
        tm.that(result.error, none=True)
        with pytest.raises(ValueError, match="non-None payload"):
            _ = result.value

    # ---- unpackb failure --------------------------------------------------

    @pytest.mark.parametrize(
        "invalid",
        [
            b"\xff\xff\xff\xff",  # trailing extra data
            b"\xc1",  # msgpack "never used" opcode
            b"\x81",  # truncated map header
            b"",  # empty payload
        ],
    )
    def test_unpackb_returns_failure_for_undecodable_bytes(
        self, invalid: bytes
    ) -> None:
        """Undecodable bytes produce a failure result, never a raised error."""
        result = u.Api.unpackb(invalid)

        sentinel = "<<unreachable>>"
        tm.that(result.failure, eq=True)
        tm.that(result.success, eq=False)
        tm.that(result.unwrap_or(sentinel), eq=sentinel)

    def test_unpackb_failure_reports_deserialization_error(self) -> None:
        """The failure error message names the deserialization operation."""
        result = u.Api.unpackb(b"\xff\xff\xff\xff")

        tm.that(result.error, none=False)
        tm.that(result.error, has="msgpack deserialization")

    def test_unpackb_failure_recovers_via_recover(self) -> None:
        """A failed result recovers through recover() to a caller-supplied value."""
        recovered = u.Api.unpackb(b"\xff\xff\xff\xff").recover(
            lambda _error: "fallback"
        )

        tm.that(recovered.success, eq=True)
        tm.that(recovered.value, eq="fallback")

    # ---- round trip / invariants -----------------------------------------

    @pytest.mark.parametrize(
        "payload",
        [
            {"key": "value"},
            {"nested": {"a": [1, 2, {"b": True}]}},
            [1, 2, 3],
            [],
            {},
            "hello",
            42,
            True,
        ],
    )
    def test_packb_then_unpackb_is_identity(self, payload: t.JsonValue) -> None:
        """unpackb(packb(x)) reproduces the original JSON value."""
        result = u.Api.unpackb(u.Api.packb(payload))

        tm.that(result.success, eq=True)
        tm.that(result.value, eq=payload)

    def test_packb_returns_bytes(self) -> None:
        """Packb produces a bytes payload consumable by unpackb."""
        packed = u.Api.packb({"key": "value"})

        tm.that(packed, is_=bytes)

    def test_unpackb_is_deterministic(self) -> None:
        """Decoding the same bytes twice yields equal values."""
        packed = u.Api.packb([1, 2, 3])

        first = u.Api.unpackb(packed)
        second = u.Api.unpackb(packed)

        tm.that(first.value, eq=second.value)
