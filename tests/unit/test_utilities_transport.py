"""Behavioral tests for the httpx transport owner exposed through ``u.Api``.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import (
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
)

import pytest

from tests import c, t, tm, u


class TestsFlextApiUtilitiesTransport:
    """Consumers construct, annotate, raise and catch httpx through the owner."""

    @staticmethod
    def test_client_constructs_and_closes_through_the_owner() -> None:
        """A real client constructs, narrows and closes.

        Construction routes through ``u.Api.HttpxClient``.
        """
        client: t.Api.HttpxClient = u.Api.HttpxClient(timeout=2.0)
        try:
            tm.ok(isinstance(client, u.Api.HttpxClient))
            tm.fail(client.is_closed)
        finally:
            client.close()
        tm.ok(client.is_closed)

    @pytest.mark.asyncio
    @staticmethod
    async def test_async_client_constructs_and_closes_through_the_owner() -> None:
        """A real async client opens and closes through ``u.Api.HttpxAsyncClient``."""
        async with u.Api.HttpxAsyncClient(timeout=2.0) as client:
            opened: t.Api.HttpxAsyncClient = client
            tm.fail(opened.is_closed)
        tm.ok(opened.is_closed)

    @staticmethod
    def test_status_error_is_raised_and_caught_through_the_owner() -> None:
        """A conflict response raises the owner status error and its base."""
        with u.Api.HttpxClient() as client:
            request = client.build_request("GET", "https://service.example/items")
        response: t.Api.HttpxResponse = u.Api.HttpxResponse(
            int(c.Web.StatusCode.CONFLICT),
            request=request,
        )
        with pytest.raises(u.Api.HttpxHTTPStatusError) as caught:
            response.raise_for_status()
        tm.ok(isinstance(caught.value, u.Api.HttpxHTTPError))
        tm.that(caught.value.response.status_code, eq=int(c.Web.StatusCode.CONFLICT))

    @staticmethod
    def test_request_error_is_caught_through_the_owner() -> None:
        """An unsupported scheme fails before I/O with the owner request error."""
        with (
            u.Api.HttpxClient() as client,
            pytest.raises(u.Api.HttpxRequestError) as caught,
        ):
            client.get("ftp://service.example/items")
        tm.ok(isinstance(caught.value, u.Api.HttpxHTTPError))
        tm.that(
            issubclass(u.Api.HttpxTimeoutException, u.Api.HttpxRequestError),
            eq=True,
        )
