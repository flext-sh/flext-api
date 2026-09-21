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
from flext_tests import tm

from flext_api import t, u


class TestsFlextApiSerializers:
    """Public-contract behavior of packb/unpackb."""

    @pytest.mark.parametrize(
        ("packed", "expected"),
        [
            (b"\x81\xa3key\xa5value", {"key": "value"}),
            (b"\x93\x01\x02\x03", [1, 2, 3]),
            (b"\x2a", 42),
            (b"\xff", -1),
        ],
    )
    def test_unpackb_valid_input_succeeds(
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
        result = u.Api.unpackb(b"\x81\xa3key\xa5value").map(lambda value: [value])

        tm.that(result.success, eq=True)
        tm.that(result.value, eq=[{"key": "value"}])

    def test_unpackb_success_supports_flat_map_combinator(self) -> None:
        """A successful result chains a further fallible step via flat_map()."""
        result = u.Api.unpackb(b"\x2a").flat_map(
            lambda value: u.Api.unpackb(u.Api.packb(value))
        )

        tm.that(result.success, eq=True)
        tm.that(result.value, eq=42)

    @pytest.mark.parametrize("packed", [b"\xd9", b"\xc1"])
    def test_unpackb_invalid_input_fails(self, packed: bytes) -> None:
        """Incomplete or reserved MessagePack input yields a failure."""
        result = u.Api.unpackb(packed)

        tm.that(result.success, eq=False)
        tm.that(result.failure, eq=True)
        tm.that(result.error, is_=str, empty=False)

    def test_packb_unpackb_roundtrip(self) -> None:
        """packb() followed by unpackb() yields the original value."""
        original: t.JsonValue = {"key": "value", "list": [1, 2, 3]}
        packed = u.Api.packb(original)
        result = u.Api.unpackb(packed)

        tm.that(result.success, eq=True)
        tm.that(result.value, eq=original)

    def test_packb_valid_input_succeeds(self) -> None:
        """Valid JSON values pack successfully."""
        packed = u.Api.packb({"key": "value"})

        tm.that(packed, eq=b"\x81\xa3key\xa5value")

    def test_packb_unpackb_roundtrip_list(self) -> None:
        """Round-trip for lists."""
        original: t.JsonValue = [1, 2, 3]
        packed = u.Api.packb(original)
        result = u.Api.unpackb(packed)

        tm.that(result.success, eq=True)
        tm.that(result.value, eq=original)

    def test_packb_unpackb_roundtrip_str(self) -> None:
        """Round-trip for strings."""
        original: t.JsonValue = "hello world"
        packed = u.Api.packb(original)
        result = u.Api.unpackb(packed)

        tm.that(result.success, eq=True)
        tm.that(result.value, eq=original)

    def test_packb_unpackb_roundtrip_bool(self) -> None:
        """Round-trip for booleans."""
        original: t.JsonValue = True
        packed = u.Api.packb(original)
        result = u.Api.unpackb(packed)

        tm.that(result.success, eq=True)
        tm.that(result.value, eq=original)

    def test_unpackb_rejects_nil_payload(self) -> None:
        """An encoded msgpack nil fails because Result cannot succeed with None."""
        packed = u.Api.packb(None)
        result = u.Api.unpackb(packed)

        tm.that(result.success, eq=False)
        tm.that(result.failure, eq=True)
        tm.that(str(result.error), has="Result cannot carry None")

    def test_packb_none_encodes_nil(self) -> None:
        """Packing None produces the MessagePack nil marker."""
        tm.that(u.Api.packb(None), eq=b"\xc0")

    def test_packb_unpackb_roundtrip_nested_none(self) -> None:
        """Null values inside a collection survive a round-trip."""
        original: t.JsonValue = {"nullable": None, "items": [None, "value"]}
        result = u.Api.unpackb(u.Api.packb(original))

        tm.that(result.success, eq=True)
        tm.that(result.value, eq=original)


__all__: list[str] = ["TestsFlextApiSerializers"]
