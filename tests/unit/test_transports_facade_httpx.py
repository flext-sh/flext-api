"""The public HTTP class contracts own httpx construction and exception identity.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import httpx

from flext_api import (
    HttpxAsyncClient,
    HttpxClient,
    HttpxHTTPError,
    HttpxHTTPStatusError,
    HttpxRequestError,
    HttpxResponse,
    HttpxTimeoutException,
)
from tests import p, tm


class TestsFlextApiHttpxContracts:
    """Observable construction and exception contracts of the HTTP owner."""

    @staticmethod
    def test_client_primitives_are_the_owner_types() -> None:
        """Client factories and response type are the httpx owner types."""
        tm.ok(HttpxClient is httpx.Client)
        tm.ok(HttpxAsyncClient is httpx.AsyncClient)
        tm.ok(HttpxResponse is httpx.Response)

    @staticmethod
    def test_exception_primitives_are_the_owner_types() -> None:
        """Exception types match the httpx owner for consumer except clauses."""
        tm.ok(HttpxHTTPError is httpx.HTTPError)
        tm.ok(HttpxHTTPStatusError is httpx.HTTPStatusError)
        tm.ok(HttpxRequestError is httpx.RequestError)
        tm.ok(HttpxTimeoutException is httpx.TimeoutException)

    @staticmethod
    def test_conflict_status_is_derived_from_the_owner() -> None:
        """The conflict constant stays int-typed and equals the httpx owner."""
        conflict = p.Api.Httpx.CONFLICT
        tm.that(type(conflict), eq=int)
        tm.that(conflict, eq=int(httpx.codes.CONFLICT))

    @staticmethod
    def test_client_constructs_through_the_public_contract() -> None:
        """A real client constructs and closes through the owner type."""
        client = HttpxClient(timeout=2.0)
        try:
            tm.fail(client.is_closed)
        finally:
            client.close()
        tm.ok(client.is_closed)
