"""Minimal tests for client status and response helpers."""

from __future__ import annotations

import pytest

from flext_api import (
    FlextApiClient,
    FlextApiModels,
)


def test_client_status_transitions() -> None:
    """Client starts in IDLE status consistently across implementations."""
    client = FlextApiClient(base_url="https://example.com")
    status_str = str(client.status)
    assert status_str in {"FlextApiClientStatus.IDLE", "idle"}


@pytest.mark.asyncio
async def test_response_helpers() -> None:
    """Response helpers should indicate success and render JSON/text."""
    resp = FlextApiModels.ApiResponse(id="test_resp", status_code=200, data={"a": 1})
    assert resp.is_success() is True
    assert resp.is_error() is False
    assert resp.json() == {"a": 1}
    assert isinstance(resp.text(), str)
