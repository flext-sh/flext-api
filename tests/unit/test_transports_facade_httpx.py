"""The public HTTP class contracts own httpx construction and exception identity.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import httpx

from tests import tm, u


class TestsFlextApiHttpxContracts:
    """Observable construction and exception contracts of the HTTP owner."""

    @staticmethod
    def test_client_primitives_are_the_owner_types() -> None:
        """Client factories and response type are the httpx owner types."""
        tm.ok(u.Api.HttpxClient is httpx.Client)
        tm.ok(u.Api.HttpxAsyncClient is httpx.AsyncClient)
        tm.ok(u.Api.HttpxResponse is httpx.Response)

    @staticmethod
    def test_exception_primitives_are_the_owner_types() -> None:
        """Exception types match the httpx owner for consumer except clauses."""
        tm.ok(u.Api.HttpxHTTPError is httpx.HTTPError)
        tm.ok(u.Api.HttpxHTTPStatusError is httpx.HTTPStatusError)
        tm.ok(u.Api.HttpxRequestError is httpx.RequestError)
        tm.ok(u.Api.HttpxTimeoutException is httpx.TimeoutException)

    @staticmethod
    def test_client_constructs_through_the_public_contract() -> None:
        """A real client constructs and closes through the owner type."""
        client = u.Api.HttpxClient(timeout=2.0)
        try:
            tm.fail(client.is_closed)
        finally:
            client.close()
        tm.ok(client.is_closed)
