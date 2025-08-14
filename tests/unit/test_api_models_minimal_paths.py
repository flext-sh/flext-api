"""Minimal path tests for API models request/response helpers."""

from __future__ import annotations

from flext_api.api_models import ApiRequest, ApiResponse, HttpMethod


def test_response_model_basic() -> None:
    """Response model should mark 200 as success."""
    r = ApiResponse(id="resp1", status_code=200)
    assert r.is_success() is True


def test_request_model_basic() -> None:
    """Request model basic validation should pass."""
    req = ApiRequest(id="req1", method=HttpMethod.GET, url="https://x/y")
    assert req.validate_business_rules().success
