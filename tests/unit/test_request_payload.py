"""Behavioral tests for the validated request boundary.

Exercises the PUBLIC contract of ``u.Api.RequestUtils.build_request_payload``:
it returns the validated HTTP request model, keeps raw ``bytes`` bodies, and
reports invalid method or URL input as a failed result.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from tests import c, tm, u


class TestsFlextApiRequestPayload:
    """Public-contract behavior of build_request_payload."""

    @staticmethod
    def test_bytes_body_reaches_the_validated_request() -> None:
        """A raw bytes body is preserved on the validated request."""
        body = b"raw-bytes"
        result = u.Api.RequestUtils.build_request_payload(
            method=c.Api.Method.POST,
            url="https://example.com/resources",
            data=body,
        )

        tm.ok(result.success)
        tm.that(result.value.body, eq=body)
        tm.that(str(result.value.method), eq=str(c.Api.Method.POST))

    @c.Tests.MARK.parametrize(
        ("method", "url"),
        [
            ("NOT A METHOD", "https://example.com/resources"),
            (c.Api.Method.GET, ""),
        ],
    )
    @staticmethod
    def test_invalid_request_input_fails(method: str, url: str) -> None:
        """Invalid method or URL input is a failed result, not an exception."""
        result = u.Api.RequestUtils.build_request_payload(method=method, url=url)

        tm.ok(result.failure)
        tm.that(result.error, none=False)
