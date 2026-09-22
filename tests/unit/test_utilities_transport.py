"""Behavioral tests for the httpx transport owner exposed through ``u.Api.Httpx``.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest
from flext_tests import tm

from flext_api import c, t, u


class TestsFlextApiUtilitiesTransport:
    """Consumers construct, annotate, raise and catch httpx through the owner."""

    def test_client_constructs_and_closes_through_the_owner(self) -> None:
        """A real client constructs, narrows and closes through ``u.Api.Httpx``."""
        client: t.Api.Httpx.Client = u.Api.Httpx.Client(timeout=2.0)
        try:
            tm.that(isinstance(client, u.Api.Httpx.Client), eq=True)
            tm.that(client.is_closed, eq=False)
        finally:
            client.close()
        tm.that(client.is_closed, eq=True)

    @pytest.mark.asyncio
    async def test_async_client_constructs_and_closes_through_the_owner(self) -> None:
        """A real async client opens and closes through ``u.Api.Httpx``."""
        async with u.Api.Httpx.AsyncClient(timeout=2.0) as client:
            opened: t.Api.Httpx.AsyncClient = client
            tm.that(opened.is_closed, eq=False)
        tm.that(opened.is_closed, eq=True)

    def test_status_error_is_raised_and_caught_through_the_owner(self) -> None:
        """A conflict response raises the owner status error and its base."""
        with u.Api.Httpx.Client() as client:
            request = client.build_request("GET", "https://service.example/items")
        response: t.Api.Httpx.Response = u.Api.Httpx.Response(
            int(c.Web.StatusCode.CONFLICT), request=request
        )
        with pytest.raises(u.Api.Httpx.HTTPStatusError) as caught:
            response.raise_for_status()
        tm.that(isinstance(caught.value, u.Api.Httpx.HTTPError), eq=True)
        tm.that(caught.value.response.status_code, eq=int(c.Web.StatusCode.CONFLICT))

    def test_request_error_is_caught_through_the_owner(self) -> None:
        """An unsupported scheme fails before I/O with the owner request error."""
        with (
            u.Api.Httpx.Client() as client,
            pytest.raises(u.Api.Httpx.RequestError) as caught,
        ):
            client.get("ftp://service.example/items")
        tm.that(isinstance(caught.value, u.Api.Httpx.HTTPError), eq=True)
        tm.that(
            issubclass(u.Api.Httpx.TimeoutException, u.Api.Httpx.RequestError), eq=True
        )


__all__: list[str] = ["TestsFlextApiUtilitiesTransport"]
